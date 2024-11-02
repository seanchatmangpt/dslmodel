import inflection


def pythonic_str(value):
    return inflection.underscore(str(value).replace(" ", "_"))


def dasherize(value):
    return inflection.dasherize(pythonic_str(value))
