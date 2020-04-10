import abc
import traceback

import requests

from config import settings
from core.io.database.utilities import part as part_db
from core.io.xlsx import part as part_xlsx
from core.models import part as part_
from core.utilities import parser as parser_
from core.utilities import proxy as proxy_
from core.utilities import stopwatch


class Parser(abc.ABC):
    BUFFER_SIZE = 100
    OUTPUT_FILE = None

    DELAY = 0

    THREADS_COUNT = 50

    def __init__(self, xlsx_input=True, xlsx_output=True, sql_input=False, sql_output=True):
        self.xlsx_input = xlsx_input
        self.xlsx_output = xlsx_output

        self.sql_input = sql_input
        self.sql_output = sql_output

        self.table_prefix = settings.time_moment_db_table_prefix
        self.table_name = self.table_prefix + parser_.get_output_filename(self).split('.')[0]

        self.current_proxies = None
        self.proxies = []
        self.proxy_index = 0

        self.wb = None

        self.done = 0
        self.total = 0

    @stopwatch.time('Parser')
    def execute(self, iter_parts, count):
        if not iter_parts:
            return False

        self.total = count
        self.initialize()

        if self.xlsx_output:
            self.wb = part_xlsx.start_write_parts(settings.time_moment)

        ready_parts = self.find_parts(iter_parts)

        if self.xlsx_output and self.wb is not None:
            part_xlsx.save_temp_parts(self.wb, parser_.get_output_filename(self))
        return ready_parts

    def initialize(self):
        self.done = 0
        self.proxies = proxy_.load()

    def save_result(self, ready_parts):
        if self.sql_output:
            part_db.write_parts(self.table_name, ready_parts)
        if self.xlsx_output:
            part_xlsx.write_parts_to_xlsx(self.wb.active, ready_parts)

    def request(self, url, headers=None, proxies=None, retry=True, method='GET', verify=False, timeout=15, attempts=5):
        if headers is None:
            headers = self.__class__.get_headers()

        attempts_count = 0
        while True:
            if proxies is None:
                proxies = self.get_next_proxies()

            r = requests.request(method, url, headers=headers, proxies=proxies, verify=verify, timeout=timeout)
            attempts_count += 1

            if not retry or r.status_code == 200 or attempts_count == attempts:
                return r

    def get_next_proxies(self):
        proxy = proxy_.prepare_proxy(self.proxies[self.proxy_index])
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy

    @staticmethod
    def get_headers():
        return {}

    @staticmethod
    def prepare_model(model):
        return model

    @abc.abstractmethod
    def find_parts(self, iter_parts):
        pass
