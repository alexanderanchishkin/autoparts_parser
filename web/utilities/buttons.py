import os
import shutil
import stat
import sys

import flask

from config import settings
from process import process as process_
from web.utilities import checkboxes


def check_buttons():
    [check_button(process) for process in settings.PROCESSES]


def check_button(process):
    button_name = process + '_button'

    if flask.request.form.get(button_name):
        button_function_name = f'_{process}_button'

        button_function = getattr(sys.modules[__name__], button_function_name, None)

        if button_function is None:
            return

        button_function()


def _stop_button():
    settings.is_terminating = True


def _schedule_button():
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
        process_.start('report', start_date=start_date, end_date=end_date)


def _parse_button():
    if process_.get_current_processes():
        return

    parse_file = flask.request.files['file']

    if not parse_file:
        return

    _check_folders()

    parse_file.save(os.path.join(settings.UPLOAD_FOLDER, parse_file.filename))
    xlsx_name = os.path.join(settings.UPLOAD_FOLDER, parse_file.filename)
    checkboxes.check_checkboxes(xlsx_name, parse_file.filename)


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
