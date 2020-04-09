import datetime
import settings
import urllib3

from core.models.parsers.autopiter import AutoPiter
from core.models.parsers.avd_motors import AvdMotors
from core.models.parsers.froza import Froza
from core.models.parsers.mparts import Mparts
from core.models.parsers.parterra import Parterra

from core.parts.parts_explorer import read_parts_from_xlsx, merge_files
from core.parts.parts_database import create_tables, get_all_parts

from multiprocessing.dummy import Pool as ThreadPool


def parse(xlsx_name, filename, sql_mode=False):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    settings.TIME_MOMENT = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    settings.TIME_MOMENT_NAME = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    time_moment_db_table_prefix = datetime.datetime.now().strftime("%Y%m%d__%H%M%S__")

    input_xlsx = xlsx_name

    all_parts = list(get_all_parts())
    settings.articles_dict = {(article.article + article.brand): article.get_id() for article in all_parts}

    if sql_mode:
        parts = all_parts
    else:
        parts = read_parts_from_xlsx(input_xlsx)
    settings.max_parts = len(parts)
    print(f'founded {settings.max_parts} parts.')

    parsers = [AvdMotors(0, sql_mode=True, table_prefix=time_moment_db_table_prefix),
               Froza(1, sql_mode=True, table_prefix=time_moment_db_table_prefix),
               AutoPiter(2, sql_mode=True, table_prefix=time_moment_db_table_prefix),
               Mparts(3, sql_mode=True, table_prefix=time_moment_db_table_prefix),
               Parterra(4, sql_mode=True, table_prefix=time_moment_db_table_prefix)]

    # parsers = [Parterra(0, sql_mode=True, table_prefix=time_moment_db_table_prefix)]

    settings.progress_list = [0] * len(parsers)

    create_tables(time_moment_db_table_prefix, parsers)

    p = ThreadPool(len(parsers))
    ready_parts_array = list(p.map(lambda par: par.find_parts(parts), parsers))

    print('start merging...')
    out_name = filename.split('.')[0].replace(' ', '_').replace(':', '_')
    tables = [parser.OUTPUT_FILE for parser in parsers]
    output_filename = merge_files(tables, out_name)
    print('finish')
    return output_filename
