"""DSLModel CLI with independently admitted capability surfaces."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from dslmodel.capabilities import (
    CapabilityRegistry,
    CapabilitySpec,
    CapabilityStanding,
)
from dslmodel.generators.openapi_models import (
    OpenAPIGenerationError,
    generate_openapi_models,
)

console = Console()
app = typer.Typer(
    help="DSLModel — deterministic model manufacture and independently admitted capabilities.",
    no_args_is_help=True,
)
registry = CapabilityRegistry()


ROOT_CAPABILITIES = (
    CapabilitySpec("dsl", "dslmodel.commands.consolidated_cli", "Consolidated ERRC command surface", group="core", required=True),
    CapabilitySpec("slidev", "dslmodel.commands.slidev", "Slidev presentation tools", group="research"),
    CapabilitySpec("forge", "dslmodel.commands.forge", "Weaver Forge workflow commands", group="development"),
    CapabilitySpec("auto", "dslmodel.commands.autonomous", "Autonomous Decision Engine", group="agents"),
    CapabilitySpec("swarm", "dslmodel.commands.swarm", "SwarmAgent coordination", group="agents"),
    CapabilitySpec("thesis", "dslmodel.commands.thesis_cli", "SwarmSH thesis tools", group="research"),
    CapabilitySpec("demo", "dslmodel.commands.demo", "Full-cycle demonstrations", group="core"),
    CapabilitySpec("capability", "dslmodel.commands.capability_map", "Capability mapping", group="research"),
    CapabilitySpec("validate", "dslmodel.commands.validate_otel", "OpenTelemetry validation", group="validation"),
    CapabilitySpec("validate-weaver", "dslmodel.commands.validate_weaver", "Weaver validation", group="validation"),
    CapabilitySpec("validation-loop", "dslmodel.commands.validation_loop", "Continuous validation", group="validation"),
    CapabilitySpec("ollama", "dslmodel.commands.ollama_validate", "Ollama validation", group="runtime"),
    CapabilitySpec("ollama-auto", "dslmodel.commands.ollama_autonomous", "Autonomous Ollama repair", group="runtime"),
    CapabilitySpec("disc-auto", "dslmodel.commands.disc_autonomous", "DISC compensation", group="agents"),
    CapabilitySpec("disc-integrated", "dslmodel.commands.disc_integrated_auto", "DISC-integrated decisions", group="agents"),
    CapabilitySpec("weaver", "dslmodel.commands.weaver", "Weaver semantic conventions", group="development"),
    CapabilitySpec("weaver-health", "dslmodel.commands.weaver_health_check", "Weaver health checks", group="validation"),
    CapabilitySpec("worktree", "dslmodel.commands.worktree", "Git worktree management", group="development"),
    CapabilitySpec("swarm-worktree", "dslmodel.commands.swarm_worktree", "Swarm worktree coordination", group="agents"),
    CapabilitySpec("telemetry", "dslmodel.commands.telemetry_cli", "Telemetry monitoring", group="telemetry"),
    CapabilitySpec("redteam", "dslmodel.commands.redteam", "Security validation", group="security"),
    CapabilitySpec("agents", "dslmodel.commands.agent_coordination_cli", "Agent coordination", group="agents"),
    CapabilitySpec("evolve", "dslmodel.commands.unified_8020_evolution", "Unified 80/20 evolution", group="evolution"),
    CapabilitySpec("evolve-unified", "dslmodel.commands.unified_evolution_cli", "Unified evolution", group="evolution"),
    CapabilitySpec("evolve-legacy", "dslmodel.commands.evolution", "Legacy evolution", group="evolution"),
    CapabilitySpec("auto-evolve", "dslmodel.commands.auto_evolution", "Automatic evolution", group="evolution"),
    CapabilitySpec("evolve-worktree", "dslmodel.commands.evolution_worktree", "Worktree evolution", group="evolution"),
    CapabilitySpec("8020", "dslmodel.commands.complete_8020_validation", "Complete 80/20 validation", group="validation"),
    CapabilitySpec("introspect", "dslmodel.commands.system_introspection", "System introspection", group="research"),
    CapabilitySpec("weaver-diagrams", "dslmodel.commands.weaver_diagrams", "Weaver diagrams", group="research"),
    CapabilitySpec("weaver-loop", "dslmodel.commands.weaver_autonomous_loop", "Weaver autonomous loop", group="evolution"),
    CapabilitySpec("weaver-multilayer", "dslmodel.commands.multilayer_weaver_feedback", "Multilayer Weaver feedback", group="evolution"),
    CapabilitySpec("otel-learn", "dslmodel.commands.otel_learning_engine", "OTEL learning", group="telemetry"),
    CapabilitySpec("health-8020", "dslmodel.commands.health_8020_improvement", "80/20 health improvement", group="validation"),
    CapabilitySpec("otel-monitor", "dslmodel.commands.claude_code_otel_monitoring", "Claude Code OTEL monitoring", group="telemetry"),
    CapabilitySpec("gap-8020", "dslmodel.commands.gap_analysis_8020", "80/20 gap analysis", group="validation"),
    CapabilitySpec("5one", "dslmodel.commands.swarm_sh_5one", "Swarm SH 5-ONE", group="agents"),
    CapabilitySpec("pqc", "dslmodel.commands.pqc", "Post-quantum cryptography", group="security"),
    CapabilitySpec("otel", "dslmodel.commands.otel_coordination_cli", "OTEL coordination", group="telemetry"),
    CapabilitySpec("forge-dx", "dslmodel.commands.weaver_forge_dx_loop", "Forge developer-experience loop", group="development"),
)


@app.callback()
def main(
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable output where supported."),
) -> None:
    """Initialize the DSLModel command surface without importing optional capabilities globally."""

    if json_output:
        os.environ["DSLMODEL_JSON"] = "1"
        try:
            from dslmodel.utils.json_output import set_json_mode
        except (ImportError, ModuleNotFoundError):
            return
        set_json_mode(True)


@app.command("gen")
def generate_class(
    prompt: str = typer.Argument(..., help="Natural-language model description."),
    output_dir: Path = typer.Option(Path.cwd(), "--output-dir", help="Destination directory."),
    file_format: str = typer.Option("py", "--file-format", help="Generated file format."),
    config: Path | None = typer.Option(None, "--config", help="Optional generator configuration."),
    model: Annotated[str, typer.Option("--model", help="Language model identifier.")] = "groq/llama-3.2-90b-text-preview",
) -> None:
    """Generate DSLModel classes through the existing LLM-backed generator."""

    try:
        from dslmodel.generators.gen_dslmodel_class import generate_and_save_dslmodel
        from dslmodel.utils.dspy_tools import init_lm
    except (ImportError, ModuleNotFoundError) as exc:
        console.print(f"[red]REFUSED:GENERATOR_UNAVAILABLE[/red] {exc}")
        raise typer.Exit(2) from exc

    output_dir.mkdir(parents=True, exist_ok=True)
    init_lm(model=model)
    try:
        _, output_file = generate_and_save_dslmodel(prompt, output_dir, file_format, config)
    except Exception as exc:
        console.print(f"[red]BUILD_BROKEN[/red] {exc}")
        raise typer.Exit(1) from exc
    console.print(f"[green]ALIVE[/green] {output_file}")


@app.command("openapi")
def openapi(
    openapi_file: Path = typer.Argument(..., exists=True, readable=True, help="OpenAPI JSON or YAML document."),
    output_file: Path = typer.Option(Path("models.py"), "--output", "-o", help="Generated Python module."),
) -> None:
    """Generate all component schemas as deterministic Pydantic v2 models."""

    try:
        generated = generate_openapi_models(openapi_file, output_file)
    except OpenAPIGenerationError as exc:
        console.print(f"[red]REFUSED:OPENAPI_NOT_ADMITTED[/red] {exc}")
        raise typer.Exit(2) from exc
    console.print(f"[green]ALIVE[/green] {generated}")


@app.command("doctor")
def doctor(
    as_json: bool = typer.Option(False, "--json", help="Emit JSON receipts."),
    strict: bool = typer.Option(False, "--strict", help="Fail when a required capability is not ALIVE."),
    include_alive: bool = typer.Option(False, "--all", help="Show ALIVE capabilities as well as failures."),
) -> None:
    """Report exact import and mount standing for every advertised command."""

    report = registry.report()
    if as_json or os.getenv("DSLMODEL_JSON") == "1":
        typer.echo(json.dumps(report, indent=2, sort_keys=True))
    else:
        table = Table(title=f"DSLModel capability standing: {report['standing']}")
        table.add_column("Capability")
        table.add_column("Group")
        table.add_column("Standing")
        table.add_column("Evidence")
        for receipt in registry.receipts:
            if not include_alive and receipt.standing is CapabilityStanding.ALIVE:
                continue
            evidence = receipt.reason or ("mounted" if receipt.mounted else "imported")
            table.add_row(receipt.name, receipt.group, receipt.standing.value, evidence)
        console.print(table)
        counts = ", ".join(f"{key}={value}" for key, value in report["counts"].items() if value)
        console.print(counts)
    if strict and registry.required_failures():
        raise typer.Exit(1)


registry.mount_all(app, ROOT_CAPABILITIES)


if __name__ == "__main__":
    app()
