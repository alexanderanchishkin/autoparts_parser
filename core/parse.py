import datetime
from config import settings
import urllib3

from core.models.parsers.autopiter import AutoPiter
from core.models.parsers.avd_motors import AvdMotors
from core.models.parsers.froza import Froza
from core.models.parsers.mparts import Mparts
from core.models.parsers.parterra import Parterra

from core.io.xlsx.utilities.merge import merge_files
from core.io.xlsx.part import read_parts_iter
from core.io.database.utilities.table import create_tables

from core.utilities import proxy

from multiprocessing.dummy import Pool as ThreadPool


def parse(xlsx_name, filename):
    proxy.load()
    init_time()

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    input_xlsx = xlsx_name
    parts, count = read_parts_iter(input_xlsx)
    print(f'founded {count} parts.')

    parsers = [AvdMotors(),
               Froza(),
               AutoPiter(),
               Mparts(),
               Parterra()]

    create_tables(settings.time_moment_db_table_prefix, parsers)

    p = ThreadPool(len(parsers))
    p.map(lambda par: par.find_parts(parts), parsers)

    print('start merging...')
    out_name = filename.split('.')[0].replace(' ', '_').replace(':', '_')
    tables = [parser.OUTPUT_FILE for parser in parsers]
    output_filename = merge_files(tables, out_name)

    print('finish')
    return output_filename


def init_time():
    now = datetime.datetime.now()

    settings.time_moment_date = now
    settings.time_moment = now.strftime("%d.%m.%Y %H:%M:%S")
    settings.time_moment_name = now.strftime("%Y%m%d_%H%M%S")
    settings.time_moment_db_table_prefix = now.strftime("%Y%m%d__%H%M%S__")
