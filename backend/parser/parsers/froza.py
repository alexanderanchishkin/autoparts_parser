import json
import requests
import settings
import time
import traceback

from backend.parser.parsers.parser import Parser
from backend.parser.parts.part import Part


class Froza(Parser):
    OUTPUT_FILE = 'froza.xlsx'
    OUTPUT_TABLE = 'Froza'

    NEED_AUTH = False
    TIME_SLEEP = 0

    MULTI_REQUEST = True
    THREADS_COUNT = 450

    def find_one_part(self, part):
        start_time = time.time()
        try:
            if settings.DEBUG:
                print('start finding')
                print(part)
            html = self.get_part_html(part)
            ready_part = self.parse_html(html, part)

            if settings.DEBUG:
                print(ready_part)
                print('end finding')

            if not settings.DEBUG:
                print(f"{self.__class__.__name__}: {self.done}\\{self.amount}\n", end='')
            return ready_part
        except Exception as e:
            print('Произошла ошибка: ', traceback.print_exc())
            print('Деталь: ', part)
            return Part(part.number, part.model, 'Нет в наличии', 'Нет в наличии')
        finally:
            self.done += 1
            settings.progress_list[self.id] = self.done / self.amount
            # time.sleep(max(30 - (time.time() - start_time), 0))

    def get_part_html(self, part):
        url = f'https://www.froza.ru/index.php/search/original.json?' \
              f'multi=1&detail_num={part.number}&make_name={part.model}' \
              f'&country=10&region_id=0&discount_id=258&sort=sortByPrice&add_warehouse='
        while True:
            try:
                proxies = self.get_next_proxies()
                r = requests.get(url, proxies=proxies, timeout=15)
                break
            except:
                print('timeout2')
                pass
        return r.text

    def login(self):
        pass

    def parse_html(self, html, part):
        json_response = json.loads(html)
        block = json_response['data']
        if not block:
            return Part(part.number, part.model, 'Нет в наличии', 'Нет в наличии')

        for inner_block in block.values():
            return self.parse_part_from_block_model(inner_block, part)

        return Part(part.number, part.model, 'Нет в наличии', 'Нет в наличии')

    def parse_part_from_block_model(self, block_model, part):
        stores = list(block_model.values())[0]
        if len(stores) == 0:
            return Part(part.number, part.model, 'Нет в наличии', 'Нет в наличии')
        if len(stores) == 1:
            inner = stores[0]
        else:
            inner = stores[1]

        if len(inner) < 4:
            print(block_model)
        number = inner[3]
        title = inner[4]
        price = str(inner[16]).replace(',', '.')

        ready_part = Part(number, part.model, title, price)
        return ready_part
