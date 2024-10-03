from inflection import underscore


def pythonic_str(value):
    return underscore(str(value).replace(" ", "_"))
