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
