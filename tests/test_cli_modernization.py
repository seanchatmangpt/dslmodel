from __future__ import annotations

import json
from pathlib import Path
import sys

from typer.testing import CliRunner


runner = CliRunner()


def test_package_import_has_no_dspy_side_effect() -> None:
    sys.modules.pop("dslmodel.utils.dspy_tools", None)
    import dslmodel

    assert "dslmodel.utils.dspy_tools" not in sys.modules
    assert "DSLModel" in dir(dslmodel)


def test_root_help_contains_only_canonical_surface() -> None:
    from dslmodel.cli import app

    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0, result.output
    for command in ("doctor", "openapi", "receipt", "selftest", "dsl"):
        assert command in result.output
    for retired in ("ollama-auto", "weaver-loop", "evolve-legacy", "forge-dx"):
        assert retired not in result.output


def test_root_doctor_is_strictly_alive_and_execution_backed() -> None:
    from dslmodel.cli import app

    result = runner.invoke(app, ["doctor", "--json", "--strict"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["standing"] == "ALIVE"
    capabilities = payload["capability_registry"]["capabilities"]
    assert [item["name"] for item in capabilities] == ["dsl"]
    assert capabilities[0]["standing"] == "ALIVE"
    assert capabilities[0]["mounted"] is True
    assert capabilities[0]["executed"] is True
    assert capabilities[0]["exit_code"] == 0
    assert all(item["standing"] == "ALIVE" for item in payload["semantic_checks"])


def test_consolidated_cli_is_strictly_alive() -> None:
    from dslmodel.commands.consolidated_cli import app

    help_result = runner.invoke(app, ["--help"])
    assert help_result.exit_code == 0, help_result.output
    for command in ("core", "evidence", "selftest", "status", "inventory"):
        assert command in help_result.output

    status = runner.invoke(app, ["status", "--json", "--strict"])
    assert status.exit_code == 0, status.output
    payload = json.loads(status.output)
    assert payload["standing"] == "ALIVE"
    assert payload["admitted_count"] == 5
    assert payload["non_admitted_count"] >= 40
    assert all(item["standing"] == "ALIVE" for item in payload["checks"])


def test_inventory_preserves_retired_surface_without_admitting_it() -> None:
    from dslmodel.commands.consolidated_cli import app

    result = runner.invoke(app, ["inventory", "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["standing"] == "ALIVE"
    assert {item["name"] for item in payload["admitted"]} == {
        "core.openapi",
        "validate.selftest",
        "evidence.receipt",
        "system.status",
        "system.inventory",
    }
    retired = {item["name"]: item for item in payload["non_admitted"]}
    assert retired["gen"]["disposition"] == "NOT_ADMITTED"
    assert retired["pqc"]["disposition"] == "NOT_ADMITTED"
    assert retired["forge-dx"]["replacement"].startswith("dsl core openapi")


def test_openapi_cli_generates_executable_models_and_receipt(tmp_path: Path) -> None:
    from dslmodel.cli import app

    schema = tmp_path / "openapi.yaml"
    output = tmp_path / "models.py"
    schema.write_text(
        """
openapi: 3.1.0
info: {title: test, version: '1'}
components:
  schemas:
    Pet:
      type: object
      required: [name]
      properties:
        name: {type: string, minLength: 1}
        age: {type: integer, minimum: 0}
""".strip(),
        encoding="utf-8",
    )

    result = runner.invoke(app, ["openapi", str(schema), "--output", str(output)])
    assert result.exit_code == 0, result.output
    assert "ALIVE" in result.output
    assert "sha256=" in result.output
    assert output.exists()
    compile(output.read_text(encoding="utf-8"), str(output), "exec")


def test_receipt_cli_replays_identity(tmp_path: Path) -> None:
    from dslmodel.cli import app

    artifact = tmp_path / "artifact.txt"
    artifact.write_text("receipt\n", encoding="utf-8")
    created = runner.invoke(app, ["receipt", str(artifact), "--json"])
    assert created.exit_code == 0, created.output
    payload = json.loads(created.output)
    assert payload["standing"] == "ALIVE"

    replay = runner.invoke(app, ["receipt", str(artifact), "--expect", payload["digest"], "--json"])
    assert replay.exit_code == 0, replay.output
    assert json.loads(replay.output)["verified"] is True

    refused = runner.invoke(app, ["receipt", str(artifact), "--expect", "0" * 64, "--json"])
    assert refused.exit_code == 1
    assert json.loads(refused.output)["standing"] == "BUILD_BROKEN"
