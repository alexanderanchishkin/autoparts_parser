import json
import traceback

from core.models import part as part_
from core.models.base.parser import get_parse_part_parser as parser


class AvdMotors(parser.GetParsePartParser):
    def get_part_html(self, part):
        url = f'https://www.avdmotors.ru/api/items/{part.number.split("#")[0]}'
        r = self.request(url, method='POST')
        if r is None:
            return None
        if r.status_code == 500:
            return None
        return r.text

    @staticmethod
    def parse_html(html, part):
        response = html

        try:
            json_response = json.loads(response)
        except json.decoder.JSONDecodeError:
            return AvdMotors._handle_error(part, response)

        if not json_response:
            print('no data')
            return part.not_found()

        for part_info in json_response:
            catalog_info = part_info.get('catalog', None)
            if catalog_info is None:
                continue
            model = catalog_info.get('name', None)
            if model is None or model != AvdMotors.prepare_model(part.model):
                continue

            price = part_info.get('price', None)
            title = part_info.get('name', part.number)

            ready_part = part_.Part(part.number, part.model, title, price)
            return ready_part

        print('no part_info')
        return part.not_found()

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
        if 'HELLA' in up_model:
            return 'BEHR-HELLA'
        return up_model

    @staticmethod
    def _handle_error(part: part_.Part, response):
        print('AVDMotors: ')
        print(response)
        traceback.print_exc()
        return part.not_found()
