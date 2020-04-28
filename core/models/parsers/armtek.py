import json
import random
import traceback

from config import settings
from core.models import part as part_
from core.models.base.parser import part_parser as parser


class Armtek(parser.PartParser):
    OUTPUT_FILE = 'armtek.xlsx'

    DELAY = 1
    BUFFER_SIZE = settings.DEFAULT_PARSER_BUFFER_SIZE
    THREADS_COUNT = 1

    USE_SESSION = True
    USE_PROXY = False

    def login(self):
        return
        url = f'https://etp.armtek.ru/authorization/identify/?' + str(random.uniform(0, 1))

        data = {
            'LOGIN': 'SUNLIGHT.VOLKOV@MAIL.RU',
            'PASSWORD': 'Verjabnby123',
            'REMEMBER': '1',
            'CAPTCHA': '',
            'FORMAT': 'json',
            'LANG': 'ru'
        }

        r = self.request(url, data=data, method='POST')
        print('login')
        print(r.text)

    def find_one_part(self, part):
        part_id_html = self.get_part_id_html(part)
        if part_id_html is None:
            return part.not_found()
        part_id = self.parse_part_id_html(part_id_html, part)
        if part_id is None:
            return part.not_found()
        part_html = self.get_part_html(part_id, part.model)
        if part_html is None:
            return part.not_found()
        part = self.parse_html(part_html, part)

        print(part)
        return part

    def get_part_id_html(self, part):
        url = 'https://etp.armtek.ru/search/autocomplete/?' + str(random.uniform(0, 1))
        data = {
            'str': part.number,
            'type': '1',
            'FORMAT': 'json',
            'LANG': 'ru'
        }
        r = self.request(url, data=data, method='POST')
        if r is None:
            return None

        return r.text

    def parse_part_id_html(self, part_id_html, part):
        try:
            json_part_id_html = json.loads(part_id_html)
            if not json_part_id_html['status']:
                return None

            if 'data' not in json_part_id_html or not json_part_id_html['data']:
                return None

            for key, brand_block in json_part_id_html['data'].items():
                if 'BRAND' not in brand_block:
                    continue
                if brand_block['BRAND'] == self.prepare_model(part.model):
                    return key
            return None
        except json.JSONDecodeError:
            return None

    def get_part_html(self, part_id, model):
        url = 'https://etp.armtek.ru/search/getArticlesBySearch/?' + str(random.uniform(0, 1))
        data = {
            'QUERY': str(part_id),
            'QUERY_TYPE': '5',
            'QUERY_DATA': 'S2',
            'OPTRS': True,
            'PKW': 'X',
            'LKW': 'X',
            'page': '1',
            'FORMAT': 'json',
            'LANG': 'ru'
        }

        r = self.request(url, data=data, method='POST')
        if r is None:
            return None
        return r.text

    def get_headers(self):
        return {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "Cookie": "ci_sessions=ffc57af6a91749ff3d60683c221ddeb6da4d777b",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://etp.armtek.ru",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://etp.armtek.ru/",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
        }

    @staticmethod
    def parse_html(html, part):
        try:
            json_part = json.loads(html)
        except json.JSONDecodeError:
            return part.not_found()

        if not json_part['status']:
            print('status false')
            print(json_part)
            return part.not_found()

        if 'data' not in json_part:
            print('no data')
            return part.not_found()

        if 'TBL' not in json_part['data']:
            print('no tbl')
            return part.not_found()

        if 'SRCDATA' not in json_part['data']['TBL']:
            print('no srcdata')
            return part.not_found()

        parts = json_part['data']['TBL']['SRCDATA']
        if not parts:
            print('no parts')
            return part.not_found()

        if parts[0]['RSTP'] == 1:
            print('here')
            return part.not_found()

        if len(parts) == 1 or parts[1]['RSTP'] == 1:
            print('here2')
            return part_.Part(part.number, part.model, parts[0]['NAME'], parts[0]['PRICES1'])

        return part_.Part(part.number, part.model, parts[1]['NAME'], parts[1]['PRICES1'])

    @staticmethod
    def prepare_model(model: str):
        up_model = model.upper()
        if 'AC' in up_model and 'DELCO' in up_model:
            return 'AC DELCO'
        if 'MERCEDE' in up_model:
            return 'MB'
        if 'GM' in up_model or 'GENERAL' in up_model:
            return 'GM'
        if 'HYUNDAI' in up_model:
            return 'HYUNDAI'
        if 'KIA' in up_model:
            return 'KIA'
        if 'PEUGEOT' in up_model or 'CITROEN' in up_model:
            return 'PSA'
        return up_model
