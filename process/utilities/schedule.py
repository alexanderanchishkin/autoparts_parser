from process import process


def check_process():
    return 'schedule' in process.get_current_processes()
