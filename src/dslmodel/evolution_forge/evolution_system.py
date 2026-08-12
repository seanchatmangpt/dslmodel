"""Execution-backed telemetry events for evolution operations.

Emission receipts prove that the local OpenTelemetry API path executed. They do
not claim that an exporter, collector, or backend received the span; exporter
standing belongs to the configured telemetry runtime.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping

from opentelemetry import trace


class EvolutionTelemetryError(ValueError):
    """Raised when an evolution telemetry request is not admitted."""


@dataclass(frozen=True, slots=True)
class EmissionReceipt:
    operation: str
    span_name: str
    session_id: str
    attributes: dict[str, str | int | float | bool]
    recording: bool
    trace_id: str | None
    span_id: str | None

    @property
    def receipt_id(self) -> str:
        payload = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))
        return sha256(payload.encode("utf-8")).hexdigest()

    def as_dict(self) -> dict[str, Any]:
        return asdict(self) | {"receipt_id": self.receipt_id}


class EvolutionSystem:
    """Emit typed evolution spans and retain local execution receipts."""

    OPERATIONS = {"analyze", "generate", "apply", "learn", "validate", "worktree"}

    def __init__(self, tracer: trace.Tracer | None = None) -> None:
        self.tracer = tracer or trace.get_tracer(__name__, "1.0.0")
        self._receipts: list[EmissionReceipt] = []

    @staticmethod
    def _normalize_attributes(attributes: Mapping[str, Any]) -> dict[str, str | int | float | bool]:
        normalized: dict[str, str | int | float | bool] = {}
        for key, value in attributes.items():
            if not isinstance(key, str) or not key:
                raise EvolutionTelemetryError("attribute names must be non-empty strings")
            if isinstance(value, (str, int, float, bool)):
                normalized[key] = value
            elif value is None:
                continue
            else:
                raise EvolutionTelemetryError(
                    f"attribute {key!r} has unsupported value type {type(value).__name__}"
                )
        return normalized

    def _emit(
        self,
        operation: str,
        session_id: str,
        attributes: Mapping[str, Any],
    ) -> EmissionReceipt:
        if operation not in self.OPERATIONS:
            raise EvolutionTelemetryError(f"unsupported operation: {operation}")
        if not isinstance(session_id, str) or not session_id.strip():
            raise EvolutionTelemetryError("session_id must be a non-empty string")

        normalized = self._normalize_attributes(attributes)
        normalized["evolution.session_id"] = session_id
        span_name = f"dslmodel.evolution.{operation}"
        with self.tracer.start_as_current_span(span_name) as span:
            for key, value in normalized.items():
                span.set_attribute(key, value)
            context = span.get_span_context()
            valid_context = bool(context.is_valid)
            receipt = EmissionReceipt(
                operation=operation,
                span_name=span_name,
                session_id=session_id,
                attributes=normalized,
                recording=span.is_recording(),
                trace_id=f"{context.trace_id:032x}" if valid_context else None,
                span_id=f"{context.span_id:016x}" if valid_context else None,
            )
        self._receipts.append(receipt)
        return receipt

    def emit_analyze(self, session_id: str, analysis_type: str, issues_found: int) -> EmissionReceipt:
        return self._emit(
            "analyze",
            session_id,
            {
                "evolution.analysis_type": analysis_type,
                "evolution.issues_found": issues_found,
            },
        )

    def emit_generate(
        self,
        session_id: str,
        improvement_id: str,
        improvement_type: str,
        confidence_score: float,
        priority: str,
    ) -> EmissionReceipt:
        return self._emit(
            "generate",
            session_id,
            {
                "evolution.improvement_id": improvement_id,
                "evolution.improvement_type": improvement_type,
                "evolution.confidence_score": confidence_score,
                "evolution.priority": priority,
            },
        )

    def emit_apply(
        self,
        session_id: str,
        improvement_id: str,
        application_mode: str,
        application_result: str,
    ) -> EmissionReceipt:
        return self._emit(
            "apply",
            session_id,
            {
                "evolution.improvement_id": improvement_id,
                "evolution.application_mode": application_mode,
                "evolution.application_result": application_result,
            },
        )

    def emit_learn(self, session_id: str, patterns_analyzed: int, success_rate: float) -> EmissionReceipt:
        if not 0.0 <= success_rate <= 1.0:
            raise EvolutionTelemetryError("success_rate must be between 0 and 1")
        return self._emit(
            "learn",
            session_id,
            {
                "evolution.patterns_analyzed": patterns_analyzed,
                "evolution.success_rate": success_rate,
            },
        )

    def emit_validate(
        self,
        session_id: str,
        improvement_id: str,
        validation_type: str,
        validation_result: str,
    ) -> EmissionReceipt:
        return self._emit(
            "validate",
            session_id,
            {
                "evolution.improvement_id": improvement_id,
                "evolution.validation_type": validation_type,
                "evolution.validation_result": validation_result,
            },
        )

    def emit_worktree(self, session_id: str, worktree_id: str, worktree_action: str) -> EmissionReceipt:
        return self._emit(
            "worktree",
            session_id,
            {
                "evolution.worktree_id": worktree_id,
                "evolution.worktree_action": worktree_action,
            },
        )

    def get_status(self) -> dict[str, Any]:
        last = self._receipts[-1] if self._receipts else None
        return {
            "initialized": True,
            "emissions_observed": len(self._receipts),
            "last_receipt_id": last.receipt_id if last else None,
            "exporter_delivery": "UNKNOWN",
        }

    def run(self, config: Path | None = None) -> dict[str, Any]:
        """Emit one operation from an explicit JSON configuration file."""

        if config is None:
            return {
                "success": False,
                "standing": "REFUSED",
                "error": "configuration is required; no telemetry operation is inferred",
            }
        try:
            document = json.loads(config.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return {"success": False, "standing": "BUILD_BROKEN", "error": str(exc)}
        if not isinstance(document, dict):
            return {
                "success": False,
                "standing": "REFUSED",
                "error": "configuration root must be an object",
            }
        operation = document.get("operation")
        session_id = document.get("session_id")
        attributes = document.get("attributes", {})
        if not isinstance(operation, str) or operation not in self.OPERATIONS:
            return {
                "success": False,
                "standing": "REFUSED",
                "error": f"operation must be one of {sorted(self.OPERATIONS)}",
            }
        if not isinstance(session_id, str) or not session_id:
            return {"success": False, "standing": "REFUSED", "error": "session_id is required"}
        if not isinstance(attributes, dict):
            return {"success": False, "standing": "REFUSED", "error": "attributes must be an object"}
        try:
            receipt = self._emit(operation, session_id, attributes)
        except EvolutionTelemetryError as exc:
            return {"success": False, "standing": "REFUSED", "error": str(exc)}
        return {
            "success": True,
            "standing": "ALIVE",
            "emission": receipt.as_dict(),
            "exporter_delivery": "UNKNOWN",
        }
