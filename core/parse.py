import datetime
from multiprocessing import dummy as thread
import urllib3

from config import settings
from core.io import xlsx
from core.io.database.utilities import table as table_
from core.models import parsers as parsers_
from core.utilities import proxy


def parse(xlsx_name, filename):
    init()

    parts, count = xlsx.part.read_parts_iter(xlsx_name)
    print(f'founded {count} parts.')

    parsers = load_parsers()
    run_parsers(parsers, parts)
    output_filename = finalize_parts(filename, parsers)

    return output_filename


def init():
    proxy.load()
    init_time()

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def init_time():
    now = datetime.datetime.now()

    settings.time_moment_date = now
    settings.time_moment = now.strftime("%d.%m.%Y %H:%M:%S")
    settings.time_moment_name = now.strftime("%Y%m%d_%H%M%S")
    settings.time_moment_db_table_prefix = now.strftime("%Y%m%d__%H%M%S__")


def load_parsers():
    return [
        parsers_.autopiter.AutoPiter(),
        parsers_.avd_motors.AvdMotors(),
        parsers_.froza.Froza(),
        parsers_.mparts.Mparts(),
        parsers_.parterra.Parterra()
    ]


def run_parsers(parsers, parts):
    table_.create_tables(settings.time_moment_db_table_prefix, parsers)

    p = thread.Pool(len(parsers))
    p.map(run(parts), parsers)


def finalize_parts(filename, parsers):
    print('start merging...')

    out_name = filename.split('.')[0].replace(' ', '_').replace(':', '_')
    tables = [parser.OUTPUT_FILE for parser in parsers]
    output_filename = xlsx.merge.merge_files(tables, out_name)

    print('finish')

    return output_filename


def run(parts):
    def run_parser(parser):
        parser.find_parts(parts)
    return run_parser
