import json
import traceback

from core.models import part as part_
from core.models.base.parser import get_parse_part_parser as parser


class Autodoc(parser.GetParsePartParser):
    USE_PROXY = False

    def get_part_html(self, part):
        url = f'https://webapi.autodoc.ru/api/manufacturers/{part.number.split("#")[0]}/?showAll=true'
        r = self.request(url, method='GET')
        if r is None:
            return None
        if r.status_code == 500:
            return None

        try:
            manufactures = json.loads(r.text)
            manufacturer_id = self.find_model(self.prepare_model(part.model), manufactures)
        except:
            traceback.print_exc()
            return None

        if manufacturer_id is None:
            return None

        url2 = f'https://webapi.autodoc.ru/api/spareparts/{manufacturer_id}/{part.number.split("#")[0]}/null?isrecross=false'
        r = self.request(url2, method='GET')
        if r is None:
            return None
        if r.status_code == 500:
            return None

        return r.text

    def find_model(self, model, manufactures):
        for manufacturer in manufactures:
            if self.prepare_model(model) == manufacturer.get('manufacturerName', None):
                return manufacturer['id']
        return None

    @staticmethod
    def parse_html(html, part):
        response = html

        try:
            json_response = json.loads(response)
        except json.decoder.JSONDecodeError:
            return Autodoc._handle_error(part, response)

        name = json_response.get('name', None)
        items = json_response.get('inventoryItems', None)

        if not json_response or not items:
            print('no data')
            return part.not_found()

        for part_info in items:
            price = part_info.get('price', None)

            ready_part = part_.Part(part.number, part.model, name, price)
            return ready_part

        print('no part_info')
        return part.not_found()

    @staticmethod
    def prepare_model(model: str):
        up_model = model.upper()

        if 'BMW' in up_model:
            return 'BMW/MINI/RR'
        if 'NTN' in up_model or 'SNR' in up_model:
            return 'NTN-SNR'
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
        print('Autodoc: ')
        print(response)
        traceback.print_exc()
        return part.not_found()
