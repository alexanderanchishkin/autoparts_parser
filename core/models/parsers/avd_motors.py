import json
import traceback

from core.models import part as part_
from core.models.base.parser import get_parse_part_parser as parser


class AvdMotors(parser.GetParsePartParser):
    OUTPUT_FILE = 'avd_motors.xlsx'

    THREADS_COUNT = 50

    def get_part_html(self, part):
        url = f'https://www.avdmotors.ru/price/?number=' \
              f'{part.number.split("#")[0]}&catalog={AvdMotors.prepare_model(part.model)}'
        url2 = f'https://www.avdmotors.ru/price/clones'
        r = self.request(url, method='POST')
        if r is None:
            return None
        r1 = self.request(url2, method='POST')
        if r1 is None:
            return None
        return r.text + '!^^!' + r1.text

    @staticmethod
    def parse_html(html, part):
        response1, response2 = html.split('!^^!')
        try:
            json_response = json.loads(response1)
        except json.decoder.JSONDecodeError:
            return AvdMotors._handle_error(part, response1)

        if 'data' not in json_response:
            return part.not_found()

        prices = json_response['data']
        if isinstance(prices, dict):
            prices = list(prices.values())

        if not prices:
            return part.not_found()

        min_price = prices[0].get('price', None)
        min_title = prices[0].get('item_name', part.number)

        if len(prices) > 1:
            min_price2 = prices[1].get('price', None)
            min_title2 = prices[1].get('item_name', part.number)
        else:
            min_price2 = int(1e+6)
            min_title2 = min_title

        if min_price is None or min_price2 is None:
            return part.not_found()

        try:
            json_response = json.loads(response2)
            clones = json_response['data']
        except json.decoder.JSONDecodeError:
            return AvdMotors._handle_error(part)

        if not clones:
            return part.not_found()

        articles = clones[0]
        if isinstance(articles, dict):
            articles = list(articles.values())
        for prices in articles:
            if isinstance(prices, dict):
                prices = list(prices.values())
            current_min_price = prices[0]['price']
            current_min_title = prices[0].get('item_name', part.number)
            current_min_price2 = prices[1]['price']
            current_min_title2 = prices[1].get('item_name', part.number)

            if current_min_price > min_price2:
                continue
            if current_min_price < min_price:
                min_price2 = min_price
                min_title2 = min_title
                min_price = current_min_price
                min_title = current_min_title

                if current_min_price2 < min_price2:
                    min_price2 = current_min_price2
                    min_title2 = current_min_title2
                continue
            if min_price < current_min_price < min_price2:
                min_price2 = current_min_price
                min_title2 = current_min_title
                continue

        if min_price2 > int(1e+6) - 1:
            min_price2 = min_price
            min_title2 = min_title

        ready_part = part_.Part(part.number, part.model, min_title2, min_price2)
        return ready_part

    @staticmethod
    def prepare_model(model: str):
        up_model = model.upper()
        if 'AC' in up_model and 'DELCO' in up_model:
            return 'AC DELCO'
        if 'MERCEDE' in up_model:
            return 'MERCEDES-BENZ'
        if 'GM' in up_model:
            return 'GENERAL MOTORS'
        if 'HYUNDAI' in up_model or 'KIA' in up_model:
            return 'HYUNDAI/KIA'
        if 'PEUGEOT' in up_model or 'CITROEN' in up_model:
            return 'PEUGEOT / CITROEN'
        return up_model

    @staticmethod
    def _handle_error(part: part_.Part, response):
        print('AVDMotors: ')
        print(response)
        traceback.print_exc()
        return part.not_found()
