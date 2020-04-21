from core.io.database import database
from core.io.database.utilities import table

from config import settings


def write_report(statistics):
    table_name = table.create_report_table(settings.time_moment_name)
    insert_statistics(table_name, statistics)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def insert_statistics(table_name: str, statistics: list):
    if not statistics:
        return

    # noinspection SqlResolve
    query_start = f"INSERT INTO `{table_name}` (`article_id`, `min_price`, `min_shop`, " \
                  f"`avg_price`, `max_price`, `max_shop`) VALUES"
    statistics_values = [prepare_statistics_values(one_statistics) for one_statistics in statistics
                         if 'article' in one_statistics and 'brand' in one_statistics]

    values = chunks(statistics_values, 100)
    for value in values:
        query = f"{query_start} {', '.join(value)}"
        database.db.execute_sql(query)


def prepare_statistics_values(one_statistics):
    article_id = _generate_article_id_subquery(one_statistics)
    return f"(({article_id}), {one_statistics['min_price']}, " \
           f"'{one_statistics['min_shop']}', {one_statistics['avg_price']}, " \
           f"{one_statistics['max_price']}, '{one_statistics['max_shop']}')"


def _generate_article_id_subquery(one_statistics):
    return\
        f"SELECT id FROM articles "\
        f"WHERE LOWER(article) = LOWER('{str(one_statistics['article'])}') "\
        f"AND LOWER(brand) = LOWER('{one_statistics['brand']}') LIMIT 1"
