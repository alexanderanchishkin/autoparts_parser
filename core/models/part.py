class Part:
    def __init__(self, number, model, title=None, price=None, article_id=0):
        self.article_id = article_id
        self.number = number
        self.model = model
        self.title = title
        self.price = price

    def __str__(self):
        return f'{self.number}, {self.model}, {self.title}, {self.price}'

    __repr__ = __str__

    @classmethod
    def not_found(cls, part):
        return cls(part.number, part.model, 'Нет в наличии', 'Нет в наличии')
