from core.io.database import models, database
from core.utilities import value


def get_all_parts():
    return models.Article.select()


def add_parts(parts):
    articles = models.Article.generate_rows_from_parts(parts)
    models.Article.insert_many(articles).on_conflict_ignore().execute()

# TODO: One statement
def write_parts(table_name, parts):
    [write_part(table_name, part) for article, part in parts.items() if value.is_correct_positive(part.price)]


def write_part(table_name, part):
    article_id = f"SELECT id FROM articles " \
                 f"WHERE LOWER(article) = LOWER({str(part.number)}) " \
                 f"AND LOWER(brand) = LOWER({part.model}) LIMIT 1"

    # noinspection SqlResolve
    query = f"INSERT INTO {table_name} (`article_id`, `price`) VALUES ({article_id}, {part.price})"

    database.db.execute_sql(query)
