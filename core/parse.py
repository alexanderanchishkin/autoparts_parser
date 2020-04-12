from multiprocessing import dummy as thread

from config import settings
from core.io.xlsx import part as part_xlsx
from core.io.xlsx import merge as merge_xlsx
from core.io.database.utilities import table as table_db
from core.models.parsers import autopiter
from core.models.parsers import avd_motors
from core.models.parsers import froza
from core.models.parsers import mparts
from core.models.parsers import parterra
from core.utilities import time as time_
from core.utilities import warning


def parse(xlsx_name, filename, sql_output=True, source='xlsx'):
    _init()

    _, count = _get_parts_iter(source, xlsx=xlsx_name)
    print(f'founded {count} parts.')

    parsers = load_parsers()
    run_parsers(parsers, sql_output, source, xlsx=xlsx_name)
    output_filename = finalize_parts(filename, parsers)

    return output_filename


def _get_parts_iter(source, **kwargs):
    if source == 'xlsx':
        return part_xlsx.read_parts_iter(kwargs.get('xlsx', None))
    if source == 'sql':
        return None, 0
    return None, 0


def _init():
    time_.init_time()
    warning.init_warnings()


def load_parsers():
    return [
        autopiter.Autopiter(),
        avd_motors.AvdMotors(),
        froza.Froza(),
        mparts.Mparts(),
        parterra.Parterra()
    ]


def run_parsers(parsers, sql_output=True, source=None, xlsx=None):
    if sql_output:
        table_db.create_tables(settings.time_moment_db_table_prefix, parsers)

    p = thread.Pool(len(parsers))
    p.map(_run(source, xlsx=xlsx), parsers)


def finalize_parts(filename, parsers):
    print(f'start merging to {filename}')

    out_name = filename.split('.')[0].replace(' ', '_').replace(':', '_')
    tables = [parser.get_output_filename() for parser in parsers]
    output_filename = merge_xlsx.merge_files(tables, out_name)

    print(f'finish merging {filename}')

    return output_filename


def _run(source, xlsx):
    def run_parser(parser):
        parts, count = _get_parts_iter(source, xlsx=xlsx)
        parser.execute(parts, count)
    return run_parser
