import abc
import re
import requests
from config import settings
import time
import traceback

from core.io.database.utilities.part import write_parts
from core.models.base.parser import parser
from core.models import part as part_

from core.utilities import parser as parser_

from multiprocessing import dummy as thread


class PartParser(parser.Parser, abc.ABC):
    MULTI_REQUEST = False
    THREADS_COUNT = 0

    def find_parts(self, iter_parts):
        # TODO: Realize
        pass

    def try_find_part(self, part):
        start_time = time.time()
        try:
            ready_part = self.find_one_part(part)

            if not settings.DEBUG:
                print(f"{self.__class__.__name__}: {self.done}\\{self.total}\n", end='')
            return ready_part
        except Exception as e:
            return part_.Part(part.number, part.model, 'Нет в наличии', 'Нет в наличии')
        finally:
            self.handle_part(start_time)

    def handle_part(self, start_time):
        self.done += 1
        end_time = time.time()
        time.sleep(parser_.get_remains_delay(self.DELAY, start_time, end_time))

    @abc.abstractmethod
    def find_one_part(self, part):
        pass
