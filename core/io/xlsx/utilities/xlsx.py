import openpyxl
import os.path

from config import settings


def start_write_xlsx(header_rows=None):
    wb = openpyxl.Workbook(write_only=True)
    ws = wb.create_sheet('Отчёт')

    if header_rows is None:
        return wb

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
