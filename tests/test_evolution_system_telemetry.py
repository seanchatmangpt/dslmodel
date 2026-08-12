from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

import pytest


MODULE_PATH = Path(__file__).parents[1] / "src" / "dslmodel" / "evolution_forge" / "evolution_system.py"
spec = importlib.util.spec_from_file_location("evolution_system_under_test", MODULE_PATH)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

EvolutionSystem = module.EvolutionSystem
EvolutionTelemetryError = module.EvolutionTelemetryError


def test_typed_emit_produces_local_execution_receipt() -> None:
    system = EvolutionSystem()
    receipt = system.emit_analyze("session-1", "static", 3)
    assert receipt.operation == "analyze"
    assert receipt.span_name == "dslmodel.evolution.analyze"
    assert receipt.attributes["evolution.session_id"] == "session-1"
    assert receipt.attributes["evolution.issues_found"] == 3
    assert receipt.receipt_id
    status = system.get_status()
    assert status["emissions_observed"] == 1
    assert status["last_receipt_id"] == receipt.receipt_id
    assert status["exporter_delivery"] == "UNKNOWN"


def test_run_requires_explicit_operation_config(tmp_path: Path) -> None:
    system = EvolutionSystem()
    assert system.run()["standing"] == "REFUSED"

    config = tmp_path / "event.json"
    config.write_text(
        json.dumps(
            {
                "operation": "validate",
                "session_id": "session-2",
                "attributes": {
                    "evolution.improvement_id": "candidate-1",
                    "evolution.validation_type": "pytest",
                    "evolution.validation_result": "passed",
                },
            }
        ),
        encoding="utf-8",
    )
    result = system.run(config)
    assert result["success"] is True
    assert result["standing"] == "ALIVE"
    assert result["emission"]["operation"] == "validate"
    assert result["exporter_delivery"] == "UNKNOWN"


def test_invalid_semantic_value_is_refused() -> None:
    system = EvolutionSystem()
    with pytest.raises(EvolutionTelemetryError, match="between 0 and 1"):
        system.emit_learn("session", 4, 1.5)
