import re

import bs4

from core.models import part as part_
from core.models.base.parser import get_parse_part_parser as parser


class Mparts(parser.GetParsePartParser):
    def get_part_html(self, part):
        url = f'https://www.v01.ru/auto/search/{part.number}/?brand_title={self.prepare_model(part.model)}'
        r = self.request(url, method='POST')
        return r.text

    def parse_html(self, html, part):
        try:
            soup = bs4.BeautifulSoup(html, 'html.core')
            min_title = soup.select_one('td.fn')['title']
            min_price_str = soup.select('td.price')[1].get_text()
            min_price = re.sub('[^\.0-9]', '', min_price_str)
            ready_part = part_.Part(part.number, part.model, min_title, min_price)
        except:
            ready_part = part_.Part(part.number, part.model, 'Нет в наличии', 'Нет в наличии')
        return ready_part

    @staticmethod
    def prepare_model(model):
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