import datetime
import os

import flask

from config import settings
from web.utilities import buttons
from web.utilities import reports as reports_
from process import process as process_
from process.utilities import progress as progress_
from process.utilities import schedule as schedule_

app = flask.Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    is_running = bool(process_.get_current_processes())
    is_terminating = 'stop' in process_.get_current_processes()
    working_file = process_.get_working_file()

    progress_bar = progress_.calculate_progress()
    progresses = progress_.get_progresses()

    link = settings.RESULTS_FOLDER_NAME
    reports = reports_.get_reports()
    default_start_date = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    default_end_date = datetime.datetime.now().strftime("%Y-%m-%d")

    is_schedule = schedule_.check_process()
    if is_schedule:
        working_file = 'Идёт парсинг по расписанию'

    return flask.render_template('index.html', link=link, reports=reports,
                                 default_start_date=default_start_date, default_end_date=default_end_date,
                                 is_running=is_running, progress_bar=progress_bar,
                                 is_terminating=is_terminating, working_file=working_file, progresses=progresses)


@app.route('/', methods=['POST'])
def make():
    buttons.check_buttons()
    return flask.redirect('/')


@app.route('/results/<path:path>')
def download_report(path):
    return flask.send_from_directory(os.path.join('..', settings.RESULTS_FOLDER), path)


@app.route('/uploads/<path:path>')
def download_upload(path):
    return flask.send_from_directory(os.path.join('..', settings.UPLOAD_FOLDER), path)


@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r
