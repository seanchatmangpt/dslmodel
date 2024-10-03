import inflection
from pydantic import Field

import dspy
from dspy import InputField, OutputField, Signature

from dslmodel import DSLModel
from dslmodel.template import render


class FieldTemplateSpecificationModel(DSLModel):
    field_name: str = Field(
        ...,
        description="The name of the field in the model. No prefixes, suffixes, or abbreviations.",
    )
    field_type: str = Field(
        ...,
        description="The data type of the field, e.g., 'str', 'int', 'EmailStr', or 'datetime'. No dict or classes.",
    )
    default_value: str | int | None = Field(
        "...",
        description="The default value for the field if not provided. ",
    )
    description: str = Field(
        ...,
        description="A detailed description of the field's purpose and usage.",
    )
    # constraints: str | None = Field(
    #     None,
    #     description="Constraints or validation rules for the field, if any. Specify as a string, e.g., 'min_length=2, max_length=50' or 'ge=0, le=120'.",
    # )


class ConfigTemplateSpecificationModel(DSLModel):
    title: str = Field(
        ...,
        description="The title for the DSLModel configuration.",
    )
    description: str = Field(
        ...,
        description="A detailed description of the DSLModel configuration's purpose and usage.",
    )
    allow_population_by_field_name: bool = Field(
        True,
        description="Whether to allow populating a model using field names.",
    )
    underscore_attrs_are_private: bool = Field(
        False,
        description="Whether to treat underscore-prefixed attributes as private (no validation).",
    )
    alias_generator: str = Field(
        ...,
        description="The alias generator to use for field aliasing.",
    )


class ValidatorTemplateSpecificationModel(DSLModel):
    validator_name: str = Field(
        ...,
        title="Validator Name",
        description="The name of the validator.",
    )
    description: str = Field(
        ...,
        title="Description",
        description="A detailed description of the validator's purpose and usage.",
    )
    parameters: list[str] = Field(
        [],
        title="Parameters",
        description="A list of parameter names accepted by the validator.",
    )


class DSLModelClassTemplateSpecificationModel(DSLModel):
    class_name: str = Field(
        ...,
        description="The class name of the DSLModel model.",
    )
    description: str = Field(
        ...,
        description="A detailed description of the DSLModel's purpose and usage.",
    )
    fields: list[FieldTemplateSpecificationModel] = Field(
        ...,
        description="A list of field specifications for the model. Each field specifies the name, type, default value, description, and constraints. 15 fields max.",
    )


class_template_str = '''from pydantic Field, validator, root_validator, EmailStr, UrlStr
from typing import List, Optional
from datetime import datetime
from dslmodel import DSLModel


class {{ model.class_name }}(DSLModel):
    """{{ model.description }}"""
    {% for field in model.fields %}
    {{ field.field_name | underscore }}: {{ field.field_type }} = Field(default={{ field.default_value }}, title="{{ field.title }}", description="{{ field.description }}"{% if field.constraints %}, {{ field.constraints }}{% endif %})
    {% endfor %}

    {% if model.validators|length > 0 %}
    {% for validator in model.validators %}
    @validator('{{ validator.parameters|join("', '") }}')
    def {{ validator.validator_name }}(cls, value):
        # {{ validator.description }}
        return value
    {% endfor %}
    {% endif %}
    {% if model.config %}
    class Config:
        {% if model.config.allow_population_by_field_name %}allow_population_by_field_name = True{% endif %}
        {% if model.config.underscore_attrs_are_private %}underscore_attrs_are_private = True{% endif %}
        {% if model.config.alias_generator %}alias_generator = {{ model.config.alias_generator }}{% endif %}
    {% endif %}
'''


def write_pydantic_class_to_file(class_str, filename):
    with open(filename, "w") as file:
        file.write(class_str)


# Example usage
def main():
    from dslmodel.utils.dspy_tools import init_lm
    init_lm()

    model_prompt = ("I need a verbose contact model named ContactModel from the friend of a friend ontology with 10 "
                    "fields, each with length constraints")

    model_inst = DSLModelClassTemplateSpecificationModel.from_prompt(model_prompt, True)

    # Render the Pydantic class from the specification
    rendered_class_str = render(class_template_str, model=model_inst)

    # Write the rendered class to a Python file
    write_pydantic_class_to_file(
        rendered_class_str, f"{inflection.underscore(model_inst.class_name)}.py"
    )


icalendar_entities = {
    "VEVENT": "This is one of the most commonly used components in iCalendar and represents an event.",
    "VTODO": "Represents a to-do task or action item.",
    "VJOURNAL": "Represents a journal entry or a note.",
    "VFREEBUSY": "Represents information about the free or busy time of a calendar user.",
    "VTIMEZONE": "Represents time zone information.",
    "VAVAILABILITY": "Represents availability information for a calendar user.",
    "VALARM": "Represents an alarm or reminder associated with an event or to-do.",
}



# def generate_icalendar_models():
#     for entity, description in icalendar_entities.items():
#         # Define a Pydantic class dynamically for each entity
#         model_prompt = f"I need a model named {entity}Model that has all of the relevant fields for RFC 5545 compliance."
#
#         model_module = GenPydanticInstance(
#             root_model=PydanticClassTemplateSpecificationModel,
#             child_models=[FieldTemplateSpecificationModel],
#             generate_sig=PromptToPydanticInstanceSignature,
#             correct_generate_sig=PromptToPydanticInstanceErrorSignature,
#         )
#
#         model_inst = model_module.forward(model_prompt)
#
#         # Render the Pydantic class from the specification
#         rendered_class_str = template(class_template_str, model=model_inst)
#
#         # Write the rendered class to a Python file
#         write_pydantic_class_to_file(
#             rendered_class_str,
#             f"ical/{inflection.underscore(model_inst.class_name)}.py",
#         )
#
#         print(f"{model_inst.class_name} written to {model_inst.class_name}.py")


from pydantic import BaseModel, Field


if __name__ == "__main__":
    main()
