import json
import traceback

import bs4
import requests

from core.models import part as part_
from core.models.base.parser import parser


class Parterra(parser.Parser):
    OUTPUT_FILE = 'parterra.xlsx'
    OUTPUT_TABLE = 'Parterra'

    NEED_AUTH = False

    MULTI_REQUEST = True
    THREADS_COUNT = 50

    TIME_SLEEP = 0

    def get_part_html(self, part):
        url = f'http://parterra.ru/utils/?action=search&term={part.number} {self.prepare_model(part.model)}'
        proxies = self.get_next_proxies()
        r = requests.post(url, verify=False, proxies=proxies, timeout=15)
        url2 = None
        try:
            json_response = json.loads(r.text)
            suggestions = json_response['suggestions']
            for suggestion in suggestions:
                suggestion_value = suggestion['value'].replace('-', '').replace(' ', '').replace('/', '').replace('.', '').upper()
                if str(part.number).replace(' ', '').upper() in suggestion_value \
                        and self.prepare_model(part.model)\
                        .replace('-', '').replace(' ', '').replace('/', '').replace('.', '').upper() in suggestion_value:
                    url2 = 'http://parterra.ru' + suggestion['href']
                    break
            if not url2:
                return False
        except:
            return False
        proxies = self.get_next_proxies()
        r = requests.get(url2, verify=False, proxies=proxies, timeout=15)
        return r.text

    def prepare_model(self, model):
        up_model = model.upper()
        if up_model == 'GENERAL MOTORS':
            return 'GM'
        if 'HYUNDAI' in up_model or 'KIA' in up_model:
            return 'Hyundai/Kia'
        if 'NTN' in up_model:
            return 'Ntn'
        if 'MERCEDE' in up_model:
            return 'Mercedes'
        if 'MAHLE' in model or 'KNECHT' in model:
            return 'Knecht'
        if 'CITROEN' in up_model or 'PEUGEOT' in up_model:
            return 'Citroen/Peugeot'
        return up_model

    def login(self):
        pass

    def parse_html(self, html, part):
        try:
            if not html:
                raise Exception('Нет в наличии')

            soup = bs4.BeautifulSoup(html, 'html.core')
            min_title = soup.select_one('div.product-title > h1').get_text()

            prices_block = soup.select_one('div.product-others')
            if not prices_block or 'Аналоги' in prices_block:
                raise Exception('Нет в наличии')

            prices_html = prices_block.select('div.price')
            if not prices_html:
                raise Exception('Нет в наличии')

            prices = [float(price.contents[0].replace(' ', '')) for price in prices_html]
            span_price = soup.select_one('span.price')
            if not span_price:
                raise Exception('Нет в наличии')
            main_price = span_price.contents[0].replace(' ', '')
            prices.append(float(main_price))
            prices = sorted(prices)
            if len(prices) == 0:
                raise Exception
            if len(prices) == 1:
                min_price = prices[0]
            else:
                min_price = prices[1]
            ready_part = part_.Part(part.number, part.model, min_title, min_price)
        except:
            traceback.print_exc()
            ready_part = part_.Part(part.number, part.model, 'Нет в наличии', 'Нет в наличии')
        return ready_part
