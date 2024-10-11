from pathlib import Path

from dslmodel.template import render


class DSLClassGenerator:
    """
    This class generates Python classes using the provided DSLModel specifications.
    It includes functionality for appending to files or creating new ones.
    """

    class_template_str = '''{% if include_imports %}
from pydantic import Field, validator, root_validator, EmailStr
from typing import List, Optional
from datetime import datetime
from dslmodel import DSLModel
{% endif %}

class {{ model.class_name }}(DSLModel):
    """{{ model.description }}"""
    {% for field in model.fields %}
    {{ field.field_name | underscore }}: {{ field.field_type }} = Field(default={{ field.default_value }}, alias="{{ field.field_name }}", description="{{ field.description }}"{% if field.constraints %}, {{ field.constraints }}{% endif %})
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

    def __init__(
        self,
        model_prompt: str,
        file_path: Path = Path.cwd(),
        append: bool = False,
        max_workers: int = 5,
    ):
        """
        Initializes the generator with a prompt for the model and output settings.

        :param model_prompt: The natural language prompt that specifies the class.
        :param file_path: The path where the generated class will be saved. If a directory, the class will be saved with a auto-generated name.
        If a file, the name will be used.
        :param append: Whether to append to the file if it exists. Default is False.
        :param max_workers: The number of workers to use for parallel processing. Default is 5.
        """
        self.model_prompt = model_prompt
        self.file_path = file_path
        self.append = append
        self.max_workers = max_workers

    def __call__(self):
        return self.forward()

    def generate_fields(self):
        """
        Generates a list of field names based on the model prompt (stub implementation).
        In real implementation, this would use a model generation tool.
        """
        from dslmodel.generators import gen_list

        return gen_list(
            f"Please provide only the field names for a BaseModel derived from the following prompt. "
            f"The model should follow Python naming conventions and include only the names of the fields, "
            f"without any additional metadata or descriptions. Strings must have quotes."
            f'Example: list = ["id", "name", "age"]'
            f"\nPrompt: {self.model_prompt}"
        )

    def generate_field_descriptions(self, fields: list):
        """
        Generates detailed field descriptions (stub implementation).
        """
        from dslmodel.generators.gen_models import FieldTemplateSpecificationModel

        tasks = [
            (
                FieldTemplateSpecificationModel,
                f"Generate a field named {field} with a useful description",
            )
            for field in fields
        ]
        from dslmodel.utils.model_tools import run_dsls

        return run_dsls(tasks, self.max_workers)

    def generate_model_instance(self):
        """
        Creates a model instance from the prompt.
        """
        from dslmodel.generators.gen_models import DSLModelClassTemplateSpecificationModel

        return DSLModelClassTemplateSpecificationModel.from_prompt(self.model_prompt)

    def render_class(self, model_inst, fields, include_imports: bool):
        """
        Renders the class based on the template and provided fields.
        """
        template_data = {**model_inst.model_dump(), "fields": fields}
        return render(self.class_template_str, model=template_data, include_imports=include_imports)

    def write_class_to_file(self, rendered_class_str, class_name):
        """
        Writes or appends the rendered class to a file.
        """
        from dslmodel.utils.str_tools import pythonic_str

        if self.file_path.is_dir():
            filename = f"{pythonic_str(class_name)}.py"
            output_path = self.file_path / filename
        else:
            output_path = self.file_path

        mode = "a" if self.append else "w"
        with open(output_path, mode) as file:
            file.write(rendered_class_str)

        action = "Appended to" if self.append else "Written to"
        print(f"{action} {output_path}")
        return output_path

    def forward(self):
        """
        Main method to generate and save a DSLModel class based on the provided prompt.
        """
        fields = self.generate_fields()
        field_descriptions = self.generate_field_descriptions(fields)
        model_instance = self.generate_model_instance()

        # Determine whether to include imports
        include_imports = not self.append

        # Render the class with or without imports
        rendered_class = self.render_class(model_instance, field_descriptions, include_imports)

        # Write or append the class to the file
        return self.write_class_to_file(rendered_class, model_instance.class_name)


swagger_data = {
    "x-swagger-router-model": "io.swagger.petstore.model.Pet",
    "required": ["name", "photoUrls"],
    "properties": {
        "id": {"type": "integer", "format": "int64", "example": 10},
        "name": {"type": "string", "example": "doggie"},
        "category": {"$ref": "#/components/schemas/Category"},
        "photoUrls": {
            "type": "array",
            "xml": {"wrapped": True},
            "items": {"type": "string", "xml": {"name": "photoUrl"}},
        },
        "tags": {
            "type": "array",
            "xml": {"wrapped": True},
            "items": {"$ref": "#/components/schemas/Tag", "xml": {"name": "tag"}},
        },
        "status": {
            "type": "string",
            "description": "pet status in the store",
            "enum": ["available", "pending", "sold"],
        },
    },
    "xml": {"name": "pet"},
    "type": "object",
}


def create_dslmodel_from_swagger(swagger: dict):
    jinja_template = """I need a DSLModel called {{ swagger['x-swagger-router-model'].split('.')[-1] }} with the following fields:
{% for field_name, field_info in swagger['properties'].items() %}
    {{ field_name }}: {{ field_info['type'] }} = Field(..., description="{{ field_info.get('description', '') }}")
{% endfor %}
"""
    prompt = render(jinja_template, swagger=swagger)
    print(prompt)
    return DSLClassGenerator(prompt)()


# Example usage
if __name__ == "__main__":
    from dslmodel import init_instant

    init_instant()

    create_dslmodel_from_swagger(swagger_data)

    # model_prompt = "I need a UserModel with 2 fields"
    # output_dir = Path("gen_models.py")
    # append_to_file = True  # Set to True to append to the file instead of overwriting
    #
    # # Create an instance of DSLClassGenerator
    # dsl_generator = DSLClassGenerator(model_prompt, output_dir, append=append_to_file)
    #
    # # Generate and save (or append) the class
    # generated_class_path = dsl_generator.forward()
    # print(f"Generated class saved at: {generated_class_path}")
