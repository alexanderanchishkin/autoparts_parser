import datetime
import os
import shutil
import stat

import flask

from config import settings
from core.utilities import value

from process import process
from web.utilities import progress as progress_
from web.utilities import reports as reports_

app = flask.Flask(__name__)

p = None


@app.route('/', methods=['GET'])
def index():
    is_running = settings.is_running
    is_terminating = settings.is_terminating
    working_file = settings.working_file

    progress_bar = progress_.calculate_progress()
    progresses = progress_.get_progresses()

    link = settings.RESULTS_FOLDER_NAME
    reports = reports_.get_reports()
    default_start_date = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    default_end_date = datetime.datetime.now().strftime("%Y-%m-%d")

    if process.get_current_process() == 'schedule':
        is_running = True
        working_file = 'Идёт парсинг по расписанию'
        progress_bar_string = process.read_pipefile('schedule')
        progress_bar = float(progress_bar_string) if value.float_try_parse(progress_bar_string) else None

    return flask.render_template('index.html', link=link, reports=reports,
                                 default_start_date=default_start_date, default_end_date=default_end_date,
                                 is_running=is_running, progress_bar=progress_bar,
                                 is_terminating=is_terminating, working_file=working_file, progresses=progresses)


@app.route('/', methods=['POST'])
def make():
    global p

    if flask.request.form.get('stop_button'):
        settings.is_terminating = True
        return flask.redirect('/')

    folder = settings.UPLOAD_FOLDER

    if flask.request.form.get('schedule_button'):
        f = flask.request.files['schedule_file']

        if not f:
            return flask.redirect('/')

        filename = 'input.xlsx'
        filepath = os.path.join(folder, filename)
        if os.path.isfile(filepath):
            os.remove(filepath)
        f.save(filepath)
        return flask.redirect('/')

    if flask.request.form.get('report_button'):
        start_date = flask.request.form.get('start_date')
        end_date = flask.request.form.get('end_date')
        if start_date and end_date:
            process.run(None, None, 'report', start_date, end_date)
        return flask.redirect('/')

    if not os.path.exists(folder):
        os.makedirs(folder)

    out_folder = os.path.join(flask.current_app.root_path, 'files/results')
    temp_folder = os.path.join(out_folder, 'tmp')

    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    def remove_readonly(func, path):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder, onerror=remove_readonly)
        os.makedirs(temp_folder)

    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    f = flask.request.files['file']

    if not f:
        return flask.redirect('/')

    filename = f.filename
    f.save(os.path.join(folder, filename))

    if p and p.is_alive():
        return flask.redirect('/')

    xlsx_name = os.path.join(settings.UPLOAD_FOLDER, filename)

    if flask.request.form.get('add_checkbox'):
        DummyProcess(target=process.run, args=(xlsx_name, filename, 'add')).start()

    if flask.request.form.get('parse_checkbox'):
        p = DummyProcess(target=process.run, args=(xlsx_name, filename))
        p.start()

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
