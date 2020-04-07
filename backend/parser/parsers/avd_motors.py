import json
import re
import requests
import traceback

from backend.parser.parsers.parser import Parser
from backend.parser.parts.part import Part


class AvdMotors(Parser):
    OUTPUT_FILE = 'avd_motors.xlsx'
    OUTPUT_TABLE = 'AVDMotors'

    NEED_AUTH = False

    MULTI_REQUEST = True
    THREADS_COUNT = 50

    TIME_SLEEP = 0

    def get_part_html(self, part):
        url = f'https://www.avdmotors.ru/price/?number=' \
              f'{part.number.split("#")[0]}&catalog={self.prepare_model(part.model)}'
        proxies = self.get_next_proxies()
        r = requests.post(url, verify=False, proxies=proxies, timeout=15)
        url2 = f'https://www.avdmotors.ru/price/clones'
        proxies = self.get_next_proxies()
        json_request = {'number': part.number, 'catalog': self.prepare_model(part.model)}
        r1 = requests.post(url2, json=json_request, verify=False, proxies=proxies, timeout=15)
        return r.text + '!^^!' + r1.text

    def prepare_model(self, model):
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

    def login(self):
        pass

    def parse_html(self, html, part):
        response1, response2 = html.split('!^^!')
        try:
            json_response = json.loads(response1)
        except:
            traceback.print_exc()
            print(response1)
            return Part(part.number, part.model, 'Нет в наличии', 'Нет в наличии')
        prices = json_response['data']
        if isinstance(prices, dict):
            prices = list(prices.values())

        if not prices:
            return Part(part.number, part.model, 'Нет в наличии', 'Нет в наличии')

        try:
            min_price = prices[0]['price']
            min_title = prices[0].get('item_name', part.number)
        except:
            traceback.print_exc()
            print(response1)
            return Part(part.number, part.model, 'Нет в наличии', 'Нет в наличии')
        if len(prices) > 1:
            min_price2 = prices[1]['price']
            min_title2 = prices[1].get('item_name', part.number)
        else:
            min_price2 = int(1e+6)
            min_title2 = min_title

        try:
            json_response = json.loads(response2)
            clones = json_response['data']
            if not clones:
                raise Exception
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
        except:
            pass

        if min_price2 > int(1e+6) - 1:
            min_price2 = min_price

        ready_part = Part(part.number, part.model, min_title2, min_price2)
        return ready_part



