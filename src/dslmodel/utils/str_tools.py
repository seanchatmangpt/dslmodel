import inflection


def pythonic_str(value):
    return inflection.underscore(str(value).replace(" ", "_"))


def dasherize(value):
    return inflection.dasherize(pythonic_str(value))

def camelize_lower(value):
    return inflection.camelize(str(value), uppercase_first_letter=False)