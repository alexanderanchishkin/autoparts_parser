import datetime
import settings
import sys
import threading
import urllib3

from backend.parser.parsers.autopiter import AutoPiter
from backend.parser.parsers.avd_motors import AvdMotors
from backend.parser.parsers.froza import Froza

from backend.parser.parts.parts_explorer import read_parts_from_xlsx
from backend.parser.parts.parts_database import add_parts

from backend.parser.parts.part import Part

from multiprocessing.dummy import Pool as ThreadPool


def add(xlsx_name, filename):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    input_xlsx = xlsx_name

    parts = read_parts_from_xlsx(input_xlsx)
    print(f'founded {len(parts)} parts for adding.')
    add_parts(parts)
    print('finish add')
    return True
