import scrapy
import re
from collections import OrderedDict
from urllib.parse import urlparse

class AsnaSpider(scrapy.Spider):
    name = 'asnaspider'
    start_urls = ['https://www.asna.ru/catalog/']

    def parse_product(self, response):
        lastmod = response.meta.get('lastmod')
        source = response.url
        parsed_url = urlparse(source)
        slug = parsed_url.path.replace('/cards/', '').replace('.html', '')
        product_name = response.css('.product-title>h1::text').extract_first()
        product_id = response.css('.leftcol-catalog-item>div[data-product-id]::attr(data-product-id)').extract_first()
        brand_name = ''
        breadcrumbs = response.css('.breadcrumbs')
        categories = breadcrumbs.css('li[itemprop="itemListElement"] span[itemprop="name"]::text').extract()[2:-1]
        availability = response.css('.farm-contains-wrapp'). \
                        xpath('.//meta[@itemprop="availability"]/@content').extract_first()
        in_stock = 0 if availability == 'out_of_stock' else 1

        price_input = response.css('.item-component-price-wapper>input')
        
        offer_id = price_input.css('::attr(data-offer-id)').extract_first()
        min_base_price = price_input.css('::attr(data-min-base-price)').extract_first()
        base_price = price_input.css('::attr(data-base-price)').extract_first()
        price = price_input.css('::attr(data-show-price)').extract_first()
        

        country = ''
        for info in response.css('.nomobile>ul.infos>li'):
            info_param = info.css('.param::text').extract_first()
            if 'Производитель' in info_param:
                brand_name = info.css('.param-text::text').extract_first().strip()
            if 'Завод-производитель' in info_param:
                country = info.css('.param-text::text').extract_first().strip()
        if country:
            try:
                country = country.split('(', 1)[1].split(')')[0]
            except IndexError:
                country = ''

        yield OrderedDict([
            ('id', offer_id),
            ('slug', slug),
            ('name', product_name),
            ('country', country),
            ('brand', brand_name),
            ('categories', '||'.join(categories)),
            ('base_price', base_price), # базовая цена
            ('min_base_price', min_base_price), # минимальная базовая цена
            ('discount_price', price), # минимальная цена со скидкой при заказе свыше 3000р
            ('source', source),
            ('in_stock', in_stock),
            ('product_id', product_id),
            ('lastmod', lastmod),
            # ('price_not_empty', price_not_empty),
            # ('region_slug', self.region_slug),
        ])

    def parse(self, response):
        for next_product in response.css('.product__information>a'):
            # next_product_link = next_product.css('.product__information>a')
            yield response.follow(next_product, self.parse_product)

        for next_page in response.css('a.next'):
            yield response.follow(next_page, self.parse)

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.http.Request(url, cookies={'my_auto_region_id':'46'}, callback=self.parse)