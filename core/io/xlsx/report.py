from core.io.xlsx.utilities import xlsx


def start_report():
    headers = ['Артикул', 'Бренд', 'Минимум', '', 'Средняя', 'Максимум', '']
    sub_headers = ['', '', 'Цена', 'Магазин', '', 'Цена', 'Магазин']

    return xlsx.start_write_xlsx([headers, sub_headers])


def save_report(wb, out_name):
    xlsx.save_time_xlsx(wb, out_name)


def write_report_parts(ws, parts: list):
    rows = (_get_report_row_from_part(part) for part in parts if 'article' in part)
    xlsx.add_rows_xlsx(ws, rows)


def _get_report_row_from_part(part):
    return [part['article'], part['brand'],
            part['min_price'], part['min_shop'],
            part['avg_price'],
            part['max_price'], part['max_shop']]
