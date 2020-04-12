import os
import time

from config import settings
from core import add
from core import parse
from core import report


def run(xlsx_name, filename, process='parse', start_date='', end_date=''):
    try:
        print(f'start process {process}')
        settings.progress_list = []
        settings.working_file = filename

        while settings.is_running:
            time.sleep(1)

        settings.is_running = True

        if process == 'add':
            return add.add(xlsx_name)
        if process == 'report':
            return report.report(start_date, end_date)
        if process == 'parse':
            with open('pipefile2', 'w') as f:
                pass
            return parse.parse(xlsx_name, filename)
        return 'Nothing'
    finally:
        print('finish process')
        settings.is_running = False
        settings.is_terminating = False
        if os.path.isfile('pipefile2'):
            os.remove('pipefile2')


def get_current_process():
    pipefiles_directory = settings.INTER_PROCESS_DIRECTORY
    processes = settings.PROCESSES

    pipefiles = [os.path.join(pipefiles_directory, process) for process in processes]
    exists_pipefiles = [pipefile for pipefile in pipefiles if os.path.isfile(pipefile)]

    if not exists_pipefiles:
        return None

    if len(exists_pipefiles) > 1:
        print('Несколько процессов одновременно: ', ', '.join(exists_pipefiles))
        return exists_pipefiles[0]

    return exists_pipefiles[0]


def read_pipefile(filename):
    pipefiles_directory = settings.INTER_PROCESS_DIRECTORY
    pipefile = os.path.join(pipefiles_directory, filename)
    with open(pipefile, 'r') as f:
        return f.read()
