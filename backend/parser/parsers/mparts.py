from bs4 import BeautifulSoup


import json
import re
import requests

from backend.parser.parsers.parser import Parser
from backend.parser.parts.part import Part


class Mparts(Parser):
    OUTPUT_FILE = 'mparts.xlsx'
    OUTPUT_TABLE = 'Mparts'

    NEED_AUTH = False

    MULTI_REQUEST = True
    THREADS_COUNT = 50

    TIME_SLEEP = 0

    def get_part_html(self, part):
        url = f'https://www.v01.ru/auto/search/{part.number}/?brand_title={self.prepare_model(part.model)}'
        proxies = self.get_next_proxies()
        r = requests.post(url, verify=False, proxies=proxies, timeout=15)
        return r.text

    def prepare_model(self, model):
        up_model = model.upper()
        if up_model == 'GENERAL MOTORS':
            return 'GM'
        if 'ROVER' in up_model:
            return 'ROVER%2FLAND+ROVER'
        if 'HYUNDAI' in up_model or 'KIA' in up_model:
            return 'MOBIS'
        if 'MERCEDE' in up_model:
            return 'MERCEDES-BENZ'
        return up_model.replace(' ', '+')

    def login(self):
        pass

    def parse_html(self, html, part):
        try:
            soup = BeautifulSoup(html, 'html.parser')
            min_title = soup.select_one('td.fn')['title']
            min_price_str = soup.select('td.price')[1].get_text()
            min_price = re.sub('[^\.0-9]', '', min_price_str)
            ready_part = Part(part.number, part.model, min_title, min_price)
        except:
            ready_part = Part(part.number, part.model, 'Нет в наличии', 'Нет в наличии')
        return ready_part



