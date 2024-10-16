"""dslmodel CLI."""

from pathlib import Path

import typer
from rich import print

from dslmodel import init_instant
from dslmodel.generators.gen_dslmodel_class import generate_and_save_dslmodel
from dslmodel.template import render

app = typer.Typer()


@app.command()
def fire(name: str = "Chell") -> None:
    """Fire portal gun."""
    print(f"[bold red]Alert![/bold red] {name} fired [green]portal gun[/green] :boom:")


@app.command("gen")
def generate_class(
    prompt: str = typer.Argument(
        ..., help="A natural language description of the model(s) to generate."
    ),
    output_dir: Path = typer.Option(
        Path.cwd(),
        "--output-dir",
        help="The directory to save the generated class files. Defaults to the current directory.",
    ),
    file_format: str = typer.Option(
        "py",
        "--file-format",
        help="The file format for saving the generated models. Defaults to 'py'.",
    ),
    config: Path = typer.Option(None, "--config", help="Path to a custom configuration file."),
):
    """
    Generate DSLModel-based classes from a natural language prompt.

    The generated classes are saved to the specified directory in the chosen format.
    """
    typer.echo(f"Generating class from prompt: '{prompt}'")
    from dslmodel.utils.dspy_tools import init_instant

    # init_lm()
    init_instant()

    # Delegate the core logic to the generate_and_save_dslmodel function
    try:
        generate_and_save_dslmodel(prompt, output_dir, file_format, config)
    except Exception as e:
        typer.echo(f"Error generating class: {e}")
        raise typer.Exit(code=1)

    typer.echo(f"Class generated successfully! Saved in: {output_dir}")


import json
from pathlib import Path

import typer
import yaml


@app.command("openapi")
def generate_models(openapi_file: Path = Path("openapi.yaml"), output_dir: Path = Path(".")):
    # Ensure the output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load the OpenAPI file
    with open(openapi_file) as file:
        if openapi_file.suffix in [".yaml", ".yml"]:
            openapi_data = yaml.safe_load(file)
        elif openapi_file.suffix == ".json":
            openapi_data = json.load(file)
        else:
            typer.echo("Unsupported file format. Use YAML or JSON.")
            raise typer.Exit()

    # Process each schema in OpenAPI
    schemas = openapi_data.get("components", {}).get("schemas", {})
    if not schemas:
        typer.echo("No schemas found in the OpenAPI file.")
        raise typer.Exit()

    init_instant()

    for schema_name, schema in schemas.items():
        if schema_name != "Pet":
            continue
        print(schema)
        # Render the model
        jinja_template = """I need a DSLModel called {{ schema_name }} with the following fields:
        {% for field_name, field_info in swagger['properties'].items() %}
            {{ field_name }}: {{ field_info['type'] }} = Field(..., description="{{ field_info.get('description', '') }}")
        {% endfor %}
        """
        prompt = render(jinja_template, schema_name=schema_name, swagger=schema)
        from dslmodel.generators.dsl_class_generator import DSLClassGenerator

        DSLClassGenerator(prompt, max_workers=3)()

        from time import sleep

        sleep(1)

        typer.echo(f"Generated Pydantic model for '{schema_name}'")


if __name__ == "__main__":
    app()
