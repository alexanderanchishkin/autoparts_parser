import peewee


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
