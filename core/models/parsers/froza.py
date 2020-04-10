import json

from core.models import part as part_
from core.models.base.parser import get_parse_part_parser as parser


class Froza(parser.GetParsePartParser):
    OUTPUT_FILE = 'froza.xlsx'

    MULTI_REQUEST = True
    THREADS_COUNT = 50

    DELAY = 15

    def get_part_html(self, part):
        url = f'https://www.froza.ru/index.php/search/original.json?' \
              f'multi=1&detail_num={part.number}&make_name={part.model}' \
              f'&country=10&region_id=0&discount_id=258&sort=sortByPrice&add_warehouse='
        r = self.request(url, retry=True)
        return r.text

    @staticmethod
    def parse_html(html, part):
        json_response = json.loads(html)
        block = json_response['data']
        if not block:
            return Froza.not_found(part)

        for inner_block in block.values():
            return Froza._parse_part_from_block_model(inner_block, part)

        return Froza.not_found(part)

    @staticmethod
    def _parse_part_from_block_model(block_model, part):
        stores = list(block_model.values())[0]
        if len(stores) == 0:
            return Froza.not_found(part)

        inner = stores[0] if len(stores) == 1 else stores[1]

        number = inner[3]
        title = inner[4]
        price = Froza._get_price_from_element(inner[16])

        ready_part = part_.Part(number, part.model, title, price)
        return ready_part

    @staticmethod
    def _get_price_from_element(element):
        return str(element).replace(',', '.')
