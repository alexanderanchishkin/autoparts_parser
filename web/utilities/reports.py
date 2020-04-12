import os

from config import settings


def get_reports():
    filenames = get_results_from_directory()
    return list(reversed(sorted(filter(is_result_file_exists, filenames))))[:20]


def get_results_from_directory():
    return os.listdir(settings.RESULTS_FOLDER)


def is_result_file_exists(filename):
    return os.path.isfile(os.path.join(settings.RESULTS_FOLDER, filename))
