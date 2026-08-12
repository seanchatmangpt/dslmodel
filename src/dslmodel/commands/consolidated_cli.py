"""Canonical DSLModel command surface and capability inventory."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from dslmodel.capabilities import artifact_receipt, verify_artifact_receipt
from dslmodel.generators.openapi_models import OpenAPIGenerationError, generate_openapi_models
from dslmodel.selftest import run_selftests

console = Console()
app = typer.Typer(help="DSLModel — manufacture, validate, and receipt", no_args_is_help=True)
core_app = typer.Typer(help="Deterministic model manufacture")
evidence_app = typer.Typer(help="Artifact receipt and replay")

ADMITTED_CAPABILITIES: tuple[dict[str, str], ...] = (
    {"name": "core.openapi", "purpose": "OpenAPI 3 to executable Pydantic v2 manufacture"},
    {"name": "validate.selftest", "purpose": "Dependency-closed semantic self-play"},
    {"name": "evidence.receipt", "purpose": "Deterministic artifact identity and replay"},
    {"name": "system.status", "purpose": "Machine-readable aggregate standing"},
    {"name": "system.inventory", "purpose": "Capability and exclusion catalog"},
)

OPTIONAL_CAPABILITIES: tuple[dict[str, str], ...] = (
    {
        "name": "library.documents",
        "standing": "ALIVE_CORE_OPTIONAL_PDF",
        "purpose": "TXT/Markdown/DOCX/EPUB readers; PDF requires dslmodel[readers]",
    },
    {
        "name": "library.pqc",
        "standing": "ALIVE_WITH_EXTRA",
        "purpose": "ML-KEM + AES-256-GCM and ML-DSA; requires dslmodel[pqc]",
    },
    {
        "name": "library.verbs",
        "standing": "ALIVE",
        "purpose": "Composable JSON fetch/process/atomic-persist transformations",
    },
)

_RETIRED_NAMES = (
    "gen",
    "slidev",
    "forge",
    "auto",
    "swarm",
    "thesis",
    "demo",
    "capability",
    "validate",
    "validate-weaver",
    "validation-loop",
    "ollama",
    "ollama-auto",
    "disc-auto",
    "disc-integrated",
    "weaver",
    "weaver-health",
    "worktree",
    "swarm-worktree",
    "telemetry",
    "redteam",
    "agents",
    "evolve",
    "evolve-unified",
    "evolve-legacy",
    "auto-evolve",
    "evolve-worktree",
    "8020",
    "introspect",
    "weaver-diagrams",
    "weaver-loop",
    "weaver-multilayer",
    "otel-learn",
    "health-8020",
    "otel-monitor",
    "gap-8020",
    "5one",
    "otel",
    "forge-dx",
)

NON_ADMITTED_CAPABILITIES: tuple[dict[str, str], ...] = tuple(
    {
        "name": name,
        "disposition": "NOT_SHIPPED",
        "reason": "historical command, experimental integration, or external-runtime surface without current execution proof",
        "replacement": "dsl core openapi | dsl selftest | dsl evidence receipt | dsl status | dsl inventory",
    }
    for name in _RETIRED_NAMES
)


def _emit(payload: dict[str, Any], *, as_json: bool) -> None:
    if as_json:
        typer.echo(json.dumps(payload, indent=2, sort_keys=True))
        return
    console.print_json(data=payload)


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
    receipt = artifact_receipt(generated)
    console.print(f"[green]ALIVE[/green] {generated} sha256={receipt['digest']}")


@evidence_app.command("receipt")
def receipt(
    artifact: Path = typer.Argument(..., exists=True, readable=True),
    expected_digest: str | None = typer.Option(None, "--expect", help="Expected SHA-256 digest."),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    """Create a receipt or replay an expected artifact identity."""

    try:
        payload = artifact_receipt(artifact)
    except ValueError as exc:
        console.print(f"[red]REFUSED:ARTIFACT_NOT_ADMITTED[/red] {exc}")
        raise typer.Exit(2) from exc
    verified = expected_digest is None or verify_artifact_receipt(artifact, expected_digest)
    payload["standing"] = "ALIVE" if verified else "BUILD_BROKEN"
    payload["verified"] = verified
    _emit(payload, as_json=as_json)
    if not verified:
        raise typer.Exit(1)


@app.command("selftest")
def selftest(
    as_json: bool = typer.Option(False, "--json"),
    strict: bool = typer.Option(False, "--strict"),
) -> None:
    payload = run_selftests()
    _emit(payload, as_json=as_json)
    if strict and payload["standing"] != "ALIVE":
        raise typer.Exit(1)


@app.command("status")
def status(
    as_json: bool = typer.Option(False, "--json"),
    strict: bool = typer.Option(False, "--strict"),
) -> None:
    verification = run_selftests()
    payload = {
        "standing": verification["standing"],
        "admitted_count": len(ADMITTED_CAPABILITIES),
        "optional_count": len(OPTIONAL_CAPABILITIES),
        "non_admitted_count": len(NON_ADMITTED_CAPABILITIES),
        "checks": verification["checks"],
    }
    _emit(payload, as_json=as_json)
    if strict and payload["standing"] != "ALIVE":
        raise typer.Exit(1)


@app.command("inventory")
def inventory(as_json: bool = typer.Option(False, "--json")) -> None:
    payload = {
        "standing": "ALIVE",
        "admitted": list(ADMITTED_CAPABILITIES),
        "optional": list(OPTIONAL_CAPABILITIES),
        "non_admitted": list(NON_ADMITTED_CAPABILITIES),
    }
    if as_json:
        typer.echo(json.dumps(payload, indent=2, sort_keys=True))
        return

    admitted = Table(title="Admitted capabilities")
    admitted.add_column("Capability")
    admitted.add_column("Purpose")
    for item in ADMITTED_CAPABILITIES:
        admitted.add_row(item["name"], item["purpose"])
    console.print(admitted)

    optional = Table(title="Implemented optional libraries")
    optional.add_column("Capability")
    optional.add_column("Standing")
    optional.add_column("Purpose")
    for item in OPTIONAL_CAPABILITIES:
        optional.add_row(item["name"], item["standing"], item["purpose"])
    console.print(optional)
    console.print(f"Preserved but not shipped historical command surfaces: {len(NON_ADMITTED_CAPABILITIES)}")


app.add_typer(core_app, name="core")
app.add_typer(evidence_app, name="evidence")


if __name__ == "__main__":
    app()
