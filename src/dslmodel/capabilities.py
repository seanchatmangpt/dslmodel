"""Capability admission, execution verification, and artifact receipts.

A capability is ALIVE only after its Typer application imports, mounts, and an
explicit verifier command executes successfully. Historical or experimental
surfaces belong in a separate non-admitted catalog; they are not silently
counted as product capabilities.
"""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass, replace
from enum import StrEnum
from hashlib import sha256
from importlib import import_module
from io import StringIO
import json
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Iterable, Mapping

from typer.testing import CliRunner


class CapabilityStanding(StrEnum):
    """Execution standing for one admitted capability boundary."""

    UNKNOWN = "UNKNOWN"
    PARTIAL_ALIVE = "PARTIAL_ALIVE"
    ALIVE = "ALIVE"
    BLOCKED = "BLOCKED"
    BUILD_BROKEN = "BUILD_BROKEN"
    UNSUPPORTED = "UNSUPPORTED"


@dataclass(frozen=True, slots=True)
class CapabilitySpec:
    """Declarative description of one admitted CLI capability."""

    name: str
    module: str
    help: str
    group: str = "core"
    required: bool = False
    app_attribute: str = "app"
    command: str | None = None
    verifier_args: tuple[str, ...] | None = ("--help",)


@dataclass(frozen=True, slots=True)
class CapabilityReceipt:
    """Evidence produced while importing, mounting, and executing a capability."""

    name: str
    module: str
    group: str
    required: bool
    standing: CapabilityStanding
    imported: bool = False
    mounted: bool = False
    executed: bool = False
    verifier_args: tuple[str, ...] | None = None
    exit_code: int | None = None
    reason: str | None = None
    missing_dependency: str | None = None
    exception_type: str | None = None
    import_output: str | None = None
    verification_output: str | None = None

    @property
    def receipt_id(self) -> str:
        payload = json.dumps(self.as_dict(include_receipt=False), sort_keys=True)
        return sha256(payload.encode("utf-8")).hexdigest()

    def as_dict(self, *, include_receipt: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": self.name,
            "module": self.module,
            "group": self.group,
            "required": self.required,
            "standing": self.standing.value,
            "imported": self.imported,
            "mounted": self.mounted,
            "executed": self.executed,
            "verifier_args": list(self.verifier_args) if self.verifier_args is not None else None,
            "exit_code": self.exit_code,
            "reason": self.reason,
            "missing_dependency": self.missing_dependency,
            "exception_type": self.exception_type,
            "import_output": self.import_output,
            "verification_output": self.verification_output,
        }
        if include_receipt:
            payload["receipt_id"] = self.receipt_id
        return payload


Importer = Callable[[str], ModuleType]


class CapabilityRegistry:
    """Admit command modules independently and require observed execution."""

    def __init__(
        self,
        *,
        importer: Importer = import_module,
        capture_import_output: bool = True,
    ) -> None:
        self._importer = importer
        self._capture_import_output = capture_import_output
        self._modules: dict[str, ModuleType] = {}
        self._receipts: dict[str, CapabilityReceipt] = {}

    @staticmethod
    def _clean_output(stdout: StringIO, stderr: StringIO) -> str | None:
        text = "\n".join(part.strip() for part in (stdout.getvalue(), stderr.getvalue()) if part.strip())
        return text[:4000] or None

    @staticmethod
    def _truncate(text: str | None) -> str | None:
        return text[:4000] if text else None

    @staticmethod
    def _classify_import_failure(
        spec: CapabilitySpec,
        exc: BaseException,
        output: str | None,
    ) -> CapabilityReceipt:
        missing = getattr(exc, "name", None)
        internal_missing = bool(
            missing
            and (
                missing == spec.module
                or spec.module.startswith(f"{missing}.")
                or str(missing).startswith("dslmodel")
            )
        )
        standing = (
            CapabilityStanding.BUILD_BROKEN
            if internal_missing or not isinstance(exc, ModuleNotFoundError)
            else CapabilityStanding.UNSUPPORTED
        )
        return CapabilityReceipt(
            name=spec.name,
            module=spec.module,
            group=spec.group,
            required=spec.required,
            standing=standing,
            verifier_args=spec.verifier_args,
            reason=str(exc),
            missing_dependency=str(missing) if missing else None,
            exception_type=type(exc).__name__,
            import_output=output,
        )

    def probe(self, spec: CapabilitySpec, *, refresh: bool = False) -> CapabilityReceipt:
        """Import one capability; import alone is PARTIAL_ALIVE, never ALIVE."""

        if not refresh and spec.name in self._receipts:
            return self._receipts[spec.name]

        stdout, stderr = StringIO(), StringIO()
        try:
            if self._capture_import_output:
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    module = self._importer(spec.module)
            else:
                module = self._importer(spec.module)
        except Exception as exc:
            receipt = self._classify_import_failure(
                spec,
                exc,
                self._clean_output(stdout, stderr),
            )
            self._receipts[spec.name] = receipt
            return receipt

        app = getattr(module, spec.app_attribute, None)
        if app is None or not hasattr(app, "registered_commands"):
            receipt = CapabilityReceipt(
                name=spec.name,
                module=spec.module,
                group=spec.group,
                required=spec.required,
                standing=CapabilityStanding.BUILD_BROKEN,
                imported=True,
                verifier_args=spec.verifier_args,
                reason=f"module has no Typer app attribute {spec.app_attribute!r}",
                import_output=self._clean_output(stdout, stderr),
            )
        else:
            self._modules[spec.name] = module
            receipt = CapabilityReceipt(
                name=spec.name,
                module=spec.module,
                group=spec.group,
                required=spec.required,
                standing=CapabilityStanding.PARTIAL_ALIVE,
                imported=True,
                verifier_args=spec.verifier_args,
                import_output=self._clean_output(stdout, stderr),
                reason="imported but not yet executed",
            )

        self._receipts[spec.name] = receipt
        return receipt

    def mount(self, parent: Any, spec: CapabilitySpec) -> CapabilityReceipt:
        """Mount and execute a verifier for one admitted Typer application."""

        receipt = self.probe(spec)
        if receipt.standing not in {CapabilityStanding.PARTIAL_ALIVE, CapabilityStanding.ALIVE}:
            return receipt

        module = self._modules[spec.name]
        app = getattr(module, spec.app_attribute)
        try:
            parent.add_typer(app, name=spec.command or spec.name, help=spec.help)
        except Exception as exc:
            failed = replace(
                receipt,
                standing=CapabilityStanding.BUILD_BROKEN,
                mounted=False,
                reason=str(exc),
                exception_type=type(exc).__name__,
            )
            self._receipts[spec.name] = failed
            return failed

        mounted = replace(receipt, mounted=True, reason="mounted but not yet executed")
        if spec.verifier_args is None:
            self._receipts[spec.name] = mounted
            return mounted

        result = CliRunner().invoke(app, list(spec.verifier_args), catch_exceptions=True)
        if result.exit_code != 0:
            failed = replace(
                mounted,
                standing=CapabilityStanding.BUILD_BROKEN,
                executed=True,
                exit_code=result.exit_code,
                reason=f"verifier exited {result.exit_code}",
                exception_type=type(result.exception).__name__ if result.exception else None,
                verification_output=self._truncate(result.output),
            )
            self._receipts[spec.name] = failed
            return failed

        alive = replace(
            mounted,
            standing=CapabilityStanding.ALIVE,
            executed=True,
            exit_code=0,
            reason="verifier executed successfully",
            verification_output=self._truncate(result.output),
        )
        self._receipts[spec.name] = alive
        return alive

    def mount_all(self, parent: Any, specs: Iterable[CapabilitySpec]) -> tuple[CapabilityReceipt, ...]:
        return tuple(self.mount(parent, spec) for spec in specs)

    @property
    def receipts(self) -> tuple[CapabilityReceipt, ...]:
        return tuple(self._receipts.values())

    def report(self) -> dict[str, Any]:
        receipts = self.receipts
        counts = {standing.value: 0 for standing in CapabilityStanding}
        for receipt in receipts:
            counts[receipt.standing.value] += 1
        required_failures = [
            receipt.as_dict()
            for receipt in receipts
            if receipt.required and receipt.standing is not CapabilityStanding.ALIVE
        ]
        if not receipts:
            aggregate = CapabilityStanding.UNKNOWN.value
        elif all(receipt.standing is CapabilityStanding.ALIVE for receipt in receipts):
            aggregate = CapabilityStanding.ALIVE.value
        elif any(receipt.standing is CapabilityStanding.ALIVE for receipt in receipts):
            aggregate = CapabilityStanding.PARTIAL_ALIVE.value
        elif any(receipt.standing is CapabilityStanding.BUILD_BROKEN for receipt in receipts):
            aggregate = CapabilityStanding.BUILD_BROKEN.value
        elif any(receipt.standing is CapabilityStanding.PARTIAL_ALIVE for receipt in receipts):
            aggregate = CapabilityStanding.PARTIAL_ALIVE.value
        elif all(receipt.standing is CapabilityStanding.UNSUPPORTED for receipt in receipts):
            aggregate = CapabilityStanding.UNSUPPORTED.value
        else:
            aggregate = CapabilityStanding.UNKNOWN.value
        return {
            "standing": aggregate,
            "counts": counts,
            "required_failures": required_failures,
            "capabilities": [receipt.as_dict() for receipt in receipts],
        }

    def required_failures(self) -> tuple[CapabilityReceipt, ...]:
        return tuple(
            receipt
            for receipt in self.receipts
            if receipt.required and receipt.standing is not CapabilityStanding.ALIVE
        )


def artifact_receipt(path: Path) -> dict[str, Any]:
    """Create a deterministic receipt for one regular file."""

    if not path.is_file():
        raise ValueError(f"artifact is not a regular file: {path}")
    data = path.read_bytes()
    payload = {
        "algorithm": "sha256",
        "path": str(path),
        "size": len(data),
        "digest": sha256(data).hexdigest(),
    }
    identity = {
        "algorithm": payload["algorithm"],
        "size": payload["size"],
        "digest": payload["digest"],
    }
    canonical = json.dumps(identity, sort_keys=True, separators=(",", ":"))
    payload["receipt_id"] = sha256(canonical.encode("utf-8")).hexdigest()
    return payload


def verify_artifact_receipt(path: Path, expected_digest: str) -> bool:
    """Verify an artifact against an expected SHA-256 digest."""

    return artifact_receipt(path)["digest"] == expected_digest.lower()


def render_receipts_json(registries: Mapping[str, CapabilityRegistry]) -> str:
    """Render multiple registry reports in a stable machine-readable envelope."""

    reports = {name: registry.report() for name, registry in sorted(registries.items())}
    if reports and all(report["standing"] == CapabilityStanding.ALIVE.value for report in reports.values()):
        standing = CapabilityStanding.ALIVE.value
    elif any(
        report["standing"] in {CapabilityStanding.ALIVE.value, CapabilityStanding.PARTIAL_ALIVE.value}
        for report in reports.values()
    ):
        standing = CapabilityStanding.PARTIAL_ALIVE.value
    else:
        standing = CapabilityStanding.UNKNOWN.value
    return json.dumps({"standing": standing, "registries": reports}, indent=2, sort_keys=True)
