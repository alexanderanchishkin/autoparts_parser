import re

import bs4

from core.models import part as part_
from core.models.base.parser import get_parse_part_parser as parser


class Mparts(parser.GetParsePartParser):
    def get_part_html(self, part):
        url = f'https://www.v01.ru/auto/search/{part.number}/?brand_title={self.prepare_model(part.model)}'
        r = self.request(url, method='POST')
        if r is None:
            return None
        return r.text

    def parse_html(self, html, part):
        if html is None or not html:
            return part.not_found()

        soup = bs4.BeautifulSoup(html, 'html.parser')

        min_title = Mparts._get_min_title(soup)
        min_price = Mparts._get_min_price(soup)

        if min_price is None:
            return part.not_found()

        ready_part = part_.Part(part.number, part.model, min_title, min_price)
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

    @staticmethod
    def _get_min_title(soup):
        fn_block = soup.select_one('td.fn')
        if fn_block is None:
            return None
        if not hasattr(fn_block, 'title'):
            return None
        min_title = fn_block['title']
        return min_title

    @staticmethod
    def _get_min_price(soup):
        block_prices = soup.select('td.price')
        if block_prices is None:
            return None

        if not block_prices:
            return None

        min_price_block = block_prices[0] if len(block_prices) == 1 else block_prices[1]
        min_price_string = min_price_block.get_text()

        min_price = Mparts._prepare_price(min_price_string)
        return min_price

    @staticmethod
    def _prepare_price(string):
        return re.sub('[^.0-9]', '', string)
