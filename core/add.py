import urllib3

from core.parts.parts_explorer import read_parts_from_xlsx
from core.parts.parts_database import add_parts


def add(xlsx_name):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    input_xlsx = xlsx_name

    parts = read_parts_from_xlsx(input_xlsx)
    add_parts(parts)
    return True
