import datetime

from config import settings


def init_time():
    now = datetime.datetime.now()

    settings.time_moment_date = now
    settings.time_moment = now.strftime("%d.%m.%Y %H:%M:%S")
    settings.time_moment_name = now.strftime("%Y%m%d_%H%M%S")
    settings.time_moment_db_table_prefix = now.strftime("%Y%m%d__%H%M%S__")