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

            p = thread.Pool(self.THREADS_COUNT)
            ready_parts = p.map(self.try_find_one_part, parts_chunk)

            try:
                self.save_result(ready_parts)
            except:
                print(f'{self.__class__.__name__}: not saved db')
                pass

    def try_find_one_part(self, part):
        start_time = time.time()
        try:
            ready_part = self.find_one_part(part)
            return ready_part
        except:
            import traceback
            traceback.print_exc()
            return part.not_found()
        finally:
            self.handle_part(start_time)
            try:
                self.print_progress()
            except:
                pass

    def handle_part(self, start_time):
        self.done += 1

        if self.done == self.total:
            return

        end_time = time.time()
        time.sleep(parser_utilities.get_remains_delay(self.DELAY, start_time, end_time))

    @abc.abstractmethod
    def find_one_part(self, part):
        pass
