import datetime
import os
import time


def main():
    _init()

    while True:
        if _check_time():
            _start_parse_schedule()

        time.sleep(60)


def _init():
    if os.path.isfile('pipefile'):
        os.remove('pipefile')


def _check_time():
    now = datetime.datetime.now()
    return (now.hour == 10 or now.hour == 18) and now.minute < 1


def _start_parse_schedule():
    # TODO: start parse schedule
    pass


if __name__ == '__main__':
    main()
