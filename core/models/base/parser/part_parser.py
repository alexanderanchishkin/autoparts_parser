import abc
import re
import requests
from config import settings
import time
import traceback

from core.io.database.utilities.part import write_parts
from core.models.base.parser import parser
from core.models.part import Part

from multiprocessing import dummy as thread


class PartParser(parser.Parser, abc.ABC):
    MULTI_REQUEST = False
    THREADS_COUNT = 0

    def find_parts(self, parts):
        try:
            self.get_part_html(parts[0])
        except requests.exceptions.ProxyError:
            settings.progress_list[self.id] = 1
            return False

        parts_chunks = (parts[i:i + min(len(parts), self.BUFFER_SIZE)] for i in range(0, len(parts), self.BUFFER_SIZE))
        for parts_chunk in parts_chunks:
            if settings.is_terminating:
                print('Terminating...')
                break

            if self.MULTI_REQUEST:
                p = thread.Pool(self.THREADS_COUNT)
                ready_parts_array = list(p.map(self.find_one_part, parts_chunk))
            else:
                ready_parts_array = [self.find_one_part(part) for part in parts_chunk]
            ready_parts = {part.number: part for part in ready_parts_array}
            print('Saving...')

            if settings.is_terminating:
                print('Terminating...')
                break

            self.save_result(ready_parts)

    @abc.abstractmethod
    def find_one_part(self, part):
        pass
