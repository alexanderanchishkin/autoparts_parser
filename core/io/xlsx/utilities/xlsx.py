import openpyxl
import os.path

from config import settings


def start_write_xlsx(header_rows=None, table_name='Отчёт'):
    wb = openpyxl.Workbook(write_only=True)
    ws = wb.create_sheet(table_name)

    if header_rows is None:
        return wb

    if not header_rows:
        return wb

    if isinstance(header_rows[0], str):
        header_rows = [header_rows]

    [ws.append(row) for row in header_rows]

    return wb


def add_rows_xlsx(ws, rows):
    [ws.append(row) for row in rows]


def get_column_by_index(index):
    excel_column = str()
    div = index
    while div:
        (div, mod) = divmod(div - 1, 26)
        excel_column = chr(mod + 65) + excel_column

    return excel_column


def save_time_xlsx(wb, out_name):
    output_filename = f"{settings.time_moment_name}_{out_name}.xlsx"
    output_path = os.path.join(settings.RESULTS_FOLDER, output_filename)

    wb.save(output_path)
