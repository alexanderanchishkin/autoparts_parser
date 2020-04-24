import abc
import os

import requests
import stringcase

from config import settings
from core.io.database.utilities import part as part_db
from core.io.xlsx import part as part_xlsx
from core.utilities import parser as parser_
from core.utilities import proxy as proxy_
from core.utilities import stopwatch
from process import process as process_


class Parser(abc.ABC):
    BUFFER_SIZE = settings.DEFAULT_PARSER_BUFFER_SIZE
    OUTPUT_FILE = None

    DELAY = 0

    THREADS_COUNT = settings.DEFAULT_PARSER_THREADS_COUNT

    USE_SESSION = False
    USE_PROXY = True

    def __init__(self, xlsx_input=True, xlsx_output=True, sql_input=False, sql_output=True):
        self.xlsx_input = xlsx_input
        self.xlsx_output = xlsx_output

        self.sql_input = sql_input
        self.sql_output = sql_output

        self.table_prefix = settings.time_moment_db_table_prefix
        self.table_name = self.table_prefix + self.get_output_filename().split('.')[0]

        self.current_proxies = None
        self.proxies = []
        self.proxy_index = 0

        self.wb = None

        self.done = 0
        self.total = 0

        self.session = requests.Session() if self.USE_SESSION else None

    @stopwatch.time('Parser')
    def execute(self, iter_parts, count):
        if not iter_parts:
            return False

        self.total = count
        self._initialize()

        self.login()

        if self.xlsx_output:
            self.wb = part_xlsx.start_write_parts(settings.time_moment, self.__class__.__name__)

        self.find_parts(iter_parts)

        if self.xlsx_output and self.wb is not None:
            part_xlsx.save_temp_parts(self.wb, self.get_output_filename())

        progress_file = os.path.join(settings.PROGRESS_FOLDER, self.__class__.__name__)
        try:
            if os.path.isfile(progress_file):
                os.remove(progress_file)
        except:
            import traceback
            traceback.print_exc()

    def login(self):
        pass

    def _initialize(self):
        self.done = 0
        self.proxies = proxy_.load()

    def save_result(self, ready_parts):
        if self.sql_output:
            part_db.write_parts(self.table_name, ready_parts)
        if self.xlsx_output:
            part_xlsx.write_parts_to_xlsx(self.wb.active, ready_parts)

    def request(self, url, headers=None, proxies=None, retry=True,
                method='GET', verify=False, timeout=15, attempts=3, use_proxy=None, data=None, json_data=None):
        if headers is None:
            headers = self.get_headers()

        use_proxy = use_proxy if use_proxy is not None else self.USE_PROXY
        client = self.session if self.session is not None else requests

        attempts_count = 0
        while True:
            params = {
                'headers': headers,
                'verify': verify,
                'timeout': timeout
            }

            if use_proxy:
                if proxies is None:
                    proxies = self.get_next_proxies()
                params['proxies'] = proxies

            if data is not None:
                params['data'] = data
            if json_data is not None:
                params['json_data'] = json_data

            try:
                r = client.request(method, url, **params)

                if not retry or r.status_code == 200:
                    return r
            except requests.exceptions.ConnectTimeout:
                print('Connection timeout')
                import traceback
                traceback.print_exc()
                pass
            except requests.exceptions.ConnectionError:
                print('Connection error')
                import traceback
                traceback.print_exc()
                pass
            except requests.exceptions.ReadTimeout:
                print('Timeout')
                import traceback
                traceback.print_exc()
                pass

            attempts_count += 1

            if attempts_count == attempts:
                return None

    def get_next_proxies(self):
        proxy = proxy_.prepare_proxy(self.proxies[self.proxy_index])
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy

    def print_progress(self):
        data= f"{self.__class__.__name__}: {self.done}\\{self.total}"

        if True or self.done % 100 == 0 or self.done == 1 or self.done == self.total:
            with open(os.path.join(settings.PROGRESS_FOLDER, self.__class__.__name__), 'w') as f:
                f.write(data)

        if True or self.done % 100 == 0 or self.done == 1 or self.done == self.total:
            print(f"{data}\n", end='')

    def get_output_filename(self) -> str:
        if self.OUTPUT_FILE is not None:
            return self.OUTPUT_FILE
        return stringcase.snakecase(self.__class__.__name__) + '.xlsx'

    @staticmethod
    def get_headers():
        return {}

    @staticmethod
    def prepare_model(model):
        return model

    @abc.abstractmethod
    def find_parts(self, iter_parts):
        pass
