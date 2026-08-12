from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "audit_vacuity.py"
spec = importlib.util.spec_from_file_location("audit_vacuity", SCRIPT)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def kinds(source: str) -> set[str]:
    return {finding[2] for finding in module.python_findings(source)}


def test_abstract_methods_are_not_vacuous() -> None:
    source = """
from abc import abstractmethod
class Port:
    @abstractmethod
    def execute(self):
        pass
"""
    assert "pass_body" not in kinds(source)


def test_pass_and_not_implemented_are_detected() -> None:
    source = """
def one():
    pass

def two():
    raise NotImplementedError('later')
"""
    found = kinds(source)
    assert "pass_body" in found
    assert "not_implemented" in found


def test_constant_status_and_empty_returns_are_detected() -> None:
    source = """
def status():
    return 'success'

def load():
    return {}
"""
    found = kinds(source)
    assert "constant_status_return" in found
    assert "empty_container_return" in found


def test_swallowed_exception_is_detected() -> None:
    source = """
def risky():
    try:
        int('x')
    except ValueError:
        pass
"""
    assert "swallowed_exception" in kinds(source)


def test_generated_and_test_paths_are_classified() -> None:
    assert module.classify_path("src/dslmodel/generated/models/x.py") == "GENERATED_PROJECTION"
    assert module.classify_path("tests/test_x.py") == "TEST_FIXTURE"
    assert module.classify_path("src/dslmodel/core.py") == "ACTIONABLE"
