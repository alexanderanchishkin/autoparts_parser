import os
import time
import traceback

import settings
import shutil
import stat

from flask import redirect


def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)


from multiprocessing.dummy import DummyProcess
from backend.parser.parse import parse
from backend.adder.add import add
from backend.reporter.report import report
from flask import current_app, Flask, render_template, request, send_from_directory

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["UPLOAD_FOLDER"] = 'uploads'

p = None


@app.route('/', methods=['GET'])
def index():
    is_running = settings.is_running
    is_terminating = settings.is_terminating
    working_file = settings.working_file
    progress_bar = calculate_progress()
    link = '/results/'
    reports = get_reports()

    return render_template('index.html', link=link, reports=reports,
                           is_running=is_running, progress_bar=progress_bar,
                           is_terminating=is_terminating, working_file=working_file)


@app.route('/', methods=['POST'])
def make():
    global p

    if request.form.get('stop_button'):
        settings.is_terminating = True
        return redirect('/')

    if request.form.get('report_button'):
        start_date = '2020-04-01'
        end_date = '2020-04-01'
        run_process(None, None, 'report', start_date, end_date)
        return redirect('/')

    folder = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    if not os.path.exists(folder):
        os.makedirs(folder)

    out_folder = os.path.join(current_app.root_path, 'results')
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
    return send_from_directory('results', path)


def run_process(xlsx_name, filename, process='parse', start_date='', end_date=''):
    try:
        print(f'start process {process}')
        settings.progress_list = []
        settings.working_file = filename

        while settings.is_running:
            time.sleep(1)

        settings.is_running = True

        if process == 'add':
            return add(xlsx_name, filename)
        if process == 'report':
            return report(start_date, end_date)
        if process == 'parse':
            return parse(xlsx_name, filename)
        return 'Nothing'
    except Exception:
        print('Произошла ошибка: ', traceback.print_exc())
        return 'error'
    finally:
        print('finish process')
        settings.is_running = False
        settings.is_terminating = False


def calculate_progress():
    if not settings.progress_list:
        return 0

    return round(100 * sum(settings.progress_list) / len(settings.progress_list), 2)


def get_reports():
    return [name for name in os.listdir('results') if os.path.isfile(os.path.join('results', name))][::-1][:20]
