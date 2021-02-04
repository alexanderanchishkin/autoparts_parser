import peewee

from core.io.database import database


class Article(peewee.Model):
    article = peewee.CharField()
    brand = peewee.CharField()

    @classmethod
    def generate_rows_from_parts(cls, parts):
        return [cls.generate_row_from_part(part) for part in parts if part.number and part.model]

    @classmethod
    def generate_row_from_part(cls, part):
        return {'article': part.number.upper(), 'brand': part.model.upper()}

    class Meta:
        database = database.db
        db_table = 'articles'
