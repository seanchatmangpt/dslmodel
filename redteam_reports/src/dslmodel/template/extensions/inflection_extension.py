import inflection
from jinja2.ext import Extension

from dslmodel.utils.str_tools import dasherize, pythonic_str, camelize_lower


class InflectionExtension(Extension):
    def __init__(self, environment):
        super(InflectionExtension, self).__init__(environment)

        environment.filters["camelize"] = inflection.camelize
        environment.filters["camelize_lower"] = camelize_lower
        environment.filters["dasherize"] = dasherize
        # environment.filters["dasherize"] = inflection.dasherize
        environment.filters["humanize"] = inflection.humanize
        environment.filters["ordinal"] = inflection.ordinal
        environment.filters["ordinalize"] = inflection.ordinalize
        environment.filters["parameterize"] = inflection.parameterize
        environment.filters["pluralize"] = inflection.pluralize
        environment.filters["singularize"] = inflection.singularize
        environment.filters["tableize"] = inflection.tableize
        environment.filters["titleize"] = inflection.titleize
        environment.filters["transliterate"] = inflection.transliterate
        environment.filters["underscore"] = inflection.underscore
        environment.filters["class_name"] = inflection.camelize
        environment.filters["var_name"] = inflection.underscore
        environment.filters["pythonic_str"] = pythonic_str

