import json
import traceback

import bs4

from core.models import part as part_
from core.models.base.parser import get_parse_part_parser as parser


class Parterra(parser.GetParsePartParser):
    def get_part_html(self, part):
        url = f'http://parterra.ru/utils/?action=search&term={part.number} {self.prepare_model(part.model)}'
        r = self.request(url, method='POST')

        url2 = self._parse_part_url(r, part)

        if url2 is None:
            return None

        r = self.request(url2)
        return r.text

    @staticmethod
    def parse_html(html, part):
        if html is None or not html:
            return Parterra.not_found(part)

        soup = bs4.BeautifulSoup(html, 'html.parser')
        min_title_block = soup.select_one('div.product-title > h1')
        if min_title_block is None:
            return part.not_found(part)
        min_title = min_title_block.get_text()

        prices_block = soup.select_one('div.product-others')
        if not prices_block or 'Аналоги' in prices_block:
            return Parterra.not_found(part)

        prices_html = prices_block.select('div.price')
        if not prices_html:
            return Parterra.not_found(part)

        prices = [float(price.contents[0].replace(' ', '')) for price in prices_html]
        span_price = soup.select_one('span.price')
        if not span_price:
            return Parterra.not_found(part)
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
        return ready_part

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

    def _parse_part_url(self, r, part):
        try:
            json_response = json.loads(r.text)
        except json.JSONDecodeError:
            return None

        if 'suggestions' not in json_response:
            return None

        suggestions = json_response['suggestions']
        for suggestion in suggestions:
            suggestion_value = Parterra._prepare_string(suggestion['value'])

            if str(part.number).replace(' ', '').upper() in suggestion_value \
                    and Parterra._prepare_string(self.prepare_model(part.model)) in suggestion_value:
                return 'http://parterra.ru' + suggestion['href']
        return None

    @staticmethod
    def _prepare_string(string):
        return str(string) \
            .replace('-', '') \
            .replace(' ', '') \
            .replace('/', '') \
            .replace('.', '') \
            .upper()
