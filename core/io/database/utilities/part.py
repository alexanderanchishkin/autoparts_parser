from config import settings
from core.io.database import models, database
from core.utilities import part as part_
from core.utilities import value


def get_iter_parts():
    return get_all_parts().iterator()


def get_all_parts():
    return models.Article.select()


def add_parts(iter_parts):
    while True:
        parts = part_.get_next_parts(iter_parts, settings.DB_BUFFER_SIZE)
        if not parts:
            break
        articles = models.Article.generate_rows_from_parts(parts)
        models.Article.insert_many(articles).on_conflict_ignore().execute()


def write_parts(table_name: str, parts: list):
    correct_parts = [part for part in parts if value.is_correct_positive(part.price)]
    insert_parts(table_name, correct_parts)


def insert_parts(table_name: str, parts: list):
    if not parts:
        return

    # noinspection SqlResolve
    query_start = f"INSERT INTO `{table_name}` (`article_id`, `price`) VALUES"
    parts_values = [prepare_part_values(part) for part in parts]
    query = f"{query_start} {', '.join(parts_values)}"

    database.db.execute_sql(query)


def prepare_part_values(part):
    article_id = _generate_article_id_subquery(part)
    return f"(({article_id}), {part.price})"


def _generate_article_id_subquery(part):
    return\
        f"SELECT id FROM articles "\
        f"WHERE LOWER(article) = LOWER('{str(part.number)}') "\
        f"AND LOWER(brand) = LOWER('{part.model}') LIMIT 1"
