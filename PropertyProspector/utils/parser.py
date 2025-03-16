import re


def get_text(elem):
    return elem.text.strip() if elem else None


def extract_numeric_field(
    card, tag, pattern, cast_func, transform_func=lambda s: s, default=None
):
    if not (elem := card.find(tag, text=re.compile(pattern))):
        return default
    if match := re.search(pattern, elem.text):
        value_str = transform_func(match.group(1))
        return cast_func(value_str)
    return default
