from typing import Type, Callable, Any, Dict

import typer
from pydantic import BaseModel, Field

app = typer.Typer()


# Utility to extract CLI metadata from a field
def extract_cli_metadata(field_name: str, field_info: Any) -> Dict[str, Any]:
    # Extract metadata from `json_schema_extra` in Pydantic v2
    metadata = field_info.json_schema_extra or {}
    return {
        "help": metadata.get("cli_help", f"{field_name} ({field_info.annotation.__name__})"),
        "default": metadata.get("cli_default", field_info.default if field_info.default is not None else ...),
        "alias": metadata.get("cli_alias", f"--{field_name.replace('_', '-')}"),
        "type": metadata.get("cli_type", field_info.annotation),
    }


# Function to generate CLI arguments/options for each model field
def generate_cli_options(model: Type[BaseModel]) -> Dict[str, Any]:
    options = {}
    for field_name, field_info in model.model_fields.items():
        cli_metadata = extract_cli_metadata(field_name, field_info)
        if cli_metadata["default"] is ...:
            options[field_name] = typer.Argument(
                cli_metadata["default"],
                help=cli_metadata["help"],
                show_default=False
            )
        else:
            # Use the alias as a part of the option, without dynamic keyword arguments
            options[field_name] = typer.Option(
                cli_metadata["default"],
                help=cli_metadata["help"],
                show_default=True,
                # Apply the alias here
                param_decls=[cli_metadata["alias"]],
                type=cli_metadata["type"]
            )
    return options


# Function to create a command function that Typer can register
def create_command_function(model: Type[BaseModel], handler: Callable[[BaseModel], None]) -> Callable:
    def command_function(**kwargs):
        try:
            model_instance = model(**kwargs)
        except Exception as e:
            typer.echo(f"Error creating model instance: {e}", err=True)
            raise typer.Exit(code=1)

        # Call the handler with the model instance
        return handler(model_instance)

    return command_function


# Function to register a model and handler as a command in a Typer app
def typer_command(app: typer.Typer, model: Type[BaseModel], handler: Callable[[BaseModel], None]):
    """
    Registers a Pydantic model as a CLI command in Typer, using a separate handler function.
    """
    command_function = create_command_function(model, handler)
    cli_options = generate_cli_options(model)

    # Wrap the command function with Typer options dynamically
    for option_name, option in cli_options.items():
        command_function = option(command_function)

    # Register the command in the Typer app
    app.command()(command_function)


# Define a sample model with CLI-specific metadata
class UserInput(BaseModel):
    name: str = Field(..., json_schema_extra={"cli_help": "The user's name"})
    age: int = Field(30, json_schema_extra={"cli_help": "The user's age", "cli_alias": "--user-age"})
    active: bool = Field(True, json_schema_extra={"cli_help": "Is the user active?", "cli_default": False})


# Define the handler function for the UserInput model
def handle_user_input(user_input: UserInput):
    typer.echo(f"name={user_input.name}, age={user_input.age}, active={user_input.active}")


# Register the command in Typer
typer_command(app, model=UserInput, handler=handle_user_input)

if __name__ == "__main__":
    app()
