from core.utilities import value
from process import process


def check_process():
    if process.get_current_processes() == 'schedule':
        progress_bar_string = process.read_pipefile('schedule')
        progress_bar = float(progress_bar_string) if value.float_try_parse(progress_bar_string) else None
        return True, progress_bar
    return False, None
