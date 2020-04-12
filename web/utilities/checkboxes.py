import flask

from config import settings
from process import process as process_


def check_checkboxes(xlsx_name, filename):
    [_check_checkbox(process, xlsx_name, filename) for process in settings.PROCESSES]


def _check_checkbox(process, xlsx_name, filename):
    checkbox_name = process + '_checkbox'

    if flask.request.form.get(checkbox_name):
        process_.start(checkbox_name, xlsx_name, filename)
