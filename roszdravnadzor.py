
import json
import scrapy
import xlrd
import time

from collections import OrderedDict

from scrapy.http import FormRequest

from roszdravnadzor_pipelines import RoszdravnadzorPipeline


REQUEST_TABLE_DATA = {
    'columns[0][data]': 'col1.label',
    'columns[0][name]': '',
    'columns[0][searchable]': 'true',
    'columns[0][orderable]': 'false',
    'columns[0][search][value]': '',
    'columns[0][search][regex]': 'false',
    'columns[1][data]': 'col2.label',
    'columns[1][name]': '',
    'columns[1][searchable]': 'true',
    'columns[1][orderable]': 'false',
    'columns[1][search][value]': '',
    'columns[1][search][regex]': 'false',
    'columns[2][data]': 'col3.label',
    'columns[2][name]': '',
    'columns[2][searchable]': 'true',
    'columns[2][orderable]': 'false',
    'columns[2][search][value]': '',
    'columns[2][search][regex]': 'false',
    'columns[3][data]': 'col4.label',
    'columns[3][name]': '',
    'columns[3][searchable]': 'true',
    'columns[3][orderable]': 'false',
    'columns[3][search][value]': '',
    'columns[3][search][regex]': 'false',
    'columns[4][data]': 'col5.label',
    'columns[4][name]': '',
    'columns[4][searchable]': 'true',
    'columns[4][orderable]': 'false',
    'columns[4][search][value]': '',
    'columns[4][search][regex]': 'false',
    'columns[5][data]': 'col6.label',
    'columns[5][name]': '',
    'columns[5][searchable]': 'true',
    'columns[5][orderable]': 'false',
    'columns[5][search][value]': '',
    'columns[5][search][regex]': 'false',
    'columns[6][data]': 'col7.label',
    'columns[6][name]': '',
    'columns[6][searchable]': 'true',
    'columns[6][orderable]': 'false',
    'columns[6][search][value]': '',
    'columns[6][search][regex]': 'false',
    'columns[7][data]': 'col8.label',
    'columns[7][name]': '',
    'columns[7][searchable]': 'true',
    'columns[7][orderable]': 'false',
    'columns[7][search][value]': '',
    'columns[7][search][regex]': 'false',
    'columns[8][data]': 'col9.label',
    'columns[8][name]': '',
    'columns[8][searchable]': 'true',
    'columns[8][orderable]': 'false',
    'columns[8][search][value]': '',
    'columns[8][search][regex]': 'false',
    'columns[9][data]': 'col10.label',
    'columns[9][name]': '',
    'columns[9][searchable]': 'true',
    'columns[9][orderable]': 'false',
    'columns[9][search][value]': '',
    'columns[9][search][regex]': 'false',
    'columns[10][data]': 'col11.label',
    'columns[10][name]': '',
    'columns[10][searchable]': 'true',
    'columns[10][orderable]': 'false',
    'columns[10][search][value]': '',
    'columns[10][search][regex]': 'false',
    'columns[11][data]': 'col12.label',
    'columns[11][name]': '',
    'columns[11][searchable]': 'true',
    'columns[11][orderable]': 'false',
    'columns[11][search][value]': '',
    'columns[11][search][regex]': 'false',
    'columns[12][data]': 'col13.label',
    'columns[12][name]': '',
    'columns[12][searchable]': 'true',
    'columns[12][orderable]': 'false',
    'columns[12][search][value]': '',
    'columns[12][search][regex]': 'false',
    'columns[13][data]': 'col14.label',
    'columns[13][name]': '',
    'columns[13][searchable]': 'true',
    'columns[13][orderable]': 'false',
    'columns[13][search][value]': '',
    'columns[13][search][regex]': 'false',
    'columns[14][data]': 'col15.label',
    'columns[14][name]': '',
    'columns[14][searchable]': 'true',
    'columns[14][orderable]': 'false',
    'columns[14][search][value]': '',
    'columns[14][search][regex]': 'false',
    'columns[15][data]': 'col16.label',
    'columns[15][name]': '',
    'columns[15][searchable]': 'true',
    'columns[15][orderable]': 'false',
    'columns[15][search][value]': '',
    'columns[15][search][regex]': 'false',
    'columns[16][data]': 'col17.label',
    'columns[16][name]': '',
    'columns[16][searchable]': 'true',
    'columns[16][orderable]': 'false',
    'columns[16][search][value]': '',
    'columns[16][search][regex]': 'false',
    'columns[17][data]': 'col18.label',
    'columns[17][name]': '',
    'columns[17][searchable]': 'true',
    'columns[17][orderable]': 'false',
    'columns[17][search][value]': '',
    'columns[17][search][regex]': 'false',
    'search[value]': '',
    'search[regex]': 'false',
    'q_org_ogrn': '',
    'q_org_inn': '',
    'q_type': '1',
    'q_org_label': '',
    'q_active': '0',
    'q_region': '',
    'dt_from': '',
    'dt_to': '',
    'q_activity': ''
}

COLUMN_NAMES = {
    'col1': 'number',
    'col2': 'date',
    'col3': 'full_name_licensee',
    'col4': 'brand_name_licensee',
    'col5': 'address',
    'col6': 'ogrn',
    'col7': 'inn',
    'col8': 'okpo',
    'col9': 'number_orders',
    'col10': 'date_order',
    'col11': 'date_register',
    'col12': 'date_termination',    
    'col13': 'information_reissuing',
    'col14': 'information_suspension_resumption',
    'col15': 'information_regulations',
    'col16': 'information_cancellation',
    'col17': 'termination',
    'col18': 'information',
}

class RoszdravnadzorSpider(scrapy.Spider):
    name = 'roszdravnadzor'
    start_url = 'https://www.roszdravnadzor.ru/ajax/services/licenses'
    xls_file = './companies.xlsx'
    inn_col_index = 4
    address_col_index = 6
    length = 50

    custom_settings = {
        # 'CRAWLERA_APIKEY': 'CRAWLERA_APIKEY',
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        'REFERRER_POLICY': 'no-referrer-when-downgrade',
        'ITEM_PIPELINES': {
            'roszdravnadzor_pipelines.RoszdravnadzorPipeline': 1000,
        },
    }
    
    def parse(self, response):
        data = json.loads(response.body)
        for row in data.get('data', []):
            parse_data = []
            for column in range(1, 18):
                column_index = f'col{column}'
                if column_index == 'col9':
                    continue
                value = row[column_index].get('title', None)
                if not value:
                    value = row[column_index].get('label', '')
                if column_index == 'col10':
                    col9_10_values = value.split(' Приказ: ')
                    if len(col9_10_values) > 1:
                        parse_data.append((COLUMN_NAMES['col9'], col9_10_values[1]))
                        value = col9_10_values[0]
                if column_index == 'col12':
                    value = None if value == 'Бессрочно' else value
                parse_data.append((COLUMN_NAMES[column_index], value))
            parse_data.append(('work_address_list', row['objects']))
            parse_data.append(('work_address_xls', response.meta.get('address')))
            yield OrderedDict(parse_data)

        start_page = int(response.meta.get('page')) + self.length
        for page in range(start_page, data['recordsTotal'], self.length):
            yield FormRequest(
                url=response.url,
                formdata={
                    'draw': '4',
                    'start': f'{page}',
                    'length': f'{self.length}',
                    'prev_total': f'{data["recordsTotal"]}',
                    'q_no': '5047045359',
                    **REQUEST_TABLE_DATA
                },
                meta={'page': page},
                callback=self.parse
            )

    def read_xls(self):
        try:
            book = xlrd.open_workbook(self.xls_file,encoding_override="cp1251")  
        except:
            book = xlrd.open_workbook(self.xls_file)
        sh = book.sheet_by_index(0)
        for rx in range(sh.nrows):
            yield (
                sh.cell(rx, self.inn_col_index).value,
                sh.cell(rx, self.address_col_index).value,
            )

    def start_requests(self):        
        for inn, address in self.read_xls():
            time.sleep(1)
            try:
                yield FormRequest(
                    url=self.start_url,
                    formdata={
                        'draw': '2',
                        'start': '0',
                        'length': f'{self.length}',
                        'prev_total': '0',
                        'q_no': "{}".format(int(inn)),
                        **REQUEST_TABLE_DATA
                    },
                    meta={
                        'page': 0,
                        'address': address,
                    },
                    callback=self.parse
                )
            except Exception as error:
                print(error)

