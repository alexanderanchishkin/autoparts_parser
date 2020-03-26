import os
import shutil

def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

from multiprocessing import Process

from backend.parser.parse import parse
from flask import current_app, Flask, render_template, request, send_from_directory

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["UPLOAD_FOLDER"] = 'uploads'


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def make():
    folder = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    out_folder = os.path.join(current_app.root_path, 'results')
    shutil.rmtree(out_folder, onerror=remove_readonly)
    os.makedirs(out_folder)
    f = request.files['file']
    filename = f.filename
    f.save(os.path.join(folder, filename))
    # p = Process(target=parse, args=(os.path.join(os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER']),filename),))
    # p.start()
    # p.join()
    xlsx_name = os.path.join(os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER']), filename)
    output_filename = parse(xlsx_name, filename)
    uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    return send_from_directory(directory=out_folder, filename=output_filename,
                               attachment_filename=output_filename, as_attachment=True)
