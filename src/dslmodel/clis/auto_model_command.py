import typer
from typing import Type, Callable, Dict
from pydantic import BaseModel, Field
from pydantic_core import PydanticUndefined

from dslmodel import init_instant
from dslmodel.template.functional import render

# Create the main Typer app
app = typer.Typer()


def auto_base_model_command(predictor_class: Callable = None):
    """
    Decorator factory to generate a Typer command for a given BaseModel class.
    """

    def decorator(base_model_class: Type[BaseModel]):
        base_model_name = base_model_class.__name__.lower()
        help_text = base_model_class.__doc__ or f"{base_model_name} command"

        # Extract field definitions from the BaseModel
        fields = extract_field_definitions(base_model_class)

        # Build the command function with the extracted field options
        typed_command = build_command_with_options(base_model_name, fields)

        # Register the command with the Typer app
        register_command(base_model_name, typed_command, help_text)

        return base_model_class

    return decorator


def extract_field_definitions(base_model_class: Type[BaseModel]) -> Dict[str, Dict]:
    """
    Extract field definitions including type, default value, and description
    from the Pydantic BaseModel.
    """
    fields = {}

    for field_name, field in base_model_class.model_fields.items():
        # Extract description or use an empty string if not provided
        description = field.description or ""

        # Determine the default value or mark as required
        if field.default is not PydanticUndefined:
            default = field.default
        else:
            default = ...

        # Determine the type of the field
        field_type = field.annotation or str

        # If default is a string, render it with the render function
        if isinstance(default, str):
            default = render(default)

        # Store the extracted information in the dictionary
        fields[field_name] = {
            "description": description,
            "default": default,
            "type": field_type
        }

    return fields


def create_param(field_name: str, field_info: Dict) -> str:
    """
    Create a parameter string for a Typer command based on field information.
    """
    field_type = field_info['type']
    default = field_info['default']
    description = field_info['description']

    # Determine how to represent the default value
    default_repr = repr(default) if default is not ... else "..."

    # Construct the parameter string
    param = f"{field_name}: {field_type.__name__} = typer.Option({default_repr}, help='{description}')"
    return param


def build_command_with_options(
        name: str,
        fields: Dict[str, Dict],
) -> Callable:
    """
    Dynamically create a Typer-compatible function with typed options
    based on the provided input fields.
    """
    # Use create_param to build the function parameters
    params = ", ".join(create_param(field_name, field_info) for field_name, field_info in fields.items())

    # Create the function source code as a string
    func_code = f"""
def {name}({params}):
    kwargs = {{ {', '.join([f"'{k}': {k}" for k in fields.keys()])} }}
    typer.echo(kwargs)
    """

    namespace = {"typer": typer}

    # Execute the function code in the namespace
    exec(func_code, namespace)

    # Retrieve the generated function from the namespace
    return namespace[name]


def register_command(name: str, command: Callable, help_text: str):
    """
    Register a command with the Typer app using the provided name and help text.
    """
    app.command(name=name, help=help_text)(command)


# Example BaseModel to test with
@auto_base_model_command()
class MyModel(BaseModel):
    """
    This is the help text for the MyModel command.
    Use this command to specify a name, age, and description.
    """
    name: str = Field(..., description="The name of the person.")
    age: int = Field(..., description="The age of the person.")
    description: str = Field("A default description {{ fake_bs() }}", description="A brief description of the person.")


@auto_base_model_command()
class YourModel(BaseModel):
    """
    This is the help text for the YourModel command.
    It allows you to specify a name, age, and a different description.
    """
    name: str = Field(..., description="The name of another person.")
    age: int = Field(..., description="The age of the other person.")
    description: str = Field("Another description", description="A different description for the person.")


if __name__ == "__main__":
    init_instant()
    app()
