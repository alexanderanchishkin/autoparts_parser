import json
import random
import re
import settings
import string
import time
import traceback

from backend.parser.parsers.parser import Parser
from backend.parser.parts.part import Part


class AutoPiter(Parser):
    OUTPUT_FILE = 'autopiter.xlsx'
    OUTPUT_TABLE = 'AutoPiter'

    NEED_AUTH = False

    DELAY = 15

    MULTI_REQUEST = True
    THREADS_COUNT = 50
    ALL_SLEEP = False

    def prepare_model(self, model):
        if 'ntn' in model:
            return 'Ntn'
        if 'mahle' in model or 'knecht' in model:
            return 'Knecht/Mahle'
        if model.lower() == 'gm':
            return 'General Motors'
        if model.lower() == 'hyundai' or model.lower() == 'hundai':
            model = 'Hyundai-Kia'
        if model.lower() == 'acdelco':
            return 'Ac Delco'
        if '-' in model:
            return '-'.join(map(str.capitalize, model.split('-')))
        if ' ' in model:
            return ' '.join(map(str.capitalize, model.split()))
        return model.capitalize()

    def get_part_html(self, part):
        url = f'https://32.autopiter.ru/api/searchdetails?detailNumber={part.number}'
        headers = self.get_headers()
        proxies = self.get_next_proxies()
        r = self.session.get(url, verify=False, headers=headers, proxies=proxies, timeout=15)

        while r.status_code != 200:
            print('Try again...')
            url = f'https://32.autopiter.ru/api/searchdetails?detailNumber={part.number}'
            headers = self.get_headers()
            proxies = self.get_next_proxies()
            r = self.session.get(url, verify=False, headers=headers, proxies=proxies, timeout=15)

        return r.text

    def login(self):
        pass

    def find_one_part(self, part):
        start_time = time.time()
        try:
            if settings.DEBUG:
                print('start finding')
                print(part)

            html = self.get_part_html(part)
            ready_part, article_id = self.parse_html(html, part)
            if article_id == -1:
                return ready_part

            cost_html = self.get_cost_html(article_id)
            cost = self.parse_cost(cost_html, article_id)
            ready_part.price = cost

            if settings.DEBUG:
                print(ready_part)
                print('end finding')

            if not settings.DEBUG:
                print(f"{self.__class__.__name__}: {self.done}\\{self.amount}\n", end='')
            return ready_part
        except Exception as e:
            print('Произошла ошибка: ', traceback.print_exc())
            print('Деталь: ', part)
            return Part(part.number, part.model, part.model, 'Нет в наличии')
        finally:
            self.done += 1
            settings.progress_list[self.id] = self.done / self.amount
            time.sleep(max(self.DELAY - (time.time() - start_time), 0))
            if self.proxy_index == 0:
                AutoPiter.ALL_SLEEP = True
                # print('SLEEP')
                # time.sleep(self.DELAY)
                AutoPiter.ALL_SLEEP = False
            while AutoPiter.ALL_SLEEP:
                time.sleep(1)

    def parse_html(self, html, part):
        json_response = json.loads(html)
        # while 'data' not in json_response or 'catalogs' not in json_response['data']:
        #     print('Try again...')
        #     html = self.get_part_html(part)
        #     json_response = json.loads(html)
        models = json_response['data']['catalogs']
        relevant_models = [model for model in models if model['catalogName']
                           == self.prepare_model(part.model.lower())]
        if not relevant_models:
            return Part(part.number, part.model, part.model, 'Нет в наличии'), -1

        model = relevant_models[0]
        article_id = model['id']
        title = model['name']

        ready_part = Part(part.number, part.model, title, 0)
        return ready_part, article_id

    def get_cost_html(self, article_id):
        # url = f'https://32.autopiter.ru/api/appraise/getcosts?idArticles={article_id}&searchType=1'
        url = f'https://32.autopiter.ru/api/appraise?id={article_id}&searchType=1'
        headers = self.get_headers()
        proxies = self.get_next_proxies()
        r = self.session.get(url, verify=False, headers=headers, proxies=proxies, timeout=15)
        return r.text

    def parse_cost(self, cost_html, article_id):
        json_response = json.loads(cost_html)
        if 'data' not in json_response:
            print('error')
            print(json_response)
            raise Exception
        stores = json_response['data']
        costs = set([store['price'] for store in stores if 'price' in store and 'articleId' in store and store['articleId'] == article_id])
        sorted_costs = sorted(list(costs))
        if len(sorted_costs) == 0:
            raise Exception
        if len(sorted_costs) == 1:
            return sorted_costs[0]
        return sorted_costs[1]

    def get_headers(self):
        session = ''.join(random.choices(string.ascii_lowercase + string.digits, k=24))
        return {
            'session': session
        }
