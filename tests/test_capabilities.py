from pathlib import Path
from types import ModuleType

import typer

from dslmodel.capabilities import (
    CapabilityRegistry,
    CapabilitySpec,
    CapabilityStanding,
    artifact_receipt,
    verify_artifact_receipt,
)


def _healthy_module() -> ModuleType:
    module = ModuleType("healthy")
    module.app = typer.Typer()

    @module.app.command("ping")
    def ping() -> None:
        typer.echo("pong")

    return module


def test_capabilities_are_admitted_independently() -> None:
    healthy = _healthy_module()

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
        CapabilitySpec(
            "healthy",
            "example.healthy",
            "healthy capability",
            verifier_args=(),
        ),
    )

    assert missing.standing is CapabilityStanding.UNSUPPORTED
    assert not missing.mounted
    assert admitted.standing is CapabilityStanding.ALIVE
    assert admitted.mounted
    assert admitted.executed
    assert admitted.exit_code == 0
    assert [group.name for group in parent.registered_groups] == ["healthy"]


def test_import_without_execution_is_only_partial_alive() -> None:
    registry = CapabilityRegistry(importer=lambda _: _healthy_module())
    receipt = registry.probe(CapabilitySpec("healthy", "example.healthy", "healthy"))

    assert receipt.standing is CapabilityStanding.PARTIAL_ALIVE
    assert receipt.imported
    assert not receipt.mounted
    assert not receipt.executed


def test_failing_verifier_is_build_broken() -> None:
    module = ModuleType("broken")
    module.app = typer.Typer()

    @module.app.command("fail")
    def fail() -> None:
        raise typer.Exit(7)

    registry = CapabilityRegistry(importer=lambda _: module)
    receipt = registry.mount(
        typer.Typer(),
        CapabilitySpec("broken", "example.broken", "broken", verifier_args=()),
    )

    assert receipt.standing is CapabilityStanding.BUILD_BROKEN
    assert receipt.executed
    assert receipt.exit_code == 7


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
    module = _healthy_module()
    registry = CapabilityRegistry(importer=lambda _: module)
    spec = CapabilitySpec("example", "example.module", "example", verifier_args=())

    first = registry.mount(typer.Typer(), spec)
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
    healthy = _healthy_module()

    def importer(name: str) -> ModuleType:
        if name == "example.healthy":
            return healthy
        error = ModuleNotFoundError("No module named 'missing_dep'")
        error.name = "missing_dep"
        raise error

    registry = CapabilityRegistry(importer=importer)
    registry.mount(
        typer.Typer(),
        CapabilitySpec("healthy", "example.healthy", "healthy", verifier_args=()),
    )
    registry.probe(CapabilitySpec("missing", "example.missing", "missing"))

    assert registry.report()["standing"] == "PARTIAL_ALIVE"


def test_artifact_receipt_replays_and_detects_drift(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.txt"
    artifact.write_text("alive\n", encoding="utf-8")

    first = artifact_receipt(artifact)
    second = artifact_receipt(artifact)
    assert first == second
    assert verify_artifact_receipt(artifact, str(first["digest"]))

    artifact.write_text("changed\n", encoding="utf-8")
    assert not verify_artifact_receipt(artifact, str(first["digest"]))


def test_artifact_identity_is_transport_independent(tmp_path: Path) -> None:
    first = tmp_path / "first.txt"
    second = tmp_path / "nested" / "second.txt"
    second.parent.mkdir()
    first.write_text("same bytes\n", encoding="utf-8")
    second.write_text("same bytes\n", encoding="utf-8")

    assert artifact_receipt(first)["receipt_id"] == artifact_receipt(second)["receipt_id"]
