from multiprocessing import dummy as thread

from config import settings
from core.io import xlsx
from core.io.database.utilities import table as table_
from core.models import parsers as parsers_
from core.utilities import time as time_
from core.utilities import warning


def parse(xlsx_name, filename):
    init()

    parts, count = xlsx.part.read_parts_iter(xlsx_name)
    print(f'founded {count} parts.')

    parsers = load_parsers()
    run_parsers(parsers, parts, count)
    output_filename = finalize_parts(filename, parsers)

    return output_filename


def init():
    time_.init_time()
    warning.init_warnings()


def load_parsers():
    return [
        parsers_.autopiter.AutoPiter(),
        parsers_.avd_motors.AvdMotors(),
        parsers_.froza.Froza(),
        parsers_.mparts.Mparts(),
        parsers_.parterra.Parterra()
    ]


def run_parsers(parsers, parts, count):
    table_.create_tables(settings.time_moment_db_table_prefix, parsers)

    p = thread.Pool(len(parsers))
    p.map(run(parts, count), parsers)


def finalize_parts(filename, parsers):
    print('start merging...')

    out_name = filename.split('.')[0].replace(' ', '_').replace(':', '_')
    tables = [parser.OUTPUT_FILE for parser in parsers]
    output_filename = xlsx.merge.merge_files(tables, out_name)

    print('finish')

    return output_filename


def run(parts, count):
    def run_parser(parser):
        parser.execute(parts, count)
    return run_parser
