"""Dependency-closed 80/20 execution verifier for DSLModel."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import ModuleType
from typing import Callable

import typer

from dslmodel.capabilities import (
    CapabilityRegistry,
    CapabilitySpec,
    CapabilityStanding,
    artifact_receipt,
    verify_artifact_receipt,
)
from dslmodel.generators.openapi_models import generate_openapi_models


@dataclass(frozen=True, slots=True)
class SelfTestReceipt:
    name: str
    standing: CapabilityStanding
    evidence: str
    exception_type: str | None = None

    @property
    def receipt_id(self) -> str:
        payload = json.dumps(
            {
                "name": self.name,
                "standing": self.standing.value,
                "evidence": self.evidence,
                "exception_type": self.exception_type,
            },
            sort_keys=True,
        )
        return sha256(payload.encode("utf-8")).hexdigest()

    def as_dict(self) -> dict[str, str | None]:
        return {
            "name": self.name,
            "standing": self.standing.value,
            "evidence": self.evidence,
            "exception_type": self.exception_type,
            "receipt_id": self.receipt_id,
        }


def _check_openapi_roundtrip() -> str:
    with TemporaryDirectory(prefix="dslmodel-selftest-") as temp:
        root = Path(temp)
        source = root / "openapi.yaml"
        output = root / "models.py"
        source.write_text(
            """
openapi: 3.1.0
info: {title: selftest, version: '1'}
components:
  schemas:
    Pet:
      type: object
      additionalProperties: false
      required: [display-name]
      properties:
        display-name: {type: string, minLength: 1}
        age: {type: integer, minimum: 0}
""".strip(),
            encoding="utf-8",
        )
        generate_openapi_models(source, output)
        spec = importlib.util.spec_from_file_location("dslmodel_selftest_models", output)
        if spec is None or spec.loader is None:
            raise RuntimeError("generated module could not be loaded")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        pet = module.Pet.model_validate({"display-name": "Mark", "age": 7})
        if pet.model_dump(by_alias=True) != {"display-name": "Mark", "age": 7}:
            raise AssertionError("generated model did not preserve aliases and values")
        try:
            module.Pet.model_validate({"display-name": "Mark", "unexpected": True})
        except Exception:
            pass
        else:
            raise AssertionError("additionalProperties=false was not enforced")
        compile(output.read_text(encoding="utf-8"), str(output), "exec")
        return "generated, imported, validated, and rejected forbidden properties"


def _check_capability_execution() -> str:
    module = ModuleType("dslmodel_selftest_capability")
    module.app = typer.Typer()

    @module.app.command("ping")
    def ping() -> None:
        typer.echo("pong")

    registry = CapabilityRegistry(importer=lambda _: module)
    receipt = registry.mount(
        typer.Typer(),
        CapabilitySpec(
            "selftest-capability",
            "dslmodel.selftest.capability",
            "selftest",
            required=True,
            verifier_args=(),
        ),
    )
    if receipt.standing is not CapabilityStanding.ALIVE or not receipt.executed or receipt.exit_code != 0:
        raise AssertionError(receipt.as_dict())
    return f"mounted and executed verifier receipt {receipt.receipt_id[:12]}"


def _check_artifact_receipt() -> str:
    with TemporaryDirectory(prefix="dslmodel-receipt-") as temp:
        artifact = Path(temp) / "artifact.txt"
        artifact.write_text("dslmodel-alive\n", encoding="utf-8")
        receipt = artifact_receipt(artifact)
        if not verify_artifact_receipt(artifact, str(receipt["digest"])):
            raise AssertionError("receipt replay failed")
        artifact.write_text("mutated\n", encoding="utf-8")
        if verify_artifact_receipt(artifact, str(receipt["digest"])):
            raise AssertionError("receipt did not detect artifact mutation")
        return f"created, replayed, and falsified receipt {str(receipt['receipt_id'])[:12]}"


_CHECKS: tuple[tuple[str, Callable[[], str]], ...] = (
    ("openapi-roundtrip", _check_openapi_roundtrip),
    ("capability-execution", _check_capability_execution),
    ("artifact-receipt", _check_artifact_receipt),
)


def run_selftests() -> dict[str, object]:
    """Execute the admitted 80/20 capability pack and return receipts."""

    receipts: list[SelfTestReceipt] = []
    for name, check in _CHECKS:
        try:
            evidence = check()
        except Exception as exc:
            receipts.append(
                SelfTestReceipt(
                    name=name,
                    standing=CapabilityStanding.BUILD_BROKEN,
                    evidence=str(exc),
                    exception_type=type(exc).__name__,
                )
            )
        else:
            receipts.append(
                SelfTestReceipt(
                    name=name,
                    standing=CapabilityStanding.ALIVE,
                    evidence=evidence,
                )
            )
    standing = (
        CapabilityStanding.ALIVE.value
        if receipts and all(item.standing is CapabilityStanding.ALIVE for item in receipts)
        else CapabilityStanding.BUILD_BROKEN.value
    )
    return {
        "standing": standing,
        "checks": [item.as_dict() for item in receipts],
    }
