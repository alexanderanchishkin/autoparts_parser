import json

import bs4

from core.models import part as part_
from core.models.base.parser import get_parse_part_parser as parser


class Parterra(parser.GetParsePartParser):
    def get_part_html(self, part):
        url = f'http://parterra.ru/utils/?action=search&term={part.number} {self.prepare_model(part.model)}'
        r = self.request(url, method='POST')
        if r is None:
            return None

        url2 = self._parse_part_url(r, part)

        if url2 is None:
            return None

        r1 = self.request(url2)
        if r1 is None:
            return None

        return r1.text

    @staticmethod
    def parse_html(html, part):
        if html is None or not html:
            return part.not_found()

        soup = bs4.BeautifulSoup(html, 'html.parser')

        min_title = Parterra._get_min_title(soup)

        prices = Parterra._get_prices(soup)
        main_price = Parterra._get_main_price(soup)

        if main_price is None:
            return part.not_found()

        prices.append(main_price)
        prices = sorted(prices)

        if len(prices) == 0:
            return part.not_found()

        min_price = prices[0] if len(prices) == 1 else prices[1]
        ready_part = part_.Part(part.number, part.model, min_title, min_price)
        return ready_part

    @staticmethod
    def prepare_model(model):
        if model is None:
            return None

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

    @staticmethod
    def _parse_part_url(r, part):
        try:
            json_response = json.loads(r.text)
        except json.decoder.JSONDecodeError:
            return None

        if 'suggestions' not in json_response:
            return None

        suggestions = json_response['suggestions']
        for suggestion in suggestions:
            if 'value' not in suggestion:
                continue
            if 'href' not in suggestion:
                continue

            suggestion_value = Parterra._prepare_string(suggestion['value'])

            if part.number.replace(' ', '').upper() in suggestion_value \
                    and Parterra._prepare_string(Parterra.prepare_model(part.model)) in suggestion_value:
                return 'http://parterra.ru' + suggestion['href']
        return None

    @staticmethod
    def _get_min_title(soup):
        min_title_block = soup.select_one('div.product-title > h1')
        if min_title_block is None:
            return None
        min_title = min_title_block.get_text()
        return min_title

    @staticmethod
    def _get_prices(soup):
        prices_block = Parterra._get_prices_block(soup)
        if prices_block is None:
            return []
        prices_html = Parterra._get_prices_html(prices_block)
        if prices_html is None:
            return []
        prices = Parterra._get_prices_from_html(prices_html)
        return prices

    @staticmethod
    def _get_prices_block(soup):
        prices_block = soup.select_one('div.product-others')
        if prices_block is None:
            return None

        if prices_block.find('h3') is not None and 'Аналоги' in prices_block.find('h3').text:
            return None
        return prices_block

    @staticmethod
    def _get_prices_html(prices_block):
        return prices_block.select('div.price')

    @staticmethod
    def _get_prices_from_html(prices_html):
        raw_prices = [Parterra._prepare_price(price) for price in prices_html]
        prices = [price for price in raw_prices if price is not None]
        return prices

    @staticmethod
    def _get_main_price(soup):
        span_price = soup.select_one('span.price')
        if span_price is None:
            return None

        main_price = Parterra._prepare_price(span_price)
        return main_price

    @staticmethod
    def _prepare_price(price):
        if price is None:
            return None
        if not price.contents:
            return None
        return float(price.contents[0].replace(' ', '').split('<')[0])

    @staticmethod
    def _prepare_string(string):
        return str(string) \
            .replace('-', '') \
            .replace(' ', '') \
            .replace('/', '') \
            .replace('.', '') \
            .upper()
