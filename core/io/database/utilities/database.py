from core.io.database import database
from core.io.database.utilities.table import get_tables


def get_tuples_tables(start_date, end_date):
    shop_tables = get_grouped_tables(start_date, end_date)
    shop_parts = {shop: get_parts_from_tables(tables) for shop, tables in shop_tables.items()}
    shop_grouped_parts = {shop: group_parts(shop, parts) for shop, parts in shop_parts.items()}

    result_parts = {}

    for shop, parts in shop_grouped_parts.items():
        for part_id, array_tuples in parts.items():
            if part_id not in result_parts:
                result_parts[part_id] = []
            result_parts[part_id].extend(array_tuples)
    return result_parts


def get_grouped_tables(start_date, end_date):
    tables = get_tables(between_dates=(start_date, end_date))
    shops = set([table.split('__')[2] for table in tables])
    return {shop: get_tables(from_shop=shop, from_tables=tables) for shop in shops}


def get_parts_from_tables(tables):
    single_query_prefix = "SELECT article_id, price, "
    queries = [single_query_prefix + str(index) + " FROM " + table for index, table in enumerate(tables)]
    query = ' UNION '.join(queries)
    return database.db.execute_sql(query).fetchall()


def group_parts(shop, parts):
    ids = set([part[0] for part in parts])
    grouped_parts = {part_id: [] for part_id in ids}
    if not shop:
        [grouped_parts[part[0]].append(part[1]) for part in parts]
    else:
        [grouped_parts[part[0]].append((part[1], shop.replace('_', ' ').capitalize())) for part in parts]
    return grouped_parts
