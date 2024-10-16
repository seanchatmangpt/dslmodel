import typer
from typing import Type, Callable, Dict, Any
import dspy
from dslmodel import init_instant

# Create the main Typer app
app = typer.Typer()


def auto_signature_command(
        predictor_class: Callable = dspy.Predict
):
    """
    Decorator factory to generate a Typer command for a given dspy.Signature class.
    Allows specifying the predictor class, defaulting to dspy.Predict.
    """

    def decorator(signature_class: Type[dspy.Signature]):
        signature_name = signature_class.__name__.lower()

        # Create the predictor instance
        predictor = predictor_class(signature_class)

        # Extract only input fields (ignore output fields)
        input_fields = {
            name: field for name, field in signature_class.model_fields.items()
            if field.json_schema_extra.get("__dspy_field_type") == "input"
        }

        # Dynamically build the command function with typed options
        typed_command = build_command_with_options(signature_name, input_fields, predictor)

        # Register the subcommand with the main Typer app
        app.command(name=signature_name)(typed_command)

        return signature_class

    return decorator


def build_command_with_options(
        name: str, fields: Dict[str, Any], predictor: Callable
) -> Callable:
    """
    Dynamically create a Typer-compatible function with typed options
    based on the provided input fields.
    """
    # Build function parameters dynamically with typer.Option
    params = ", ".join(
        f"{field_name}: str = typer.Option(..., help='{field.json_schema_extra.get('desc', '')}')"
        for field_name, field in fields.items()
    )

    # Create the function source code
    func_code = f"""
def {name}({params}):
    kwargs = {{ {', '.join([f"'{k}': {k}" for k in fields.keys()])} }}
    result = predictor(**kwargs)
    if hasattr(result, 'items'):
        result_dict = dict(result.items())
    else:
        result_dict = result
    typer.echo(result_dict)
    """

    # Define a new namespace for the exec'ed code
    namespace = {"typer": typer, "predictor": predictor}

    # Execute the function code in the namespace
    exec(func_code, namespace)

    # Retrieve the generated function from the namespace
    return namespace[name]


# Define the first command
@auto_signature_command(predictor_class=dspy.ChainOfThought)
class JSX(dspy.Signature):
    """
    Generate clean JSX code based on the provided context and requirements,
    ensuring compatibility with react-live environments.
    """
    context = dspy.InputField(
        desc="A brief description of the desired component and its functionality."
    )
    requirements = dspy.InputField(
        desc="Specific requirements or features the JSX should include."
    )

    pure_jsx = dspy.OutputField(
        desc="Clean JSX code without {}, ready for react-live."
    )


# Define another command as an example
@auto_signature_command(predictor_class=dspy.ChainOfThought)
class Markdown(dspy.Signature):
    """
    Generate markdown text based on the provided title and content.
    """
    title = dspy.InputField(
        desc="The title of the markdown document."
    )
    content = dspy.InputField(
        desc="The content of the markdown document."
    )

    markdown = dspy.OutputField(
        desc="The generated markdown text."
    )


if __name__ == "__main__":
    init_instant()
    app()
