import re


def get_clean_text(elem):
    if not elem:
        return None
    return " ".join(elem.text.strip().split())


def extract_numeric_field(
    card, tag, pattern, cast_func, transform_func=lambda s: s, default=None
):
    if not (elem := card.find(tag, text=re.compile(pattern))):
        return default
    if match := re.search(pattern, elem.text):
        value_str = transform_func(match.group(1))
        return cast_func(value_str)
    return default


def extract_numeric_by_data_cy(card, data_cy, cast_func):
    elem = card.find("li", attrs={"data-cy": data_cy})
    if elem and (match := re.search(r"(\d+)", elem.text)):
        return cast_func(match.group(1))
    return None
