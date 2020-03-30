import re
import requests
import settings
import time
import traceback

from backend.parser.parts.part import Part
from backend.parser.parts.parts_explorer import write_parts_to_xlsx, write_column_to_xlsx

from multiprocessing.dummy import Pool as ThreadPool


class Parser:
    AUTH = None
    BUFFER_SIZE = 5000

    OUTPUT_FILE = None
    OUTPUT_TABLE = None

    NEED_AUTH = True
    TIME_SLEEP = 0

    REQUEST_METHOD = None
    HEADERS = None

    MULTI_REQUEST = False
    THREADS_COUNT = 0

    def __init__(self, parser_id=0):
        self.id = parser_id
        self.current_proxies = None
        self.proxy_index = 0
        with open('proxies.txt', 'r') as f:
            self.proxies = f.read().splitlines()
        self.session = requests.Session()
        self.amount = 0
        self.done = 0

        if not self.OUTPUT_FILE or not self.OUTPUT_TABLE:
            raise Exception(f'{self.__class__.__name__}: Для магазина не указано название файла и/или таблицы')

        if self.NEED_AUTH and not self.AUTH:
            raise Exception(f'{self.__class__.__name__}: Нужна авторизация, нет логина/пароля')

    def prepare_proxy(self, proxy):
        return {
              "http": f'http://{proxy}',
              "https": f'https://{proxy}',
        }

    def get_next_proxies(self):
        proxy = self.prepare_proxy(self.proxies[self.proxy_index])
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy

    def find_parts(self, parts):
        start_time = time.time()
        self.amount = len(parts)
        self.done = 0

        self.login()
        self.write_new_column()
        # if not settings.DEBUG:
        #     print(f'{self.__class__.__name__}: {self.done}\\{self.amount}')

        parts_chunks = [parts[i:i + min(len(parts), self.BUFFER_SIZE)] for i in range(0, len(parts), self.BUFFER_SIZE)]
        for parts_chunk in parts_chunks:
            if self.MULTI_REQUEST:
                p = ThreadPool(self.THREADS_COUNT)
                ready_parts_array = list(p.map(self.find_one_part, parts_chunk))
            else:
                ready_parts_array = [self.find_one_part(part) for part in parts_chunk]
            ready_parts = {part.number: part for part in ready_parts_array}
            print('Saving...')

            if not settings.is_running:
                print('Terminating...')
                break
            self.save_result(ready_parts)

        print('time:', time.time() - start_time)
        return True

    def find_one_part(self, part):
        try:
            time.sleep(self.__class__.TIME_SLEEP)
            if settings.DEBUG:
                print('start finding')
                print(part)
            html = self.get_part_html(part)
            ready_part = self.parse_html(html, part)
            if settings.DEBUG:
                print(ready_part)
                print('end finding')

            return ready_part
        except Exception:
            print('Произошла ошибка: ', traceback.print_exc())
            print('Деталь: ', part)
            return Part(part.number, part.model, part.model, '')
        finally:
            self.done += 1
            settings.progress_list[self.id] = self.done / self.amount
            if not settings.DEBUG:
                print(f"{self.__class__.__name__}: {self.done}\\{self.amount}\n", end='')

    def get_part_html(self, part):
        raise NotImplementedError()

    def do_request(self, url, data):
        request_method = self.__class__.REQUEST_METHOD
        r = None
        if request_method == 'GET':
            r = self.session.get(url, data=data)
        elif request_method == 'POST':
            r = self.session.post(url, data=data)

        if not r:
            raise Exception(f'{self.__class__.__name__}: Unknown Request Method')

        return r

    def save_result(self, ready_parts):
        if settings.DEBUG:
            print(f'{self.__class__.__name__}: Начинаем запись в таблицу')
        write_parts_to_xlsx(self.OUTPUT_FILE, self.OUTPUT_TABLE, ready_parts, settings.TIME_MOMENT)
        if settings.DEBUG:
            print(f'{self.__class__.__name__}: Детали сохранены')

    def write_new_column(self):
        write_column_to_xlsx(self.OUTPUT_FILE, self.OUTPUT_TABLE, settings.TIME_MOMENT)

    def check_model(self, model1, model2):
        pattern = '[^a-zA-Z]+'
        re1 = re.sub(pattern, '', model1.replace(' ', '').lower())
        re2 = re.sub(pattern, '', model2.replace(' ', '').lower())
        re1 = self.check_abbr(re1)
        re2 = self.check_abbr(re2)
        custom_checked = self.custom_check(re1, re2, model1, model2)
        return (len(re1) > 1 and len(re2) > 1 and re1 == re2) or custom_checked

    def custom_check(self, re1, re2, model1, model2):
        if model1.lower() == 'mercedez' or model1.lower() == 'mercedes':
            return model1.lower()[:-1] in model2.lower()

        if model1.lower() == 'hyundai' or model1.lower() == 'hundai':
            return 'hyundai' in model2.lower()

        if re1 == 'toyotalexux' or re2 == 'toyotalexux' or re1 == 'lexustoyota' or re2 == 'lexustoyota':
            return re1 == re2 or re1 == 'toyota' or re2 == 'toyota' or re1 == 'citroen' or re2 == 'lexus'

        if re1 == 'citroenpeugeot' or re2 == 'citroenpeugeot' or re1 == 'peugeotcitroen' or re2 == 'peugeotcitroen':
            return re1 == re2 or re1 == 'citroen' or re2 == 'citroen' or re1 == 'peugeot' or re2 == 'peugeot'

        return re1 == re2

    def check_abbr(self, short_model):
        if short_model == 'gm':
            return 'generalmotors'

        if short_model == 'mercedez':
            return 'mercedezbenz'

        return short_model

    def login(self):
        raise NotImplementedError()

    def parse_html(self, html, part):
        raise NotImplementedError()
