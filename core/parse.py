from multiprocessing import dummy as thread

from config import settings
from core.io.xlsx import part as part_xlsx
from core.io.xlsx import merge as merge_xlsx
from core.io.database.utilities import table as table_db
from core.models import parsers as parsers_
from core.utilities import time as time_
from core.utilities import warning


def parse(xlsx_name, filename, sql_output=True, source='xlsx'):
    init()

    parts, count = _get_parts_iter(source, xlsx=xlsx_name)
    print(f'founded {count} parts.')

    parsers = load_parsers()
    run_parsers(parsers, parts, count, sql_output)
    output_filename = finalize_parts(filename, parsers)

    return output_filename


def _get_parts_iter(source, **kwargs):
    if source == 'xlsx':
        return part_xlsx.read_parts_iter(kwargs.get('xlsx', None))
    if source == 'sql':
        return None, 0
    return None, 0

def init():
    time_.init_time()
    warning.init_warnings()


def load_parsers():
    return [
        parsers_.autopiter.Autopiter(),
        parsers_.avd_motors.AvdMotors(),
        parsers_.froza.Froza(),
        parsers_.mparts.Mparts(),
        parsers_.parterra.Parterra()
    ]


def run_parsers(parsers, parts, count, sql_output=True):
    if sql_output:
        table_db.create_tables(settings.time_moment_db_table_prefix, parsers)

    p = thread.Pool(len(parsers))
    p.map(run(parts, count), parsers)


def finalize_parts(filename, parsers):
    print('start merging...')

    out_name = filename.split('.')[0].replace(' ', '_').replace(':', '_')
    tables = [parser.OUTPUT_FILE for parser in parsers]
    output_filename = merge_xlsx.merge_files(tables, out_name)

    print('finish')

    return output_filename


def run(parts, count):
    def run_parser(parser):
        parser.execute(parts, count)
    return run_parser
