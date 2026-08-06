"""ERRC-modernized consolidated DSLModel CLI.

Every existing Typer application is delegated directly.  Optional import failure
is isolated to its own capability and preserved as a machine-readable receipt.
"""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from dslmodel.capabilities import CapabilityRegistry, CapabilitySpec, CapabilityStanding
from dslmodel.generators.openapi_models import OpenAPIGenerationError, generate_openapi_models

console = Console()
app = typer.Typer(help="Consolidated DSLModel capabilities", no_args_is_help=True)
core_app = typer.Typer(help="Core manufacture, evolution, coordination, validation, and development")
advanced_app = typer.Typer(help="Security, telemetry, and research capabilities")
validation_app = typer.Typer(help="Validation implementations")
development_app = typer.Typer(help="Development implementations")
security_app = typer.Typer(help="Security implementations")
telemetry_app = typer.Typer(help="Telemetry implementations")
research_app = typer.Typer(help="Research implementations")

registries = {
    "core": CapabilityRegistry(),
    "validation": CapabilityRegistry(),
    "development": CapabilityRegistry(),
    "security": CapabilityRegistry(),
    "telemetry": CapabilityRegistry(),
    "research": CapabilityRegistry(),
}


CORE_CAPABILITIES = (
    CapabilitySpec("evolution", "dslmodel.commands.unified_8020_evolution", "Unified 80/20 evolution", group="core", command="evolve"),
    CapabilitySpec("agents", "dslmodel.commands.agent_coordination_cli", "Agent coordination", group="core", command="agent"),
    CapabilitySpec("demo", "dslmodel.commands.demo", "Full-cycle demonstrations", group="core"),
)
VALIDATION_CAPABILITIES = (
    CapabilitySpec("otel-validation", "dslmodel.commands.validate_otel", "OpenTelemetry validation", group="validation", command="otel"),
    CapabilitySpec("weaver-validation", "dslmodel.commands.validate_weaver", "Weaver validation", group="validation", command="weaver"),
    CapabilitySpec("complete-8020", "dslmodel.commands.complete_8020_validation", "Complete 80/20 validation", group="validation", command="8020"),
    CapabilitySpec("validation-loop", "dslmodel.commands.validation_loop", "Continuous validation loop", group="validation", command="loop"),
)
DEVELOPMENT_CAPABILITIES = (
    CapabilitySpec("forge", "dslmodel.commands.forge", "Weaver Forge", group="development"),
    CapabilitySpec("weaver", "dslmodel.commands.weaver", "Weaver semantic conventions", group="development"),
    CapabilitySpec("worktree", "dslmodel.commands.worktree", "Git worktree management", group="development"),
)
SECURITY_CAPABILITIES = (
    CapabilitySpec("redteam", "dslmodel.commands.redteam", "Red-team validation", group="security"),
    CapabilitySpec("pqc", "dslmodel.commands.pqc", "Post-quantum cryptography", group="security"),
)
TELEMETRY_CAPABILITIES = (
    CapabilitySpec("monitor", "dslmodel.commands.telemetry_cli", "Telemetry monitoring", group="telemetry"),
    CapabilitySpec("ollama", "dslmodel.commands.ollama_validate", "Ollama runtime validation", group="telemetry"),
    CapabilitySpec("otel-coordination", "dslmodel.commands.otel_coordination_cli", "OTEL coordination", group="telemetry", command="coordination"),
)
RESEARCH_CAPABILITIES = (
    CapabilitySpec("thesis", "dslmodel.commands.thesis_cli", "SwarmSH thesis", group="research"),
    CapabilitySpec("capability-map", "dslmodel.commands.capability_map", "Capability mapping", group="research", command="capability"),
    CapabilitySpec("slidev", "dslmodel.commands.slidev", "Slidev presentations", group="research"),
)


@core_app.command("gen")
def generate_models(
    prompt: str = typer.Argument(..., help="Natural-language model description."),
    output_dir: Path = typer.Option(Path.cwd(), "--output-dir"),
    file_format: str = typer.Option("py", "--format"),
    model: str = typer.Option("groq/llama-3.2-90b-text-preview", "--model"),
) -> None:
    """Execute the existing model generator rather than reporting a placeholder."""

    try:
        from dslmodel.generators.gen_dslmodel_class import generate_and_save_dslmodel
        from dslmodel.utils.dspy_tools import init_lm
    except (ImportError, ModuleNotFoundError) as exc:
        console.print(f"[red]REFUSED:GENERATOR_UNAVAILABLE[/red] {exc}")
        raise typer.Exit(2) from exc
    output_dir.mkdir(parents=True, exist_ok=True)
    init_lm(model=model)
    try:
        _, output_file = generate_and_save_dslmodel(prompt, output_dir, file_format, None)
    except Exception as exc:
        console.print(f"[red]BUILD_BROKEN[/red] {exc}")
        raise typer.Exit(1) from exc
    console.print(f"[green]ALIVE[/green] {output_file}")


@core_app.command("openapi")
def openapi(
    openapi_file: Path = typer.Argument(..., exists=True, readable=True),
    output_file: Path = typer.Option(Path("models.py"), "--output", "-o"),
) -> None:
    """Generate all OpenAPI component schemas without an LLM or network call."""

    try:
        generated = generate_openapi_models(openapi_file, output_file)
    except OpenAPIGenerationError as exc:
        console.print(f"[red]REFUSED:OPENAPI_NOT_ADMITTED[/red] {exc}")
        raise typer.Exit(2) from exc
    console.print(f"[green]ALIVE[/green] {generated}")


@app.command("status")
def status(
    as_json: bool = typer.Option(False, "--json"),
    strict: bool = typer.Option(False, "--strict"),
    include_alive: bool = typer.Option(False, "--all"),
) -> None:
    """Show per-capability import/mount standing and deterministic receipt IDs."""

    report = {name: registry.report() for name, registry in sorted(registries.items())}
    overall = "ALIVE" if all(item["standing"] == "ALIVE" for item in report.values()) else "PARTIAL_ALIVE"
    payload = {"standing": overall, "groups": report}
    if as_json:
        typer.echo(json.dumps(payload, indent=2, sort_keys=True))
    else:
        table = Table(title=f"Consolidated capability standing: {overall}")
        table.add_column("Capability")
        table.add_column("Group")
        table.add_column("Standing")
        table.add_column("Receipt")
        table.add_column("Evidence")
        for registry in registries.values():
            for receipt in registry.receipts:
                if not include_alive and receipt.standing is CapabilityStanding.ALIVE:
                    continue
                table.add_row(
                    receipt.name,
                    receipt.group,
                    receipt.standing.value,
                    receipt.receipt_id[:12],
                    receipt.reason or ("mounted" if receipt.mounted else "imported"),
                )
        console.print(table)
    if strict and any(registry.required_failures() for registry in registries.values()):
        raise typer.Exit(1)


registries["core"].mount_all(core_app, CORE_CAPABILITIES)
registries["validation"].mount_all(validation_app, VALIDATION_CAPABILITIES)
registries["development"].mount_all(development_app, DEVELOPMENT_CAPABILITIES)
registries["security"].mount_all(security_app, SECURITY_CAPABILITIES)
registries["telemetry"].mount_all(telemetry_app, TELEMETRY_CAPABILITIES)
registries["research"].mount_all(research_app, RESEARCH_CAPABILITIES)

core_app.add_typer(validation_app, name="validate")
core_app.add_typer(development_app, name="dev")
advanced_app.add_typer(security_app, name="security")
advanced_app.add_typer(telemetry_app, name="telemetry")
advanced_app.add_typer(research_app, name="research")
app.add_typer(core_app, name="core")
app.add_typer(advanced_app, name="advanced")


if __name__ == "__main__":
    app()
