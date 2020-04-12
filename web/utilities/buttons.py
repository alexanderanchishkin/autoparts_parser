import os
import multiprocessing
import shutil
import stat

import flask

from config import settings
from process import process as process_


def check_buttons():
    buttons = {
        'stop': _stop_button,
        'schedule': _schedule_rewrite_button,
        'report': _report_button,
        'parse': _parse_button
    }

    [check_button(button_name, function) for button_name, function in buttons.items()]


def check_button(button_name, function):
    if flask.request.form.get(button_name + '_button'):
        function()


def _stop_button():
    settings.is_terminating = True


def _schedule_rewrite_button():
    schedule_file = flask.request.files['schedule_file']

    if not schedule_file:
        return

    schedule_filename = settings.SCHEDULE_FILENAME
    schedule_filepath = os.path.join(settings.UPLOAD_FOLDER, schedule_filename)
    if os.path.isfile(schedule_filepath):
        os.remove(schedule_filepath)
    schedule_file.save(schedule_filepath)


def _report_button():
    start_date = flask.request.form.get('start_date')
    end_date = flask.request.form.get('end_date')
    if start_date and end_date:
        multiprocessing.Process(target=process_.run,
                                args=('report',),
                                kwargs={'start_date': start_date, 'end_date': end_date}).start()


def _parse_button():
    _check_folders()

    f = flask.request.files['file']

    if not f:
        return

    filename = f.filename
    f.save(os.path.join(settings.RESULTS_FOLDER, filename))

    if process_.get_current_process() is not None:
        return

    xlsx_name = os.path.join(settings.UPLOAD_FOLDER, filename)

    if flask.request.form.get('add_checkbox'):
        multiprocessing.Process(target=process_.run, args=('add', xlsx_name, filename)).start()

    if flask.request.form.get('parse_checkbox'):
        multiprocessing.Process(target=process_.run, args=('parse', xlsx_name, filename)).start()


def _check_folders():
    if not os.path.exists(settings.UPLOAD_FOLDER):
        os.makedirs(settings.UPLOAD_FOLDER)

    if not os.path.exists(settings.RESULTS_FOLDER):
        os.makedirs(settings.RESULTS_FOLDER)

    if os.path.exists(settings.TEMP_XLSX_DIRECTORY):
        shutil.rmtree(settings.TEMP_XLSX_DIRECTORY, onerror=_remove_readonly)
        os.makedirs(settings.TEMP_XLSX_DIRECTORY)

    if not os.path.exists(settings.TEMP_XLSX_DIRECTORY):
        os.makedirs(settings.TEMP_XLSX_DIRECTORY)


def _remove_readonly(func, path):
    os.chmod(path, stat.S_IWRITE)
    func(path)
