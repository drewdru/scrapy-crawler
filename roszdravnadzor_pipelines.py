
import datetime
from difflib import SequenceMatcher


class RoszdravnadzorPipeline(object):
    def convert_date(self, date):
        if date is None:
            return None
        date = datetime.datetime.strptime(date, '%d.%m.%Y')
        return datetime.date.strftime(date, "%Y-%m-%d")

    def process_item(self, item, spider):
        license_data  = {
            "full_name_licensee": item.get('full_name_licensee', ''),
            "brand_name_licensee": item.get('brand_name_licensee', ''),
            "address": item.get('address', ''),
            "okpo": item.get('okpo', ''),
            "number_orders": item.get('number_orders', ''),
            "date": None if item.get('date', '') == '' else self.convert_date(item.get('date')),
            "date_order": None if item.get('date_order', '') == '' else self.convert_date(item.get('date_order')),
            "date_register": None if item.get('date_register', '') == '' else self.convert_date(item.get('date_register')),
            "date_termination": None if item.get('date_termination', '') == '' else self.convert_date(item.get('date_termination')),
            "information_reissuing": item.get('information_reissuing', ''),
            "information_suspension_resumption": item.get('information_suspension_resumption', ''),
            "information_regulations": item.get('information_regulations', ''),
            "information_cancellation": item.get('information_cancellation', ''),
            "information": item.get('information', ''),
            "termination": item.get('termination', ''),
        }

        sequence = SequenceMatcher(
            lambda x: x==" ",
            item.get('work_address_xls', ''),
            item.get('address', ''),
        )
        license_data["address_ratio_with_xls"] = sequence.ratio() * 100

        work_address_list = []
        for work_address in item.get('work_address_list', []):
            work_address_data = {
                "address": work_address['address_fact'],
                "index": work_address['address_fact_zip'],
                "region": work_address['region'],
                "city": work_address['city'],
                "street": work_address['street'],
                "code_fias": work_address['code_fias'],
            }

            works = []
            for work_name in work_address['activity'].split(','):
                work = {
                    "work": work_name.strip(),
                }
                works.append(work)
            work_address_data["works"] = works
            work_address_list.append(work_address_data)
        license_data["work_addresses"] = work_address_list
        return license_data