import json
import re
import requests

from backend.parser.parsers.parser import Parser
from backend.parser.parts.part import Part


class AvdMotors(Parser):
    OUTPUT_FILE = 'avd_motors.xlsx'
    OUTPUT_TABLE = 'AVDMotors'

    NEED_AUTH = False

    MULTI_REQUEST = True
    THREADS_COUNT = 450

    TIME_SLEEP = 0

    def get_part_html(self, part):
        url = f'https://www.avdmotors.ru/price/?number={part.number}&catalog={part.model}'
        proxies = self.get_next_proxies()
        r = requests.post(url, verify=False, proxies=proxies)
        return r.text

    def login(self):
        pass

    def parse_html(self, html, part):
        json_response = json.loads(html)
        replaces = json_response['replaces']
        brand_replaces = \
            [replace for replace in replaces
             if self.check_model(part.model, replace['catalogName'])]
        if not brand_replaces:
            return Part(part.number, part.model, part.model, 'Нет в наличии оригинала')
        min_price = int(1e+6)
        min_title = part.model
        for brand_replace in brand_replaces:
            if int(brand_replace['min']) < min_price:
                min_price = int(brand_replace['min'])
                min_title = brand_replace['itemName']
        ready_part = Part(part.number, part.model, min_title, min_price)
        return ready_part



