from openpyxl import load_workbook

from config import settings
from core.io.xlsx.utilities import xlsx
from core.models import part as part_
from core.utilities import value


def read_parts_iter(xlsx_file):
    wb = load_workbook(xlsx_file, read_only=True)
    ws = wb.worksheets[0]

    start_row = 2 if not ws[1][0].value or value.has_cyrillic(ws[1][0].value) else 1

    iter_parts = \
        (part_.Part(_prepare_part_number(row[0].value), row[1].value)
         for row in ws.iter_rows(start_row, ws.max_row, 1, 3) if row[0].value and row[1].value)

    parts_count = ws.max_row - start_row
    return iter_parts, parts_count


def start_write_parts(time_moment):
    headers = ['Артикул', 'Бренд', 'Наименование', time_moment]
    return xlsx.start_write_xlsx(headers)


def save_temp_parts(wb, out_name):
    xlsx_file_path = settings.TEMP_XLSX_DIRECTORY + out_name
    xlsx.save_time_xlsx(wb, xlsx_file_path)


def write_parts_to_xlsx(ws, parts: list):
    rows = (_get_row_from_part(part) for part in parts)
    xlsx.add_rows_xlsx(ws, rows)


def _get_row_from_part(part):
    return [str(part.number), part.model, part.title, part.price]


def _prepare_part_number(number):
    return number.split('#')[0]
