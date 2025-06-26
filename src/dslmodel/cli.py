"""dslmodel CLI."""

from pathlib import Path

from dslmodel.utils.dspy_tools import init_lm
from dslmodel.utils.json_output import set_json_mode, json_command
import typer
from rich import print
from typing_extensions import Annotated

from dslmodel import init_instant
from dslmodel.generators.gen_dslmodel_class import generate_and_save_dslmodel
from dslmodel.template import render
from dslmodel.commands import slidev, forge, autonomous, swarm, thesis_cli, demo, capability_map, validate_otel, ollama_validate, weaver, validate_weaver, worktree, telemetry_cli, weaver_health_check, redteam, validation_loop, swarm_worktree, agent_coordination_cli, evolution, auto_evolution, worktree_evolution_cli
try:
    from dslmodel.commands import pqc
    PQC_AVAILABLE = True
except ImportError:
    PQC_AVAILABLE = False
try:
    from dslmodel.commands import otel_coordination_cli
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False

app = typer.Typer()

# Global JSON flag callback
def json_callback(value: bool):
    if value:
        set_json_mode(True)

# Add global --json option
@app.callback()
def main(
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output results in JSON format",
        callback=json_callback,
        is_eager=True
    )
):
    """DSLModel CLI - Telemetry-driven development platform."""
    pass

# app.add_typer(name="asyncapi", typer_instance=asyncapi.app)
app.add_typer(name="slidev", typer_instance=slidev.app)
# app.add_typer(name="coord", typer_instance=coordination_cli.app, help="Agent coordination system")
if PQC_AVAILABLE:
    app.add_typer(name="pqc", typer_instance=pqc.app, help="Post-Quantum Cryptography commands")
if OTEL_AVAILABLE:
    app.add_typer(name="otel", typer_instance=otel_coordination_cli.app, help="OTEL-enhanced coordination system")
app.add_typer(name="forge", typer_instance=forge.app, help="Weaver Forge workflow commands")
app.add_typer(name="auto", typer_instance=autonomous.app, help="Autonomous Decision Engine")
app.add_typer(name="swarm", typer_instance=swarm.app, help="SwarmAgent coordination and management")
app.add_typer(name="thesis", typer_instance=thesis_cli.app, help="SwarmSH thesis implementation and demo")
app.add_typer(name="demo", typer_instance=demo.app, help="Automated full cycle demonstrations")
app.add_typer(name="capability", typer_instance=capability_map.app, help="SwarmAgent capability mapping and visualization")
app.add_typer(name="validate", typer_instance=validate_otel.app, help="Concurrent OpenTelemetry validation and testing")
app.add_typer(name="validate-weaver", typer_instance=validate_weaver.app, help="Weaver-first OpenTelemetry validation using semantic conventions")
app.add_typer(name="validation-loop", typer_instance=validation_loop.app, help="Continuous SwarmAgent validation loop with auto-remediation")
app.add_typer(name="ollama", typer_instance=ollama_validate.app, help="Ollama configuration validation and management")
app.add_typer(name="weaver", typer_instance=weaver.app, help="Weaver-first auto-generation from semantic conventions")
app.add_typer(name="weaver-health", typer_instance=weaver_health_check.app, help="Weaver global health checks with Ollama validation")
app.add_typer(name="worktree", typer_instance=worktree.app, help="Git worktree management for exclusive worktree development")
app.add_typer(name="swarm-worktree", typer_instance=swarm_worktree.app, help="SwarmAgent worktree coordination with OTEL telemetry")
app.add_typer(name="telemetry", typer_instance=telemetry_cli.app, help="Real-time telemetry, auto-remediation, and security monitoring")
app.add_typer(name="redteam", typer_instance=redteam.app, help="Automated red team security testing and vulnerability assessment")
app.add_typer(name="agents", typer_instance=agent_coordination_cli.app, help="Agent coordination with exclusive worktrees and OTEL communication")
app.add_typer(name="evolve", typer_instance=evolution.app, help="Autonomous evolution and self-improvement system")
app.add_typer(name="auto-evolve", typer_instance=auto_evolution.app, help="Automatic evolution with SwarmAgent integration")


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
        model: Annotated[str, "model to use."] = "groq/llama-3.2-90b-text-preview",
):
    """
    Generate DSLModel-based classes from a natural language prompt.

    The generated classes are saved to the specified directory in the chosen format.
    """
    with json_command("gen") as formatter:
        formatter.add_data("prompt", prompt)
        formatter.add_data("output_dir", str(output_dir))
        formatter.add_data("file_format", file_format)
        formatter.add_data("model", model)
        
        formatter.print(f"Generating class from prompt: '{prompt}'")
        from dslmodel.utils.dspy_tools import init_instant

        init_lm(model=model)
        # init_instant()

        # Delegate the core logic to the generate_and_save_dslmodel function
        try:
            _, output_file = generate_and_save_dslmodel(prompt, output_dir, file_format, config)
            formatter.add_data("output_file", str(output_file))
            formatter.add_data("generation_successful", True)
            formatter.print(f"Class generated successfully! Saved in: {output_file}.")
        except Exception as e:
            formatter.add_error(f"Error generating class: {e}")
            formatter.print(f"Error generating class: {e}", level="error")
            raise typer.Exit(code=1)


import json
from pathlib import Path

import typer
import yaml


@app.command("openapi", help="Generate Pydantic models from an OpenAPI schema.")
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
