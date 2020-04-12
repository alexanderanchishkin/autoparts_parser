from core.io.database import database


def create_tables(table_prefix, parsers):
    return [create_table(table_prefix, parser) for parser in parsers]


def create_table(table_prefix, parser):
    table_name = table_prefix + parser.get_output_filename().split('.')[0].lower()
    query = f"CREATE TABLE {table_name} LIKE generic"
    database.db.execute_sql(query)
    return table_name


def get_tables(between_dates=(), from_shop=None, from_tables=None):
    tables = database.db.get_tables() if from_tables is None else from_tables
    return [table for table in tables
            if _is_table_between_dates(table, between_dates) and _is_from(from_shop, table)]


def _is_table_between_dates(table, dates_between):
    if not dates_between:
        return True

    start_date, end_date = dates_between

    prepared_start_date = _prepare_date_for_table(start_date)
    prepared_end_date = _prepare_date_for_table(end_date)

    return prepared_start_date < table < prepared_end_date + '__3'


def _prepare_date_for_table(date):
    return date.replace('-', '')


def _is_from(shop, table):
    return shop is None or shop in table
