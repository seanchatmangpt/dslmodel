from pydantic import BaseModel, Field
from jinja2 import Template
from typing import Type, Dict

from pydantic_core import PydanticUndefined

# Jinja template for Zod schema generation
zod_template = """
import { z } from 'zod';

export const {{ model_name }}Schema = z.object({
    {%- for field_name, field_info in fields.items() %}
    {{ field_name }}: z.{{ field_info['type'] }}(){% if field_info['default'] is not none and field_info['default'] != 'PydanticUndefined' %}.default({{ field_info['default'] }}){% endif %}{% if field_info['optional'] %}.optional(){% endif %},
    {%- endfor %}
});
"""


def generate_zod_schema(model: Type[BaseModel]) -> str:
    """
    Generates a Zod schema from a Pydantic BaseModel using a Jinja template.

    Args:
        model (Type[BaseModel]): The Pydantic BaseModel class.

    Returns:
        str: The generated Zod schema as a string.
    """
    # Extract fields, types, and default values
    fields = {}
    for field_name, field in model.model_fields.items():
        field_type = get_zod_type(field.annotation)
        # Handle default values and optionality
        default = repr(field.default) if field.default is not PydanticUndefined else None
        optional = field.default is not PydanticUndefined and field.default is not None

        fields[field_name] = {
            "type": field_type,
            "default": default,
            "optional": optional
        }

    # Render the template
    template = Template(zod_template)
    return template.render(model_name=model.__name__, fields=fields)


def get_zod_type(python_type) -> str:
    """
    Maps Python types to Zod types.

    Args:
        python_type: The type to map.

    Returns:
        str: Corresponding Zod type as a string.
    """
    type_mapping = {
        str: 'string',
        int: 'number',
        float: 'number',
        bool: 'boolean',
        list: 'array',
        dict: 'object',
    }

    # Handle lists and other generic types if needed
    return type_mapping.get(python_type, 'any')


# Example usage
class MyModel(BaseModel):
    name: str = Field(..., description="The name of the person.")
    age: int = Field(..., description="The age of the person.")
    description: str = Field("A default description", description="A brief description of the person.")


def main():
    """Main function"""
    from dslmodel import init_lm, init_instant, init_text
    init_instant()

    zod_schema = generate_zod_schema(MyModel)
    print(zod_schema)


if __name__ == '__main__':
    main()
