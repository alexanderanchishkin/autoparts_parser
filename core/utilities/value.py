import re


def float_try_parse(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def is_correct_positive(number):
    return float_try_parse(number) and float(number) > 0


def has_cyrillic(text):
    return bool(re.search('[а-яА-Я]', text))
