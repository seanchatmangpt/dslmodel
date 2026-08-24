"""DSLModel generator exports with side-effect-free lazy loading."""

from __future__ import annotations

from importlib import import_module
from typing import Any

__all__ = [
    "gen_bool",
    "gen_dict",
    "gen_float",
    "gen_int",
    "gen_list",
    "gen_str",
    "IPythonNotebookGenerator",
]

_EXPORTS: dict[str, tuple[str, str]] = {
    "gen_bool": ("dslmodel.generators.gen_python_primitive", "gen_bool"),
    "gen_dict": ("dslmodel.generators.gen_python_primitive", "gen_dict"),
    "gen_float": ("dslmodel.generators.gen_python_primitive", "gen_float"),
    "gen_int": ("dslmodel.generators.gen_python_primitive", "gen_int"),
    "gen_list": ("dslmodel.generators.gen_python_primitive", "gen_list"),
    "gen_str": ("dslmodel.generators.gen_python_primitive", "gen_str"),
    "IPythonNotebookGenerator": (
        "dslmodel.generators.notebook_generator",
        "IPythonNotebookGenerator",
    ),
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
