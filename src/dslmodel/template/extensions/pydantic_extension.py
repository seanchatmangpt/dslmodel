from jinja2 import Environment, ext


# Define the PydanticExtension to add custom filters and macros to Jinja
class PydanticExtension(ext.Extension):
    def __init__(self, environment: Environment):
        super().__init__(environment)
        # Register the pydantic_type filter
        environment.filters["pydantic_type"] = self.pydantic_type
        # Register the pydantic_imports macro
        environment.globals["pydantic_imports"] = self.pydantic_imports

    @staticmethod
    def pydantic_type(field: str, *args, **kwargs) -> str:
        type_mapping = {
            "string": "str",
            "integer": "int",
            "boolean": "bool",
            "array": "list",
            "object": "dict",
        }

        if "enum" in field:
            return f'Literal{tuple(field["enum"])}'

        return type_mapping.get(field, "Any")

    @staticmethod
    def pydantic_imports():
        """
        Macro that returns all necessary Pydantic and typing imports.
        This will be rendered in the template where it's called.
        """
        return """
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, List, Dict, Optional
        """
