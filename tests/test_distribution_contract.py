from __future__ import annotations

import importlib
import tomllib
from pathlib import Path

from typer.testing import CliRunner

from dslmodel.cli import app
from dslmodel.commands.consolidated_cli import NON_ADMITTED_CAPABILITIES, OPTIONAL_CAPABILITIES

ROOT = Path(__file__).resolve().parents[1]


def project_config() -> dict:
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def test_distribution_has_one_admitted_console_script() -> None:
    project = project_config()["project"]
    assert project["scripts"] == {"dsl": "dslmodel.cli:app"}
    module_name, attribute = project["scripts"]["dsl"].split(":", 1)
    assert getattr(importlib.import_module(module_name), attribute) is app


def test_wheel_is_explicitly_bounded_to_audited_files() -> None:
    wheel = project_config()["tool"]["hatch"]["build"]["targets"]["wheel"]
    included = set(wheel["only-include"])
    assert "src/dslmodel/cli.py" in included
    assert "src/dslmodel/generators/openapi_models.py" in included
    assert "src/dslmodel/readers/doc_reader.py" in included
    assert "src/dslmodel/pqc/algorithms.py" in included
    assert "src/dslmodel/verbs.py" in included
    assert all(path.startswith("src/dslmodel/") for path in included)
    assert not any("swarm" in path or "evolution" in path or "ollama" in path for path in included)


def test_historical_command_families_are_explicitly_not_shipped() -> None:
    names = {item["name"] for item in NON_ADMITTED_CAPABILITIES}
    assert {"gen", "swarm", "telemetry", "redteam", "ollama", "worktree", "evolve"} <= names
    assert "pqc" not in names
    assert all(item["disposition"] == "NOT_SHIPPED" for item in NON_ADMITTED_CAPABILITIES)


def test_repaired_libraries_have_explicit_optional_standing() -> None:
    names = {item["name"] for item in OPTIONAL_CAPABILITIES}
    assert {"library.documents", "library.pqc", "library.verbs"} == names


def test_installed_cli_executes_strict_product_receipt() -> None:
    result = CliRunner().invoke(app, ["doctor", "--json", "--strict"])
    assert result.exit_code == 0, result.output
    assert '"standing": "ALIVE"' in result.output
