from jinja2 import Environment

from dslmodel.template.extensions.faker_extension import FakerExtension
from dslmodel.template.extensions.inflection_extension import InflectionExtension
from dslmodel.template.extensions.pydantic_extension import PydanticExtension


class CustomEnvironment(Environment):
    def __init__(self, **kwargs):
        super(CustomEnvironment, self).__init__(trim_blocks=True, lstrip_blocks=True, **kwargs)

        self.add_extension(FakerExtension)
        self.add_extension(InflectionExtension)
        self.add_extension(PydanticExtension)
        self.add_extension("jinja2_time.TimeExtension")
        self.add_extension("jinja2.ext.i18n")
        self.add_extension("jinja2.ext.debug")
        self.add_extension("jinja2.ext.do")
        self.add_extension("jinja2.ext.loopcontrols")

        self.filters["to_kwarg"] = lambda input_name: f"{input_name}={input_name}"
