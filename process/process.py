import multiprocessing
import os

from config import settings
from core import add
from core import parse
from core import report


def start(process, xlsx_name=None, filename=None, start_date=None, end_date=None):
    multiprocessing.Process(target=_run, args=(process, xlsx_name, filename, start_date, end_date))


def _run(process, xlsx_name=None, filename=None, start_date=None, end_date=None):
    print(f'start process {process}')

    if process == 'add':
        add.add(xlsx_name)
    if process == 'report':
        report.report(start_date, end_date)
    if process == 'parse':
        with open('pipefile2', 'w') as f:
            pass
        parse.parse(xlsx_name, filename)

    if os.path.isfile('pipefile2'):
        os.remove('pipefile2')

    print(f'finish process {process}')


def get_current_processes():
    pipefiles_directory = settings.INTER_PROCESS_DIRECTORY
    processes = settings.PROCESSES

    pipefiles = [os.path.join(pipefiles_directory, process) for process in processes]
    exists_pipefiles = [pipefile for pipefile in pipefiles if os.path.isfile(pipefile)]

    if not exists_pipefiles:
        return []

    if len(exists_pipefiles) > 1:
        print('Несколько процессов одновременно: ', ', '.join(exists_pipefiles))

    return exists_pipefiles


def read_pipefile(filename):
    pipefiles_directory = settings.INTER_PROCESS_DIRECTORY
    pipefile = os.path.join(pipefiles_directory, filename)
    with open(pipefile, 'r') as f:
        return f.read()

def get_working_file():
    working_files_directory = settings.WORKING_FILES_DIRECTORY
