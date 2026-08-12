from __future__ import annotations

import importlib
import tomllib
from pathlib import Path

from typer.testing import CliRunner

from dslmodel.cli import app
from dslmodel.commands.consolidated_cli import NON_ADMITTED_CAPABILITIES

ROOT = Path(__file__).resolve().parents[1]


def test_distribution_has_one_admitted_console_script() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert project["scripts"] == {"dsl": "dslmodel.cli:app"}
    module_name, attribute = project["scripts"]["dsl"].split(":", 1)
    assert getattr(importlib.import_module(module_name), attribute) is app


def test_legacy_command_families_are_explicitly_not_admitted() -> None:
    names = {item["name"] for item in NON_ADMITTED_CAPABILITIES}
    assert {"gen", "swarm", "telemetry", "redteam", "pqc", "ollama", "worktree"} <= names
    assert all(item["disposition"] == "NOT_ADMITTED" for item in NON_ADMITTED_CAPABILITIES)


def test_installed_cli_executes_strict_product_receipt() -> None:
    result = CliRunner().invoke(app, ["doctor", "--json", "--strict"])
    assert result.exit_code == 0, result.output
    assert '"standing": "ALIVE"' in result.output
