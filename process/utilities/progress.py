import os

from config import settings


def calculate_progress():
    try:
        lines = get_progresses()
        if not lines:
            return 100

        total = int(lines[0].split('\\')[-1])
        dones = sum([int(line.split()[1].split('\\')[0]) for line in lines])

        return round(100 * dones / (total * len(lines)), 2)
    except:
        return 1


def get_progresses():
    files = get_progresses_from_directory()
    lines = [open(os.path.join(settings.PROGRESS_FOLDER, file), 'r').read() for file in files]
    return lines


def get_progresses_from_directory():
    return os.listdir(settings.PROGRESS_FOLDER)