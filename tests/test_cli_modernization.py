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


def test_root_help_survives_missing_optional_capabilities() -> None:
    from dslmodel.cli import app

    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0, result.output
    assert "doctor" in result.output
    assert "openapi" in result.output
    assert "dsl" in result.output


def test_root_doctor_emits_machine_readable_receipts() -> None:
    from dslmodel.cli import app

    result = runner.invoke(app, ["doctor", "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["standing"] in {"ALIVE", "PARTIAL_ALIVE"}
    assert payload["capabilities"]
    assert all(len(item["receipt_id"]) == 64 for item in payload["capabilities"])


def test_consolidated_cli_has_real_grouped_surface() -> None:
    from dslmodel.commands.consolidated_cli import app

    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0, result.output
    assert "core" in result.output
    assert "advanced" in result.output
    assert "status" in result.output

    status = runner.invoke(app, ["status", "--json"])
    assert status.exit_code == 0, status.output
    payload = json.loads(status.output)
    assert set(payload["groups"]) == {
        "core",
        "development",
        "research",
        "security",
        "telemetry",
        "validation",
    }


def test_openapi_cli_generates_executable_models(tmp_path: Path) -> None:
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
    assert output.exists()
    compile(output.read_text(encoding="utf-8"), str(output), "exec")
