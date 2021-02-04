from config import settings
from process import process as process_


def main():
    xlsx_name = settings.SCHEDULE_FILEPATH
    process_.start('parse', xlsx_name, 'по расписанию')


if __name__ == '__main__':
    main()
