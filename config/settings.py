import os

DEBUG = 0

time_moment_date = None
time_moment = None
time_moment_name = None
time_moment_db_table_prefix = None

CONTENT_FOLDER = 'files'

RESULTS_FOLDER_NAME = 'results'
RESULTS_FOLDER = os.path.join(CONTENT_FOLDER, RESULTS_FOLDER_NAME)

TEMP_XLSX_NAME = 'tmp'
TEMP_XLSX_DIRECTORY = os.path.join(RESULTS_FOLDER, TEMP_XLSX_NAME)

is_running = False
is_terminating = False

working_file = None
