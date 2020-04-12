import flask

from process import process as process_


def check_checkboxes(xlsx_name, filename):
    checkboxes = ['add', 'parse']

    [_check_checkbox(checkbox_name, xlsx_name, filename) for checkbox_name in checkboxes]


def _check_checkbox(checkbox_name, xlsx_name, filename):
    if flask.request.form.get(checkbox_name + '_checkbox'):
        process_.start(checkbox_name, xlsx_name, filename)
