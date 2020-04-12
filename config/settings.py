import os

time_moment_date = None
time_moment = None
time_moment_name = None
time_moment_db_table_prefix = None

CONTENT_FOLDER = 'files'

DEFAULT_PARSER_BUFFER_SIZE = 25
DEFAULT_PARSER_THREADS_COUNT = DEFAULT_PARSER_BUFFER_SIZE
DB_BUFFER_SIZE = 25

RESULTS_FOLDER_NAME = 'results'
RESULTS_FOLDER = os.path.join(CONTENT_FOLDER, RESULTS_FOLDER_NAME)

UPLOAD_FOLDER_NAME = 'uploads'
UPLOAD_FOLDER = os.path.join(CONTENT_FOLDER, UPLOAD_FOLDER_NAME)

TEMP_XLSX_NAME = 'tmp'
TEMP_XLSX_DIRECTORY = os.path.join(RESULTS_FOLDER, TEMP_XLSX_NAME)

SCHEDULE_FILENAME = 'input.xlsx'
SCHEDULE_FILEPATH = os.path.join(UPLOAD_FOLDER, SCHEDULE_FILENAME)

PROCESS_DIRECTORY = 'process'

PROGRESS_FOLDER_NAME = 'parser_progresses'
PROGRESS_FOLDER = os.path.join(PROCESS_DIRECTORY, PROGRESS_FOLDER_NAME)

INTER_PROCESS_DIRECTORY = os.path.join(PROCESS_DIRECTORY, 'process_pipefiles')

WORKING_FILES_DIRECTORY = os.path.join(PROCESS_DIRECTORY, 'working_files')
WORKING_FILENAME = 'working_file'
WORKING_FILE = os.path.join(WORKING_FILES_DIRECTORY, WORKING_FILENAME)

PROCESSES = ['add', 'parse', 'schedule', 'stop', 'report']

PROXY_FILE = os.path.join('config', 'proxies.txt')
