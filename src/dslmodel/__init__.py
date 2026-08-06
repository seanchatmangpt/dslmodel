"""DSLModel public API with side-effect-free lazy exports."""

from __future__ import annotations

from importlib import import_module
from typing import Any

__all__ = [
    "DSLModel",
    "DataReader",
    "DataWriter",
    "Field",
    "from_prompt_chain",
    "init_instant",
    "init_lm",
    "init_log",
    "init_text",
    "log_critical",
    "log_debug",
    "log_error",
    "log_exception",
    "log_info",
    "log_warning",
    "logger",
    "render",
    "run_dsls",
]

_EXPORTS: dict[str, tuple[str, str]] = {
    "DSLModel": ("dslmodel.dsl_models", "DSLModel"),
    "DataReader": ("dslmodel.readers.data_reader", "DataReader"),
    "DataWriter": ("dslmodel.writers.data_writer", "DataWriter"),
    "Field": ("pydantic", "Field"),
    "from_prompt_chain": ("dslmodel.utils.model_tools", "from_prompt_chain"),
    "init_instant": ("dslmodel.utils.dspy_tools", "init_instant"),
    "init_lm": ("dslmodel.utils.dspy_tools", "init_lm"),
    "init_log": ("dslmodel.utils.log_tools", "init_log"),
    "init_text": ("dslmodel.utils.dspy_tools", "init_text"),
    "log_critical": ("dslmodel.utils.log_tools", "log_critical"),
    "log_debug": ("dslmodel.utils.log_tools", "log_debug"),
    "log_error": ("dslmodel.utils.log_tools", "log_error"),
    "log_exception": ("dslmodel.utils.log_tools", "log_exception"),
    "log_info": ("dslmodel.utils.log_tools", "log_info"),
    "log_warning": ("dslmodel.utils.log_tools", "log_warning"),
    "logger": ("dslmodel.utils.log_tools", "logger"),
    "render": ("dslmodel.template", "render"),
    "run_dsls": ("dslmodel.utils.model_tools", "run_dsls"),
}


def __getattr__(name: str) -> Any:
    try:
        module_name, attribute = _EXPORTS[name]
    except KeyError as exc:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc
    value = getattr(import_module(module_name), attribute)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
