from settings import *


class Part:
    def __init__(self, number, model, title=None, price=None):
        self.number = number
        self.model = model
        self.title = title
        self.price = price

        if VERBOSE:
            print(f'Part created: {number}, {model}')

    def __str__(self):
        return f'{self.number}, {self.model}, {self.title}, {self.price}'

    __repr__ = __str__
