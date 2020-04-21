import datetime
import os
import time

from config import settings
from process import process as process_


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
    xlsx_name = settings.SCHEDULE_FILEPATH
    process_.start('schedule', xlsx_name, 'по расписанию')


if __name__ == '__main__':
    main()
