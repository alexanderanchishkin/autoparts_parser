import peewee
import settings

db = peewee.MySQLDatabase('autoparts_parser',
                          host="127.0.0.1", port=3306, user="autoparts_parser", passwd="parser123")


class Article(peewee.Model):
    article = peewee.CharField()
    brand = peewee.CharField()

    class Meta:
        database = db
        db_table = 'articles'


def add_parts(parts):
    articles = [{'article': part.number.upper(), 'brand': part.model.upper()} for part in parts]
    Article.insert_many(articles).on_conflict_ignore().execute()


def create_tables(table_prefix, parsers):
    return [create_table(table_prefix, parser) for parser in parsers]


def create_table(table_prefix, parser):
    table_name = table_prefix + parser.OUTPUT_FILE.split('.')[0].lower()
    query = f"CREATE TABLE {table_name} LIKE generic"
    db.execute_sql(query)
    return table_name


def write_parts(table_name, parts):
    [write_part(table_name, part) for article, part in parts.items() if float(part.price) > 0]


# noinspection SqlResolve
def write_part(table_name, part):
    key = (part.number + part.model).upper()
    article_id = settings.articles_dict.get(key)
    query = f"INSERT INTO {table_name} (`article_id`, `price`) VALUES ({article_id}, {part.price})"
    db.execute_sql(query)
    return True


def get_all_parts():
    return Article.select()


def get_tables_between(start_date, end_date):
    prepared_start_date = start_date.replace('-', '')
    prepared_end_date = end_date.replace('-', '')
    all_tables = db.get_tables()
    need_tables = [table for table in all_tables if prepared_start_date < table < prepared_end_date + '__3']
    return need_tables


def get_tables(start_date, end_date, shop=None):
    tables_between = get_tables_between(start_date, end_date)
    if not shop:
        return tables_between
    shop_tables = [table for table in tables_between if shop in table]
    return shop_tables


def get_grouped_tables(start_date, end_date):
    tables = get_tables(start_date, end_date)
    shops = set([table.split('__')[2] for table in tables])
    return {shop: get_shop_tables(shop, tables) for shop in shops}


def get_shop_tables(shop, tables):
    return [table for table in tables if shop in table]


def get_parts_grouped_tables(start_date, end_date):
    grouped_tables = get_grouped_tables(start_date, end_date)
    return {shop: get_grouped_parts_from_tables(shop, tables) for shop, tables in sorted(grouped_tables.items())}


# noinspection SqlResolve
def get_parts_from_table(table_name):
    query = f"SELECT article_id, price FROM {table_name}"
    return db.execute_sql(query).fetchall()


def get_parts_from_tables(tables):
    single_query_prefix = "SELECT article_id, price, "
    queries = [single_query_prefix + str(index) + " FROM " + table for index, table in enumerate(tables)]
    query = ' UNION '.join(queries)
    return db.execute_sql(query).fetchall()


def get_grouped_parts_from_tables(shop, tables):
    parts = get_parts_from_tables(tables)
    return group_parts(shop, parts)


def get_parts_grouped_by_id(start_date, end_date):
    tables = get_tables_between(start_date, end_date)
    return get_grouped_parts_from_tables(None, tables)


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


def group_parts(shop, parts):
    ids = set([part[0] for part in parts])
    grouped_parts = {part_id: [] for part_id in ids}
    if not shop:
        [grouped_parts[part[0]].append(part[1]) for part in parts]
    else:
        [grouped_parts[part[0]].append((part[1], shop.replace('_', ' ').capitalize())) for part in parts]
    return grouped_parts
