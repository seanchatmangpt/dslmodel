"""DSLModel command modules.

Command modules are imported lazily so one unavailable optional dependency cannot
prevent unrelated commands or ``dsl --help`` from starting.
"""

from __future__ import annotations

from importlib import import_module
from types import ModuleType

_COMMAND_MODULES = {
    "agent_coordination_cli",
    "asyncapi",
    "auto_evolution",
    "autonomous",
    "capability_map",
    "claude_code_otel_monitoring",
    "complete_8020_validation",
    "consolidated_cli",
    "coordination_cli",
    "demo",
    "disc_autonomous",
    "disc_integrated_auto",
    "evolution",
    "evolution_worktree",
    "forge",
    "gap_analysis_8020",
    "git_auto_cli",
    "health_8020_improvement",
    "multilayer_weaver_feedback",
    "ollama_autonomous",
    "ollama_validate",
    "otel_coordination_cli",
    "otel_learning_engine",
    "pqc",
    "redteam",
    "slidev",
    "swarm",
    "swarm_sh_5one",
    "swarm_worktree",
    "system_introspection",
    "telemetry_cli",
    "thesis_cli",
    "transformation_cli",
    "unified_8020_evolution",
    "unified_evolution_cli",
    "validate_otel",
    "validate_weaver",
    "validation_loop",
    "weaver",
    "weaver_autonomous_loop",
    "weaver_diagrams",
    "weaver_forge_dx_loop",
    "weaver_health_check",
    "worktree",
}

__all__ = sorted(_COMMAND_MODULES)


def __getattr__(name: str) -> ModuleType:
    if name not in _COMMAND_MODULES:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = import_module(f"{__name__}.{name}")
    globals()[name] = module
    return module


def __dir__() -> list[str]:
    return sorted(set(globals()) | _COMMAND_MODULES)
