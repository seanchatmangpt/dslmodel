"""DSLModel canonical CLI with execution-backed capability standing."""

from __future__ import annotations

import json
import os
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from dslmodel.capabilities import (
    CapabilityRegistry,
    CapabilitySpec,
    CapabilityStanding,
    artifact_receipt,
    verify_artifact_receipt,
)
from dslmodel.generators.openapi_models import OpenAPIGenerationError, generate_openapi_models
from dslmodel.selftest import run_selftests

console = Console()
app = typer.Typer(
    help="DSLModel — deterministic model manufacture with execution receipts.",
    no_args_is_help=True,
)
registry = CapabilityRegistry()

ROOT_CAPABILITIES = (
    CapabilitySpec(
        "dsl",
        "dslmodel.commands.consolidated_cli",
        "Canonical 80/20 command surface",
        group="core",
        required=True,
        verifier_args=("selftest", "--json", "--strict"),
    ),
)


@app.callback()
def main(
    json_output: bool = typer.Option(False, "--json", help="Emit machine-readable output where supported."),
) -> None:
    """Initialize the dependency-closed DSLModel command surface."""

    if json_output:
        os.environ["DSLMODEL_JSON"] = "1"


@app.command("openapi")
def openapi(
    openapi_file: Path = typer.Argument(..., exists=True, readable=True, help="OpenAPI JSON or YAML document."),
    output_file: Path = typer.Option(Path("models.py"), "--output", "-o", help="Generated Python module."),
) -> None:
    """Generate executable Pydantic v2 models and emit their artifact digest."""

    try:
        generated = generate_openapi_models(openapi_file, output_file)
    except OpenAPIGenerationError as exc:
        console.print(f"[red]REFUSED:OPENAPI_NOT_ADMITTED[/red] {exc}")
        raise typer.Exit(2) from exc
    receipt = artifact_receipt(generated)
    console.print(f"[green]ALIVE[/green] {generated} sha256={receipt['digest']}")


@app.command("receipt")
def receipt(
    artifact: Path = typer.Argument(..., exists=True, readable=True),
    expected_digest: str | None = typer.Option(None, "--expect"),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    """Create or replay a deterministic SHA-256 artifact receipt."""

    try:
        payload = artifact_receipt(artifact)
    except ValueError as exc:
        console.print(f"[red]REFUSED:ARTIFACT_NOT_ADMITTED[/red] {exc}")
        raise typer.Exit(2) from exc
    verified = expected_digest is None or verify_artifact_receipt(artifact, expected_digest)
    payload.update({"standing": "ALIVE" if verified else "BUILD_BROKEN", "verified": verified})
    if as_json or os.getenv("DSLMODEL_JSON") == "1":
        typer.echo(json.dumps(payload, indent=2, sort_keys=True))
    else:
        console.print_json(data=payload)
    if not verified:
        raise typer.Exit(1)


@app.command("selftest")
def selftest(
    as_json: bool = typer.Option(False, "--json"),
    strict: bool = typer.Option(False, "--strict"),
) -> None:
    """Execute dependency-closed semantic self-play."""

    payload = run_selftests()
    if as_json or os.getenv("DSLMODEL_JSON") == "1":
        typer.echo(json.dumps(payload, indent=2, sort_keys=True))
    else:
        console.print_json(data=payload)
    if strict and payload["standing"] != CapabilityStanding.ALIVE.value:
        raise typer.Exit(1)


@app.command("doctor")
def doctor(
    as_json: bool = typer.Option(False, "--json", help="Emit JSON receipts."),
    strict: bool = typer.Option(False, "--strict", help="Fail unless the complete admitted surface is ALIVE."),
    include_alive: bool = typer.Option(False, "--all", help="Show ALIVE capabilities in table output."),
) -> None:
    """Execute and report standing for every admitted command and semantic check."""

    capability_report = registry.report()
    semantic_report = run_selftests()
    overall = (
        CapabilityStanding.ALIVE.value
        if capability_report["standing"] == CapabilityStanding.ALIVE.value
        and semantic_report["standing"] == CapabilityStanding.ALIVE.value
        else CapabilityStanding.BUILD_BROKEN.value
    )
    report = {
        "standing": overall,
        "capability_registry": capability_report,
        "semantic_checks": semantic_report["checks"],
    }
    if as_json or os.getenv("DSLMODEL_JSON") == "1":
        typer.echo(json.dumps(report, indent=2, sort_keys=True))
    else:
        table = Table(title=f"DSLModel admitted standing: {overall}")
        table.add_column("Capability")
        table.add_column("Standing")
        table.add_column("Executed")
        table.add_column("Evidence")
        for item in capability_report["capabilities"]:
            if not include_alive and item["standing"] == CapabilityStanding.ALIVE.value:
                continue
            table.add_row(
                str(item["name"]),
                str(item["standing"]),
                str(item["executed"]),
                str(item["reason"]),
            )
        for item in semantic_report["checks"]:
            if not include_alive and item["standing"] == CapabilityStanding.ALIVE.value:
                continue
            table.add_row(
                str(item["name"]),
                str(item["standing"]),
                "True",
                str(item["evidence"]),
            )
        console.print(table)
    if strict and overall != CapabilityStanding.ALIVE.value:
        raise typer.Exit(1)


registry.mount_all(app, ROOT_CAPABILITIES)


if __name__ == "__main__":
    app()
