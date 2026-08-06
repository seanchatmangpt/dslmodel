"""Capability admission, mounting, and receipt generation for DSLModel.

The registry deliberately treats every command surface independently.  A missing
optional dependency can remove one edge without collapsing the complete CLI.
"""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass, replace
from enum import StrEnum
from hashlib import sha256
from importlib import import_module
from io import StringIO
import json
from types import ModuleType
from typing import Any, Callable, Iterable, Mapping


class CapabilityStanding(StrEnum):
    """Execution standing for one capability boundary."""

    UNKNOWN = "UNKNOWN"
    PARTIAL_ALIVE = "PARTIAL_ALIVE"
    ALIVE = "ALIVE"
    BLOCKED = "BLOCKED"
    BUILD_BROKEN = "BUILD_BROKEN"
    UNSUPPORTED = "UNSUPPORTED"


@dataclass(frozen=True, slots=True)
class CapabilitySpec:
    """Declarative description of a CLI capability."""

    name: str
    module: str
    help: str
    group: str = "legacy"
    required: bool = False
    app_attribute: str = "app"
    command: str | None = None


@dataclass(frozen=True, slots=True)
class CapabilityReceipt:
    """Evidence produced while admitting and mounting a capability."""

    name: str
    module: str
    group: str
    required: bool
    standing: CapabilityStanding
    imported: bool = False
    mounted: bool = False
    reason: str | None = None
    missing_dependency: str | None = None
    exception_type: str | None = None
    import_output: str | None = None

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
            "reason": self.reason,
            "missing_dependency": self.missing_dependency,
            "exception_type": self.exception_type,
            "import_output": self.import_output,
        }
        if include_receipt:
            payload["receipt_id"] = self.receipt_id
        return payload


Importer = Callable[[str], ModuleType]


class CapabilityRegistry:
    """Admit optional command modules without global failure coupling."""

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
            reason=str(exc),
            missing_dependency=str(missing) if missing else None,
            exception_type=type(exc).__name__,
            import_output=output,
        )

    def probe(self, spec: CapabilitySpec, *, refresh: bool = False) -> CapabilityReceipt:
        """Import and validate one capability, emitting a typed receipt."""

        if not refresh and spec.name in self._receipts:
            return self._receipts[spec.name]

        stdout, stderr = StringIO(), StringIO()
        try:
            if self._capture_import_output:
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    module = self._importer(spec.module)
            else:
                module = self._importer(spec.module)
        except Exception as exc:  # imports are an admission boundary
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
                standing=CapabilityStanding.ALIVE,
                imported=True,
                import_output=self._clean_output(stdout, stderr),
            )

        self._receipts[spec.name] = receipt
        return receipt

    def mount(self, parent: Any, spec: CapabilitySpec) -> CapabilityReceipt:
        """Mount one admitted Typer application under its declared name."""

        receipt = self.probe(spec)
        if receipt.standing is not CapabilityStanding.ALIVE:
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

        mounted = replace(receipt, mounted=True)
        self._receipts[spec.name] = mounted
        return mounted

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


def render_receipts_json(registries: Mapping[str, CapabilityRegistry]) -> str:
    """Render multiple registry reports in a stable machine-readable envelope."""

    reports = {name: registry.report() for name, registry in sorted(registries.items())}
    standing = (
        "ALIVE"
        if all(report["standing"] == "ALIVE" for report in reports.values())
        else "PARTIAL_ALIVE"
    )
    return json.dumps({"standing": standing, "registries": reports}, indent=2, sort_keys=True)
