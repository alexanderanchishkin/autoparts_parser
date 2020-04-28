import datetime

from config import settings

from core.io.database.utilities import database
from core.io.database.utilities import part as part_db
from core.io.database.utilities import report as report_db
from core.io.xlsx import report as report_
from core.utilities import time as time_


def report(start_date, end_date):
    time_.init_time()
    parts = part_db.get_all_parts()

    out_name = f"Отчёт_{start_date.replace('-', '')}_{end_date.replace('-', '')}"

    wb = report_.start_report()

    # TODO: !!!!!!
    articles = {part.get_id(): (part.article, part.brand) for part in parts}
    parts = database.get_tuples_tables(start_date, end_date)
    statistics = filter_parts_by_id(parts, full_statistics)

    [one_statistics.update({'article': articles[part_id][0], 'brand': articles[part_id][1]})
     for part_id, one_statistics in statistics.items() if part_id in articles]

    try:
        # report_db.write_report(statistics.values())
        pass
    except:
        print('Не получилось...')
        import traceback
        traceback.print_exc()

    report_.write_report_parts(wb.active, statistics.values())
    report_.save_report(wb, out_name)


def full_statistics(array):
    min_price, min_shop = min(array)
    max_price, max_shop = max(array)
    avg_price = avg_tuples_round_2(array)
    return {'min_price': min_price,
            'min_shop': min_shop, 'max_price': max_price, 'max_shop': max_shop, 'avg_price': avg_price}


def avg_tuples_round_2(array):
    return round(avg_tuples(array), 2)


def avg_tuples(array):
    first_elements = [element[0] for element in array]
    return sum(first_elements) / len(first_elements)


def filter_parts_by_shop(parts_by_shops, filter_function):
    return {shop: filter_parts_by_id(parts, filter_function) for shop, parts in parts_by_shops.items()}


def filter_parts_by_id(parts_by_id, filter_function):
    return {part_id: filter_function(prices)
            for part_id, prices in parts_by_id.items()}
