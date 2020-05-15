import json
import random
import string

from config import settings
from core.models import part as part_
from core.models.base.parser import part_parser


class Autopiter(part_parser.PartParser):
    OUTPUT_FILE = 'autopiter.xlsx'

    DELAY = 15
    BUFFER_SIZE = int(1.5 * settings.DEFAULT_PARSER_BUFFER_SIZE)
    THREADS_COUNT = int(1.5 * settings.DEFAULT_PARSER_THREADS_COUNT)

    def find_one_part(self, part):
        html = self.get_part_html(part)
        if html is None:
            return part.not_found()

        ready_part, article_id = self.parse_html(html, part)

        if article_id == -1:
            return ready_part

        cost_html = self._get_cost_html(article_id)
        if cost_html is None:
            return part.not_found()

        cost = Autopiter._parse_cost(cost_html, article_id)

        if cost is None:
            return ready_part.not_found()

        ready_part.price = cost
        return ready_part

    def get_part_html(self, part):
        url = f'https://32.autopiter.ru/api/searchdetails?detailNumber={part.number}'
        r = self.request(url)
        if r is None:
            return None
        return r.text

    def _get_cost_html(self, article_id):
        url = f'https://32.autopiter.ru/api/appraise?id={article_id}&searchType=1'
        r = self.request(url)
        if r is None:
            return None
        return r.text

    @staticmethod
    def parse_html(html, part: part_.Part):
        try:
            json_response = json.loads(html)
        except json.decoder.JSONDecodeError:
            return None

        models = json_response['data']['catalogs']

        relevant_models = [model for model in models
                           if model['catalogName'] == Autopiter.prepare_model(part.model.lower())]
        if not relevant_models:
            return part.not_found(), -1

        model = relevant_models[0]
        article_id = model['id']
        title = model['name']

        ready_part = part_.Part(part.number, part.model, title, 0)
        return ready_part, article_id

    @staticmethod
    def prepare_model(model):
        if 'mersede' in model.lower() or 'mercede' in model.lower():
            return 'Mercedes'
        if 'ntn' in model.lower():
            return 'Ntn'
        if 'mahle' in model.lower() or 'knecht' in model.lower():
            return 'Knecht/Mahle'
        if 'gm' in model.lower() or 'general' in model.lower():
            return 'General Motors'
        if 'hyundai' in model.lower() or 'hundai' in model.lower():
            return 'Hyundai-Kia'
        if 'delco' in model.lower():
            return 'Ac Delco'
        if '-' in model:
            return '-'.join(map(str.capitalize, model.split('-')))
        if ' ' in model:
            return ' '.join(map(str.capitalize, model.split()))
        return model.capitalize()

    @staticmethod
    def _parse_cost(cost_html, article_id):
        try:
            json_response = json.loads(cost_html)
        except json.decoder.JSONDecodeError:
            return None

        if 'data' not in json_response:
            print('error')
            print(json_response)
            return None

        stores = json_response['data']
        costs = Autopiter._get_unique_costs_from_stores(stores, article_id)
        sorted_costs = sorted(costs)

        if len(sorted_costs) == 0:
            return None

        return sorted_costs[1] if len(sorted_costs) > 1 else sorted_costs[0]

    @staticmethod
    def _get_unique_costs_from_stores(stores, article_id):
        return list(set(Autopiter._get_costs_from_stores(stores, article_id)))

    @staticmethod
    def _get_costs_from_stores(stores, article_id):
        return [store['price'] for store in stores
                if 'price' in store and 'articleId' in store and store['articleId'] == article_id]

    @staticmethod
    def get_headers():
        session_key = Autopiter._generate_session_key()
        return {
            'session': session_key
        }

    @staticmethod
    def _generate_session_key():
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=24))
