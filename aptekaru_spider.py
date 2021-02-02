import time
import scrapy
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from scrapy.selector import Selector
from collections import OrderedDict
from urllib.parse import urlparse
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
firefox_binary = FirefoxBinary("./firefox/firefox")


firefox_options = Options()
firefox_options.add_argument('--headless')
firefox_options.add_argument("--disable-notifications")
firefox_options.add_argument("--incognito")
firefox_options.add_argument("--disable-extensions")
firefox_options.add_argument(" --disable-gpu")
firefox_options.add_argument(" --disable-infobars")
firefox_options.add_argument(" -–disable-web-security")
firefox_options.add_argument("--no-sandbox")
firefox_options.add_argument('--no-default-browser-check')
firefox_options.add_argument('--no-first-run')
firefox_options.add_argument('--disable-default-apps')


class AptekaruSpider(scrapy.Spider):
    name = 'aptekaru'
    start_url = 'https://apteka.ru'
    start_urls = ['https://www.google.com/']

    category_api = 'https://api.apteka.ru/Search/CategoryUrl'

    custom_settings = {
        # 'CRAWLERA_APIKEY': 'CRAWLERA_APIKEY',
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        # 'REFERRER_POLICY': 'no-referrer-when-downgrade',
    }

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

    def parse_category(self, response):
        # print('AAAAAAA:', response.extract())
        print('BBBBBBB:', response.css('.CatalogItemsList__grid .CategoryItemCard .CategoryItemCard__title'))


    def get_selenium_page(self, url):
        with webdriver.Firefox(
            firefox_binary=firefox_binary,
            executable_path='./geckodriver',
            options=firefox_options
        ) as driver:
            driver.get(url)
            time.sleep(10)
            while True:
                if driver.execute_script("return document.readyState") == 'complete':
                    break
            return Selector(text=driver.page_source)

    def parse(self, response):
        # main_page = self.get_selenium_page(self.start_url)
        # print(main_page.css('.CatalogueOverlay__list a'))
        for next_category in response.css('.CatalogueOverlay__list li a'):
            category_slug = next_category.css('::attr(href)').extract_first()
            next_url = f'{self.start_url}{category_slug}'
            # category_slug = 
            #     page	"18"
            #     iPharmTownId	""
            #     withPrice	"false"
            #     withProfit	"false"
            #     withPromoVits	"false"
            #     apiUrl	"/Search/CategoryUrl"
            #     categoryUrl	"mouth/toothpaste"
            #     cityId	"5e57803249af4c0001d64407"
            # yield self.parse_category(self.get_selenium_page(next_url))
            # next_product_link = next_product.css('.product__information>a')
            yield response.follow(next_url, self.parse_product)

        # for next_page in response.css('a.next'):
        #     yield response.follow(next_page, self.parse)


    def start_requests(self):
        # yield self.parse(self.get_selenium_page(self.start_url))
        yield scrapy.http.Request(self.start_url, callback=self.parse)