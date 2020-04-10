import datetime
import os
import time
import traceback

from config import settings
import shutil
import stat

from flask import redirect


def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)


from multiprocessing.dummy import DummyProcess
from core.parse import parse
from core.add import add
from core.report import report
from flask import current_app, Flask, render_template, request, send_from_directory, send_file

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["CONTENT_FOLDER"] = 'files'

app.config["UPLOAD_FOLDER_NAME"] = 'uploads'
app.config["UPLOAD_FOLDER"] = os.path.join(app.config["CONTENT_FOLDER"], app.config['UPLOAD_FOLDER_NAME'])

app.config["RESULTS_FOLDER_NAME"] = 'results'
app.config["RESULTS_FOLDER"] = os.path.join(app.config["CONTENT_FOLDER"], app.config['RESULTS_FOLDER_NAME'])

p = None


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


@app.route('/', methods=['GET'])
def index():
    is_running = settings.is_running
    is_terminating = settings.is_terminating
    working_file = settings.working_file
    progress_bar = calculate_progress()

    progresses = get_progresses()

    link = app.config['RESULTS_FOLDER_NAME']
    reports = get_reports()
    default_start_date = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    default_end_date = datetime.datetime.now().strftime("%Y-%m-%d")

    if os.path.isfile('pipefile'):
        is_running = True
        working_file = 'Идёт парсинг по расписанию'
        with open('pipefile', 'r') as f:
            try:
                progress_bar = float(f.read())
            except:
                traceback.print_exc()
                progress_bar = 50

    return render_template('index.html', link=link, reports=reports,
                           default_start_date=default_start_date, default_end_date=default_end_date,
                           is_running=is_running, progress_bar=progress_bar,
                           is_terminating=is_terminating, working_file=working_file, progresses=progresses)


@app.route('/', methods=['POST'])
def make():
    global p

    if request.form.get('stop_button'):
        settings.is_terminating = True
        return redirect('/')

    folder = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])

    if request.form.get('schedule_button'):
        f = request.files['schedule_file']

        if not f:
            return redirect('/')

        filename = 'input.xlsx'
        filepath = os.path.join(folder, filename)
        if os.path.isfile(filepath):
            os.remove(filepath)
        f.save(filepath)
        return redirect('/')

    if request.form.get('report_button'):
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        if start_date and end_date:
            run_process(None, None, 'report', start_date, end_date)
        return redirect('/')

    if not os.path.exists(folder):
        os.makedirs(folder)

    out_folder = os.path.join(current_app.root_path, 'files/results')
    temp_folder = os.path.join(out_folder, 'tmp')

    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder, onerror=remove_readonly)
        os.makedirs(temp_folder)

    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    f = request.files['file']

    if not f:
        return redirect('/')

    filename = f.filename
    f.save(os.path.join(folder, filename))

    if p and p.is_alive():
        return redirect('/')

    xlsx_name = os.path.join(os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER']), filename)

    if request.form.get('add_checkbox'):
        DummyProcess(target=run_process, args=(xlsx_name, filename, 'add')).start()

    if request.form.get('parse_checkbox'):
        p = DummyProcess(target=run_process, args=(xlsx_name, filename))
        p.start()

    return redirect('/')


@app.route('/results/<path:path>')
def download_report(path):
    return send_from_directory(os.path.join('..', app.config['RESULTS_FOLDER']), path)


@app.route('/uploads/<path:path>')
def download_upload(path):
    return send_from_directory(os.path.join('..', app.config['UPLOAD_FOLDER']), path)


def run_process(xlsx_name, filename, process='parse', start_date='', end_date=''):
    try:
        print(f'start process {process}')
        settings.progress_list = []
        settings.working_file = filename

        while settings.is_running:
            time.sleep(1)

        settings.is_running = True

        if process == 'add':
            return add(xlsx_name)
        if process == 'report':
            return report(start_date, end_date)
        if process == 'parse':
            with open('pipefile2', 'w') as f:
                pass
            return parse(xlsx_name, filename)
        return 'Nothing'
    except Exception:
        print('Произошла ошибка: ', traceback.print_exc())
        return 'error'
    finally:
        print('finish process')
        settings.is_running = False
        settings.is_terminating = False
        if os.path.isfile('pipefile2'):
            os.remove('pipefile2')


def calculate_progress():
    if not settings.progress_list:
        return 0

    return round(100 * sum(settings.progress_list) / len(settings.progress_list), 2)


def get_progresses():
    if not settings.progress_list:
        return []

    targets = ['АВД Моторс', 'Фроза', 'Автопитер', 'МПартс', 'Партерра']
    targets_progress_list = zip(targets, settings.progress_list)
    return [f'{target[0]}: {round(target[1] * settings.max_parts)}\\{settings.max_parts}'
            for target in targets_progress_list]


def get_reports():
    filenames = get_results_from_directory()
    return list(reversed(sorted(filter(is_result_file_exists, filenames))))[:20]


def get_results_from_directory():
    return os.listdir(app.config['RESULTS_FOLDER'])


def is_result_file_exists(filename):
    return os.path.isfile(os.path.join(app.config['RESULTS_FOLDER'], filename))
