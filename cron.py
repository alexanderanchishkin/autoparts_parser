import os
import shutil
import stat

from multiprocessing.dummy import DummyProcess

import settings
import time
import traceback

from backend.parser.parse import parse
from backend.adder.add import add


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

        add(xlsx_name, filename)
        if process == 'parse':
            return parse(xlsx_name, filename)
        return 'Nothing'
    except Exception:
        print('Произошла ошибка: ', traceback.print_exc())
        return 'error'
    finally:
        print('finish process')
        settings.is_running = False
        settings.is_terminating = False


if __name__ == '__main__':
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
        with open('pipefile', 'w') as f:
            f.write('0')

        directory = os.path.join('uploads', 'input.xlsx')
        p = DummyProcess(target=run_process, args=(directory, 'по_расписанию'))
        p.start()
        settings.is_running = True
        while settings.is_running:
            time.sleep(5)
            with open('pipefile', 'w') as f:
                f.write(str(calculate_progress()))

    except:
        print('Произошла ошибка: ', traceback.print_exc())
        print('error')
    finally:
        os.remove('pipefile')