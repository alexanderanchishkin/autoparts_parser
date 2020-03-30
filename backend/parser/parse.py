import datetime
import settings
import sys
import threading
import urllib3

from backend.parser.parsers.autopiter import AutoPiter
from backend.parser.parsers.avd_motors import AvdMotors
from backend.parser.parsers.froza import Froza

from backend.parser.parts.parts_explorer import read_parts_from_xlsx, merge_files

from backend.parser.parts.part import Part

from multiprocessing.dummy import Pool as ThreadPool


def parse(xlsx_name, filename):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    settings.TIME_MOMENT = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    settings.TIME_MOMENT_NAME = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    input_xlsx = xlsx_name

    parts = read_parts_from_xlsx(input_xlsx)
    print(f'founded {len(parts)} parts.')

    parsers = [AvdMotors(0), Froza(1), AutoPiter(2)]
    settings.progress_list = [0] * len(parsers)

    p = ThreadPool(3)
    ready_parts_array = list(p.map(lambda par: par.find_parts(parts), parsers))

    print('start merging...')
    out_name = filename.split('.')[0].replace(' ', '_').replace(':', '_')
    output_filename = merge_files(['autopiter.xlsx', 'avd_motors.xlsx', 'froza.xlsx'], out_name)
    print('finish')
    return output_filename
