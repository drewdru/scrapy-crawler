import os
import logging
import requests


import json
import xlrd

import datetime

import scrapy

from datetime import date
from collections import OrderedDict

from scrapy import Spider
from scrapy.spiders import CrawlSpider
from scrapy.utils.project import get_project_settings
from scrapy.selector import Selector

# from crawling.models import License, WorkAddress, Work
from zipfile import ZipFile

scrapy_settings = get_project_settings()

logger = logging.getLogger(__name__)


class RoszdravnadzorOpendataParser():
    xml_file_path = './roszdravnadzor/roszdravnadzor.zip'
    url = 'https://roszdravnadzor.gov.ru/opendata/7710537160-ls_licenses/data-20210126-structure-20200906.zip'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    }

    @classmethod    
    def convert_date(cls, date):
        if date is None:
            return None
        date = datetime.datetime.strptime(date, '%d.%m.%Y')
        return datetime.date.strftime(date, "%Y-%m-%d")

    @classmethod
    def get_xml_data(cls, response):
        dirname = os.path.dirname(cls.xml_file_path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
            with open(cls.xml_file_path, mode='a'): pass
        with open(cls.xml_file_path, "wb") as f:
            f.write(response.content)
        with ZipFile(cls.xml_file_path, 'r') as zipObj:
            if not len(zipObj.infolist()):
                return Selector()
            text_data = zipObj.read(zipObj.infolist()[0])
            return Selector(text=text_data)

    @classmethod
    def run(cls):
        data = requests.get(cls.url, headers=cls.headers)
        licenses = cls.get_xml_data(data)
        for license_data in licenses.css('licenses_list licenses').extract():
            license_selector = Selector(text=license_data)

            name = license_selector.css('name::text').extract_first()
            activity_type = license_selector.css('activity_type::text').extract_first()
            full_name_licensee = license_selector.css('full_name_licensee::text').extract_first()
            abbreviated_name_licensee = license_selector.css('abbreviated_name_licensee::text').extract_first()
            brand_name_licensee = license_selector.css('brand_name_licensee::text').extract_first()
            form = license_selector.css('form::text').extract_first()
            address = license_selector.css('address::text').extract_first()
            ogrn = license_selector.css('ogrn::text').extract_first()
            inn = license_selector.css('inn::text').extract_first()
            number = license_selector.css('number::text').extract_first()
            date = license_selector.css('date::text').extract_first()
            number_orders = license_selector.css('number_orders::text').extract_first()
            date_order = license_selector.css('date_order::text').extract_first()
            date_register = license_selector.css('date_register::text').extract_first()
            number_duplicate = license_selector.css('number_duplicate::text').extract_first()
            date_duplicate = license_selector.css('date_duplicate::text').extract_first()
            termination = license_selector.css('termination::text').extract_first()
            date_termination = license_selector.css('date_termination::text').extract_first()
            information = license_selector.css('information::text').extract_first()
            information_regulations = license_selector.css('information_regulations::text').extract_first()
            information_suspension_resumption = license_selector.css('information_suspension_resumption::text').extract_first()
            information_cancellation = license_selector.css('information_cancellation::text').extract_first()
            information_reissuing = license_selector.css('information_reissuing::text').extract_first()

            work_address_list = []
            for work_address_data in license_selector.css('work_address_list address_place').extract():
                work_address = Selector(text=work_address_data)

                address = work_address.css('address::text').extract_first()
                index = work_address.css('index::text').extract_first()
                region = work_address.css('region::text').extract_first()
                city = work_address.css('city::text').extract_first()
                street = work_address.css('street::text').extract_first()
                code_fias = work_address.css('code_fias::text').extract_first()

                works_list = []
                for work in work_address.css('works work::text').extract():
                    works_list.append(work)

                work_address_list.append({
                    'address': address,
                    'index': index,
                    'region': region,
                    'city': city,
                    'street': street,
                    'code_fias': code_fias,
                    'works': works_list,
                })
            print(OrderedDict([
                ('name', name),
                ('activity_type', activity_type),
                ('full_name_licensee', full_name_licensee),
                ('abbreviated_name_licensee', abbreviated_name_licensee),
                ('brand_name_licensee', brand_name_licensee),
                ('form', form),
                ('address', address),
                ('ogrn', ogrn),
                ('inn', inn),
                ('number', number),
                ('date', date),
                ('number_orders', number_orders),
                ('date_order', date_order),
                ('date_register', date_register),
                ('number_duplicate', number_duplicate),
                ('date_duplicate', date_duplicate),
                ('termination', termination),
                ('date_termination', date_termination),
                ('information', information),
                ('information_regulations', information_regulations),
                ('information_suspension_resumption', information_suspension_resumption),
                ('information_cancellation', information_cancellation),
                ('information_reissuing', information_reissuing),
                ('work_address_list', work_address_list),
            ]))

RoszdravnadzorOpendataParser.run()