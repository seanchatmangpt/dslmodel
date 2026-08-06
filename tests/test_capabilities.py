from types import ModuleType

import typer

from dslmodel.capabilities import (
    CapabilityRegistry,
    CapabilitySpec,
    CapabilityStanding,
)


def test_capabilities_are_admitted_independently() -> None:
    healthy = ModuleType("healthy")
    healthy.app = typer.Typer()

    def importer(name: str) -> ModuleType:
        if name == "example.healthy":
            return healthy
        error = ModuleNotFoundError("No module named 'optional_dependency'")
        error.name = "optional_dependency"
        raise error

    registry = CapabilityRegistry(importer=importer)
    parent = typer.Typer()
    missing = registry.mount(
        parent,
        CapabilitySpec("missing", "example.missing", "missing capability"),
    )
    admitted = registry.mount(
        parent,
        CapabilitySpec("healthy", "example.healthy", "healthy capability"),
    )

    assert missing.standing is CapabilityStanding.UNSUPPORTED
    assert not missing.mounted
    assert admitted.standing is CapabilityStanding.ALIVE
    assert admitted.mounted
    assert [group.name for group in parent.registered_groups] == ["healthy"]


def test_internal_missing_module_is_build_broken() -> None:
    def importer(name: str) -> ModuleType:
        error = ModuleNotFoundError(f"No module named {name!r}")
        error.name = name
        raise error

    registry = CapabilityRegistry(importer=importer)
    receipt = registry.probe(CapabilitySpec("broken", "dslmodel.commands.broken", "broken"))

    assert receipt.standing is CapabilityStanding.BUILD_BROKEN
    assert receipt.missing_dependency == "dslmodel.commands.broken"


def test_receipt_identity_is_deterministic() -> None:
    module = ModuleType("example")
    module.app = typer.Typer()
    registry = CapabilityRegistry(importer=lambda _: module)
    spec = CapabilitySpec("example", "example.module", "example")

    first = registry.probe(spec)
    second = registry.probe(spec)

    assert first.receipt_id == second.receipt_id
    assert len(first.receipt_id) == 64


def test_required_failure_controls_registry_standing() -> None:
    def importer(name: str) -> ModuleType:
        error = ModuleNotFoundError("No module named 'missing_dep'")
        error.name = "missing_dep"
        raise error

    registry = CapabilityRegistry(importer=importer)
    registry.probe(CapabilitySpec("required", "example.required", "required", required=True))

    report = registry.report()
    assert report["standing"] == "UNSUPPORTED"
    assert report["required_failures"][0]["name"] == "required"


def test_registry_aggregate_never_crowns_partial_surface() -> None:
    healthy = ModuleType("healthy")
    healthy.app = typer.Typer()

    def importer(name: str) -> ModuleType:
        if name == "example.healthy":
            return healthy
        error = ModuleNotFoundError("No module named 'missing_dep'")
        error.name = "missing_dep"
        raise error

    registry = CapabilityRegistry(importer=importer)
    registry.mount(typer.Typer(), CapabilitySpec("healthy", "example.healthy", "healthy"))
    registry.probe(CapabilitySpec("missing", "example.missing", "missing"))

    assert registry.report()["standing"] == "PARTIAL_ALIVE"
