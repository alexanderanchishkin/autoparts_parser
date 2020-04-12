import abc
import time

from core.models.base.parser import parser as parser_
from core.utilities import part as part_utilities
from core.utilities import parser as parser_utilities

from multiprocessing import dummy as thread


class PartParser(parser_.Parser, abc.ABC):
    def find_parts(self, iter_parts):
        while True:
            with part_utilities.get_next_parts(iter_parts, self.BUFFER_SIZE) as parts_chunk:
                if not parts_chunk:
                    break

                with thread.Pool(len(parts_chunk)) as p:
                    with p.map(self.try_find_one_part, parts_chunk) as ready_parts:
                        self.save_result(ready_parts)

    def try_find_one_part(self, part):
        start_time = time.time()
        with self.find_one_part(part) as ready_part:
            self.handle_part(start_time)
            return ready_part

    def handle_part(self, start_time):
        self.done += 1
        self.print_progress()

        if self.done == self.total:
            return

        end_time = time.time()
        time.sleep(parser_utilities.get_remains_delay(self.DELAY, start_time, end_time))

    @abc.abstractmethod
    def find_one_part(self, part):
        pass
