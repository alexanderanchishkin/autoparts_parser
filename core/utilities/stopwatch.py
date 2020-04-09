import time as time_


class StopWatch:
    def __init__(self):
        self.start_time = 0
        self.end_time = 0
        self.elapsed_time = 0

    def __enter__(self):
        self.start_time = time_.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time_.time()
        self.elapsed_time = self.end_time - self.start_time


def time(call_name=None):
    def run_time(func):
        def time_it(*args, **kwargs):
            def print_time(elapsed_time):
                time_name = call_name if call_name is not None and not callable(call_name) else func.__name__
                print(f'{time_name} time: {elapsed_time}')

            with StopWatch() as sw:
                result = func(*args, **kwargs)
                print_time(sw.elapsed_time)
                return result

        return time_it

    if callable(call_name):
        return run_time(call_name)

    return run_time
