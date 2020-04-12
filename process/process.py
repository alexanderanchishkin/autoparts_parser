import multiprocessing
import os
import sys
import time

from config import settings
from core import add
from core import parse
from core import report
from core import schedule


def start(process, xlsx_name=None, filename=None, start_date=None, end_date=None):
    multiprocessing.Process(target=_run, args=(process, xlsx_name, filename, start_date, end_date)).start()


def _run(process, xlsx_name=None, filename=None, start_date=None, end_date=None):
    print(f'start process {process}')

    if get_current_processes():
        time.sleep(10)

    create_working_file(xlsx_name)
    create_pipefile(process)

    if process == 'add':
        add.add(xlsx_name)
    if process == 'parse':
        parse.parse(xlsx_name, filename)
    if process == 'report':
        report.report(start_date, end_date)
    if process == 'schedule':
        schedule.schedule(xlsx_name, filename)

    remove_pipefile(process)
    remove_working_file()

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
    pipefile = _get_pipefile_path(filename)
    with open(pipefile, 'r') as f:
        return f.read()


def create_pipefile(process):
    update_pipefile(process, 0)


def update_pipefile(process, data):
    pipefile = _get_pipefile_path(process)
    with open(pipefile, 'w') as f:
        f.write(str(data))


def remove_pipefile(process):
    pipefile = _get_pipefile_path(process)
    if os.path.isfile(pipefile):
        os.remove(pipefile)


def _get_pipefile_path(filename):
    return os.path.join(settings.INTER_PROCESS_DIRECTORY, filename)


def get_working_file():
    if not os.path.isfile(settings.WORKING_FILE):
        return None

    with open(settings.WORKING_FILE, 'r') as f:
        return f.read()


def create_working_file(xlsx_name):
    if xlsx_name is None:
        return

    if not os.path.isdir(settings.WORKING_FILES_DIRECTORY):
        os.mkdir(settings.WORKING_FILES_DIRECTORY)

    with open(settings.WORKING_FILE, 'w') as f:
        f.write(xlsx_name)


def remove_working_file():
    if get_current_processes():
        return

    if not os.path.isfile(settings.WORKING_FILE):
        return

    os.remove(settings.WORKING_FILE)
