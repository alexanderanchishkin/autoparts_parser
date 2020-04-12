import abc
import time

from core.models.base.parser import parser as parser_
from core.utilities import part as part_utilities
from core.utilities import parser as parser_utilities

from multiprocessing import dummy as thread


class PartParser(parser_.Parser, abc.ABC):

    def find_parts(self, iter_parts):
        while True:
            parts_chunk = part_utilities.get_next_parts(iter_parts, self.BUFFER_SIZE)

            if not parts_chunk:
                break

            p = thread.Pool(len(parts_chunk))
            ready_parts = p.map(self.try_find_one_part, parts_chunk)
            self.save_result(ready_parts)

    def try_find_one_part(self, part):
        start_time = time.time()
        ready_part = self.find_one_part(part)
        self.handle_part(start_time)
        self.print_progress()
        return ready_part

    def handle_part(self, start_time):
        self.done += 1
        end_time = time.time()
        time.sleep(parser_utilities.get_remains_delay(self.DELAY, start_time, end_time))

    @abc.abstractmethod
    def find_one_part(self, part):
        pass
