import os
import shutil
import stat

from config import settings
import traceback

from core import parse
from core import add


def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def calculate_progress():
    if not settings.progress_list:
        return 0

    return round(100 * sum(settings.progress_list) / len(settings.progress_list), 2)


def run_process(xlsx_name, filename, process='parse', start_date='', end_date=''):
    try:
        print(f'start process {process}')
        settings.progress_list = []
        settings.working_file = filename

        settings.is_running = True

        add.add(xlsx_name)
        if process == 'parse':
            return parse.parse(xlsx_name, filename)
        return 'Nothing'
    except Exception:
        print('Произошла ошибка: ', traceback.print_exc())
        return 'error'
    finally:
        print('finish process')
        settings.is_running = False
        settings.is_terminating = False


def main():
    out_folder = 'results'
    temp_folder = os.path.join(out_folder, 'tmp')

    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder, onerror=remove_readonly)
        os.makedirs(temp_folder)

    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    try:
        directory = os.path.join('uploads', 'input.xlsx')
        run_process(directory, 'тест')

    except:
        print('Произошла ошибка: ', traceback.print_exc())
        print('error')
    finally:
        if os.path.isfile('pipefile'):
            os.remove('pipefile')


from core.utilities import stopwatch

var = 0


class TestClass:
    @stopwatch.time(__qualname__)
    def test(self, a):
        for _ in range(1, 100000):
            a += 1

class TestMore(TestClass):
    pass

if __name__ == '__main__':
    TestMore().test(0)
    exit()
    main()
