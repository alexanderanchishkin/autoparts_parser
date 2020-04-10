import urllib3

from core.io.xlsx.part import read_parts_iter
from core.io.database.utilities.part import add_parts


def add(xlsx_name):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    input_xlsx = xlsx_name

    parts = read_parts_iter(input_xlsx)
    add_parts(parts)
    return True
