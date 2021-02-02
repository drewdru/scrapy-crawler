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


class EaptekaSpider(scrapy.Spider):
    name = 'eaptekaspider'
    base_url = 'https://www.eapteka.ru'
    start_urls = ['https://www.google.com/']
    categories_url = 'https://www.eapteka.ru/goods/'

    def get_selenium_page(self, url):
        with webdriver.Firefox(
            firefox_binary=firefox_binary,
            executable_path='./geckodriver',
            options=firefox_options
        ) as driver:
            driver.get(url)
            return Selector(text=driver.page_source)

    def parse(self, response):
        categories_page = self.get_selenium_page(self.categories_url)
        for next_category in categories_page.css('a.more::attr(href)'):
            category = next_category.get()
            if 'meta' in category:
                continue
            category_url = f'{self.base_url}{category}'
            categories_page = self.get_selenium_page(category_url)
            page_count = int(categories_page.css(
                '#section_nav_top>ul>li:last-child>a::text'
            ).extract_first())

            for product in self.parse_product_list(
                category_url, categories_page, 1, page_count, category
            ):
                yield product

    def parse_product_list(self, page_url, page, page_num, page_count, category):
        for next_product in page.css('a.cc-item--title::attr(href)'):
            product = next_product.get()
            product_url = f'{self.base_url}{product}'
            product_page = self.get_selenium_page(product_url)
            for product_data in self.parse_product(product_url, product_page):
                yield product_data

        if page_num < page_count:
            page_num += 1
            pagination_url = f'{self.base_url}{category}?PAGEN_1={page_num}'
            categories_page = self.get_selenium_page(pagination_url)
            for product in self.parse_product_list(
                pagination_url, categories_page, page_num, page_count, category
            ):
                yield product
    
    def parse_product(self, page_url, page):
        lastmod = ''
        source = page_url
        id = page_url.split('id')[-1].replace('/', '') if 'id' in page_url else ''
        slug = breadcrumbs.css(
            'ul.clearfix>li:last-child>a::attr(href)'
        ).extract_first()[:-1].split('/')[-1]
        product_name = page.css('.sec-item>h1::text').extract_first()
        product_id = page.css('#bitem::attr(data-product-id)').extract_first()
        brand_name = ''

        breadcrumbs = page.css('.breadcrumbs')
        categories = breadcrumbs.css('ul.clearfix>li>a::text').extract()[1:-1]
        categories = list(map(str.strip, categories))
        availability = page.css(
            '#bitem>link[itemprop="availability"]::attr(href)'
        ).extract_first()
        in_stock = 1 if 'InStock' in availability else 0
        old_price = page.css(
            '.offer-tools__old-price::text'
        ).extract_first().strip().replace(u'\xa0', u' ').split(' ')[0]
        price = page.css(
            '.offer-tools__price_num-strong::text'
        ).extract_first().strip()
        

        country = ''
        for info in page.css('.description__item>p'):
            info_param = info.css('::text').extract_first()
            if 'Производитель' in info_param:
                brand_info = info.css('a::text').extract_first().split(',')
                brand_name = brand_info[0]
                country = brand_info[-1]
                break

        yield OrderedDict([
            ('id', id),
            ('slug', slug),
            ('name', product_name),
            ('country', country),
            ('brand', brand_name),
            ('categories', '||'.join(categories)),
            ('old_price', old_price),
            ('price', price),
            ('source', source),
            ('in_stock', in_stock),
            ('product_id', product_id),
            ('lastmod', ''),
            # ('price_not_empty', price_not_empty),
            # ('region_slug', self.region_slug),
        ])