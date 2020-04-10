import abc
import traceback

from config import settings
from core.io.database.utilities import part as part_
from core.io.xlsx import part
from core.utilities import parser as parser_
from core.utilities import proxy as proxy_
from core.utilities import stopwatch


class Parser(abc.ABC):
    BUFFER_SIZE = 100
    OUTPUT_FILE = None

    def __init__(self):
        self.table_prefix = settings.time_moment_db_table_prefix
        self.table_name = self.table_prefix + parser_.get_output_filename(self).split('.')[0]

        self.current_proxies = None
        self.proxies = []
        self.proxy_index = 0

        self.done = 0
        self.total = 0

    def get_next_proxies(self):
        proxy = proxy_.prepare_proxy(self.proxies[self.proxy_index])
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy

    @stopwatch.time('Parser')
    def execute(self, iter_parts, count):
        if not iter_parts:
            return False

        self.total = count
        self.initialize()

        ready_parts = self.find_parts(iter_parts)
        return ready_parts

    def initialize(self):
        self.done = 0
        self.proxies = proxy_.load()

    def save_result(self, ready_parts):
        if settings.DEBUG:
            print(f'{self.__class__.__name__}: Начинаем запись в таблицу')

        try:
            part_.write_parts(self.table_name, ready_parts)
        except:
            traceback.print_exc()

        try:
            pass
            # TODO: excel
            # part_.write_parts_to_xlsx(self.OUTPUT_FILE, self.OUTPUT_TABLE, ready_parts, settings.time_moment)
        except:
            traceback.print_exc()

        if settings.DEBUG:
            print(f'{self.__class__.__name__}: Детали сохранены')

    @abc.abstractmethod
    def find_parts(self, parts):
        pass

    @abc.abstractmethod
    def prepare_model(self, model):
        pass
