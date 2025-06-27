from typing import Type, Callable, Any, Dict
import typer
from pydantic import BaseModel, Field
import inspect
import makefun

app = typer.Typer()


# Utility to extract CLI metadata from a field
def extract_cli_metadata(field_name: str, field_info: Any) -> Dict[str, Any]:
    """Extract CLI metadata from a Pydantic field.
    
    Args:
        field_name: The name of the field
        field_info: The Pydantic field info
        
    Returns:
        A dictionary of CLI metadata
    """
    metadata = field_info.json_schema_extra or {}
    return {
        "help": metadata.get("cli_help", f"{field_name} ({field_info.annotation.__name__})"),
        "default": metadata.get("cli_default", field_info.default if field_info.default is not None else ...),
        "alias": metadata.get("cli_alias", f"--{field_name.replace('_', '-')}"),
        "type": metadata.get("cli_type", field_info.annotation),
    }


# Function to create a Typer command from a Pydantic model
def register_model_command(app: typer.Typer, model: Type[BaseModel], handler: Callable[[BaseModel], None]):
    """Register a Typer command from a Pydantic model.
    
    Args:
        app: The Typer app to register the command with
        model: The Pydantic model to create the command from
        handler: The function to handle the command
    """
    params = []
    for field_name, field_info in model.model_fields.items():
        cli_metadata = extract_cli_metadata(field_name, field_info)
        param_type = cli_metadata["type"]
        default = cli_metadata["default"]
        help_text = cli_metadata["help"]
        alias = cli_metadata["alias"]
        
        if default is ...:
            param = inspect.Parameter(
                field_name,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=param_type,
            )
        else:
            param = inspect.Parameter(
                field_name,
                inspect.Parameter.KEYWORD_ONLY,
                default=typer.Option(default, help=help_text),
                annotation=param_type,
            )
        params.append(param)

    def command_template(**kwargs):
        instance = model(**kwargs)
        return handler(instance)

    func_signature = inspect.Signature(params)
    func_impl = command_template
    
    command = makefun.create_function(
        func_signature=func_signature,
        func_impl=func_impl,
        func_name=f"{model.__name__.lower()}_command"
    )
    app.command()(command)


# Define a sample model with CLI-specific metadata
class UserInput(BaseModel):
    """Sample model with CLI-specific metadata."""
    name: str = Field(..., json_schema_extra={"cli_help": "The user's name"})
    age: int = Field(30, json_schema_extra={"cli_help": "The user's age", "cli_alias": "--user-age"})
    active: bool = Field(True, json_schema_extra={"cli_help": "Is the user active?", "cli_default": False})


# Define the handler function for the UserInput model
def handle_user_input(user_input: UserInput):
    """Handle the user input command.
    
    Args:
        user_input: The user input model instance
    """
    typer.echo(f"name={user_input.name}, age={user_input.age}, active={user_input.active}")


# Register the command in Typer
register_model_command(app, model=UserInput, handler=handle_user_input)

if __name__ == "__main__":
    app()
