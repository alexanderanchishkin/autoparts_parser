import os
import settings
import shutil
import stat

from flask import redirect


def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)


from multiprocessing.dummy import DummyProcess

from backend.parser.parse import parse
from flask import current_app, Flask, render_template, request, send_from_directory

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["UPLOAD_FOLDER"] = 'uploads'

p = None


@app.route('/', methods=['GET'])
def index():
    is_running = settings.is_running
    progress_bar = calculate_progress()
    link = '/results/'
    reports = get_reports()

    return render_template('index.html', link=link, reports=reports, is_running=is_running, progress_bar=progress_bar)


@app.route('/', methods=['POST'])
def make():
    global p

    if request.form.get('stop_button'):
        settings.is_running = False
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
    filename = f.filename
    f.save(os.path.join(folder, filename))

    if p and p.is_alive():
        return redirect('/')

    xlsx_name = os.path.join(os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER']), filename)
    p = DummyProcess(target=run_process, args=(xlsx_name, filename))
    p.start()

    return redirect('/')


@app.route('/results/<path:path>')
def download_report(path):
    return send_from_directory('results', path)


def run_process(xlsx_name, filename):
    try:
        print('start process')
        settings.progress_list = []
        settings.is_running = True
        return parse(xlsx_name, filename)
    except:
        return 'error'
    finally:
        print('finish process')
        settings.is_running = False


def calculate_progress():
    if not settings.progress_list:
        return 0

    return round(100 * sum(settings.progress_list) / len(settings.progress_list), 2)


def get_reports():
    return [name for name in os.listdir('results') if os.path.isfile(os.path.join('results', name))][::-1][:20]
