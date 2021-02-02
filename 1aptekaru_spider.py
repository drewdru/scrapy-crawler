import time
import scrapy
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException


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
    base_url = 'https://apteka.ru'
    start_urls = ['https://www.google.com/']

    REGION_SLUG_MOSCOW = 'moscow'
    REGIONS = {
        'moscow': '5e58a675cd37fa0001a7cb79'
    }

    custom_settings = {
        # 'CRAWLERA_APIKEY': 'CRAWLERA_APIKEY',
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        # 'REFERRER_POLICY': 'no-referrer-when-downgrade',
    }

    def __init__(self, region_slug=None, *args, **kwargs):
        super(AptekaruSpider, self).__init__(*args, **kwargs)
        self.region_slug = region_slug if region_slug else self.REGION_SLUG_MOSCOW


    def get_selenium_page(self, url):
        try:
            with webdriver.Firefox(
                firefox_binary=firefox_binary,
                executable_path='./geckodriver',
                options=firefox_options
            ) as driver:
                driver.get(url)
                driver.add_cookie({"name": "selectedTown", "value": self.REGIONS['moscow']})
                driver.add_cookie({"name": "region_selected", "value": 'yes'})
                time.sleep(1)
                while True:
                    if driver.execute_script("return document.readyState") == 'complete':
                        break
                return Selector(text=driver.page_source)
        except (TimeoutException, Exception):
            return False


    def parse_product(self, url, response):
        source = url
        parsed_url = urlparse(source)
        
        breadcrumbs = response.css('.ProductPage__crumbs')
        product_name = response.css('.ProductPage__title h1::text').extract_first()
        product_id = breadcrumbs.css('li[itemprop="itemListElement"] span[itemprop="item"]::attr(itemid)').extract()[-1]
        product_id = product_id.replace('/product/', '').replace('/', '')
        product_id = product_id.split('-')[-1]
        slug = source.replace('https://apteka.ru/product/', '').replace(f'-{product_id}/', '')
        categories = breadcrumbs.css('li[itemprop="itemListElement"] meta[itemprop="name"]::attr(content)').extract()
        if len(categories):
            categories = categories[1:-1]
        price = response.css('.ProductPage__price::text').extract_first()
        price_not_empty = 1 if price and price.strip(' .,0') else 0
        old_price = response.css('.ProductPage__old-price::text').extract_first()
        availability = response.css('.ProductPage__PurchaseButton::attr(data-basket-status)').extract_first()
        in_stock = 1 if availability == 'available' else 0

        brand_name = response.css('.ProductPage__info-block meta[itemprop="brand"]::attr(content)').extract_first()

        country = ''
        for info in response.css('.ProdDescList'):
            info_name = info.css('h3::text').extract_first()
            if info_name != 'Характеристики':
                continue
            for row in info.css('dl div'):
                row_name = info.css('dt::text').extract_first()
                if row_name != 'Страна производителя':
                    continue
                country = info.css('dd::text').extract_first().strip()
                break

        yield OrderedDict([
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
            ('price_not_empty', price_not_empty),
            # ('region_slug', self.region_slug),
        ])

    def parse_category(self, response):
        for next_product in response.css('.CatalogItemsList__grid .CategoryItemCard .CategoryItemCard__title'):
            next_url = next_product.css('::attr(href)').extract_first()
            next_url = f'{self.base_url}{next_url}'
            selector = self.get_selenium_page(next_url)
            if not selector:
                continue
            for data in self.parse_product(next_url, selector):
                yield data

        for next_page in response.css('.pager-v3-next'):
            next_url = next_product.css('::attr(href)').extract_first()
            next_url = f'{self.base_url}{next_url}'
            selector = self.get_selenium_page(next_url)
            if not selector:
                continue
            for data in self.parse_category(selector):
                yield data

    def parse(self, response):
        main_page = self.get_selenium_page(self.base_url)
        if not main_page:
            yield {}

        for next_category in main_page.css('.CatalogueOverlay__list li a'):
            next_url = next_category.css('::attr(href)').extract_first()
            next_url = f'{self.base_url}{next_url}'
            selector = self.get_selenium_page(next_url)
            if not selector:
                continue
            for data in self.parse_category(selector):
                yield data
