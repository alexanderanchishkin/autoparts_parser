import itertools
import re


def get_next_parts(iter_parts, n: int) -> list:
    try:
        return list(itertools.islice(iter_parts, n))
    except ValueError:
        return []


def equal_models(self, model1, model2):
    pattern = '[^a-zA-Z]+'
    re1 = re.sub(pattern, '', model1.replace(' ', '').lower())
    re2 = re.sub(pattern, '', model2.replace(' ', '').lower())
    re1 = self.check_abbr(re1)
    re2 = self.check_abbr(re2)
    custom_checked = self._custom_equal(re1, re2, model1, model2)
    return (len(re1) > 1 and len(re2) > 1 and re1 == re2) or custom_checked


def check_abbr(self, short_model):
    if short_model == 'gm':
        return 'generalmotors'

    if 'mercede' in short_model:
        return 'mercedesbenz'

    return short_model


def _custom_equal(re1, re2, model1, model2):
    if model1.lower() == 'mercedez' or model1.lower() == 'mercedes':
        return model1.lower()[:-1] in model2.lower()

    if model1.lower() == 'hyundai' or model1.lower() == 'hundai':
        return 'hyundai' in model2.lower()

    if re1 == 'toyotalexux' or re2 == 'toyotalexux' or re1 == 'lexustoyota' or re2 == 'lexustoyota':
        return re1 == re2 or re1 == 'toyota' or re2 == 'toyota' or re1 == 'citroen' or re2 == 'lexus'

    if re1 == 'citroenpeugeot' or re2 == 'citroenpeugeot' or re1 == 'peugeotcitroen' or re2 == 'peugeotcitroen':
        return re1 == re2 or re1 == 'citroen' or re2 == 'citroen' or re1 == 'peugeot' or re2 == 'peugeot'

    return re1 == re2