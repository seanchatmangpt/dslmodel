from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


SCRIPT = Path(__file__).parents[1] / "scripts" / "audit_vacuity.py"
spec = importlib.util.spec_from_file_location("audit_vacuity", SCRIPT)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
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


def test_randomized_validation_is_critical() -> None:
    source = """
import random
def validate_candidate():
    return random.uniform(0.7, 1.0) > 0.8
"""
    assert "randomized_validation" in kinds(source)


def test_arbitrary_literals_do_not_trigger_comment_markers() -> None:
    source = '''
def explain():
    return "This string discusses a mock implementation but is data, not an implementation marker"
'''
    assert "mock_implementation" not in kinds(source)


def test_admission_classifies_shipped_canonical_separately_from_history() -> None:
    shipped = {"src/dslmodel/core.py"}
    canonical = "agent/crown"
    assert module.classify_path("src/dslmodel/core.py", canonical, canonical, shipped) == "ACTIONABLE"
    assert (
        module.classify_path("src/dslmodel/legacy.py", canonical, canonical, shipped)
        == "PRESERVED_NOT_SHIPPED"
    )
    assert (
        module.classify_path("src/dslmodel/core.py", "old-branch", canonical, shipped)
        == "HISTORICAL_BRANCH"
    )


def test_generated_and_test_paths_are_non_product_dispositions() -> None:
    shipped = {"src/dslmodel/generated/models/x.py"}
    canonical = "main"
    assert (
        module.classify_path("src/dslmodel/generated/models/x.py", canonical, canonical, shipped)
        == "GENERATED_PROJECTION"
    )
    assert module.classify_path("tests/test_x.py", canonical, canonical, shipped) == "TEST_FIXTURE"
