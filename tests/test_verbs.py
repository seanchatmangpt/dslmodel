from __future__ import annotations

import json
from pathlib import Path

import pytest

from dslmodel.verbs import DSLVerb, ProcessData, SaveToFile, ValueVerb, VerbExecutionError


class AddField(DSLVerb):
    def __init__(self, key: str, value: object) -> None:
        super().__init__()
        self.key = key
        self.value_to_add = value

    def __call__(self, context):
        context[self.key] = self.value_to_add
        return context


class ObserveField(DSLVerb):
    def __init__(self, key: str) -> None:
        super().__init__()
        self.key = key

    def __call__(self, context):
        context["observed"] = context[self.key]
        return context


def test_composition_passes_first_result_to_second() -> None:
    context: dict[str, object] = {}
    result = (AddField("answer", 42) | ObserveField("answer"))(context)
    assert result is context
    assert result["observed"] == 42


def test_base_verb_is_abstract() -> None:
    with pytest.raises(TypeError):
        DSLVerb()


def test_bind_returns_executable_value_verb() -> None:
    value = ValueVerb(21).bind(lambda item: item * 2)
    assert value({})["value"] == 42


def test_process_data_rejects_non_object_lists() -> None:
    with pytest.raises(VerbExecutionError, match="JSON objects"):
        ProcessData()({"data": [1, 2, 3]})


def test_process_and_save_pipeline(tmp_path: Path) -> None:
    output = tmp_path / "nested" / "output.json"
    context = {
        "data": [{"keep": 1, "drop": 0}, {"keep": "yes", "drop": ""}],
        "file_path": str(output),
    }
    result = (ProcessData() | SaveToFile())(context)
    assert result["saved_file"] == str(output)
    assert json.loads(output.read_text(encoding="utf-8")) == [{"keep": 1}, {"keep": "yes"}]
