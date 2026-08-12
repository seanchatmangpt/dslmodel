#!/usr/bin/env python3
"""Execution-backed worktree evolution CLI.

The CLI accepts concrete patch artifacts, validates them in isolated Git
worktrees, and emits command receipts. It never creates marker-file mutations,
fabricates fitness, reports simulated deployment health, or merges without an
explicit actuation flag.
"""

from __future__ import annotations

import asyncio
from dataclasses import asdict
import json
from pathlib import Path
from typing import Any

import typer

from ..evolution.worktree_evolution_engine import (
    EvolutionActuationRefused,
    EvolutionAdmissionError,
    EvolutionError,
    EvolutionStrategy,
    WorktreeEvolutionEngine,
)

app = typer.Typer(help="Execution-backed evolution experiments using Git worktrees")


def _emit(payload: dict[str, Any]) -> None:
    typer.echo(json.dumps(payload, indent=2, sort_keys=True, default=str))


def _strategy(value: str) -> EvolutionStrategy:
    normalized = value.strip().lower()
    aliases = {
        "performance": EvolutionStrategy.PERFORMANCE_OPTIMIZATION,
        "coordination": EvolutionStrategy.COORDINATION_IMPROVEMENT,
        "features": EvolutionStrategy.FEATURE_ENHANCEMENT,
        "feature": EvolutionStrategy.FEATURE_ENHANCEMENT,
        "reliability": EvolutionStrategy.RELIABILITY_IMPROVEMENT,
    }
    if normalized in aliases:
        return aliases[normalized]
    try:
        return EvolutionStrategy(normalized)
    except ValueError as exc:
        raise typer.BadParameter(
            "strategy must be one of performance, coordination, features, reliability, "
            "or a canonical EvolutionStrategy value"
        ) from exc


def _engine(
    base_path: Path,
    verifier: str,
    *,
    allow_merge: bool = False,
    merge_target: str | None = None,
    monitor: str | None = None,
) -> WorktreeEvolutionEngine:
    return WorktreeEvolutionEngine(
        base_path=base_path,
        verifier_command=WorktreeEvolutionEngine.parse_command(verifier),
        allow_merge=allow_merge,
        merge_target=merge_target,
        monitor_command=WorktreeEvolutionEngine.parse_command(monitor) if monitor else None,
    )


@app.command("experiment")
def experiment(
    patch: list[Path] = typer.Option(
        ...,
        "--patch",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Unified-diff patch artifact. Repeat for multiple patches in one candidate.",
    ),
    strategy: str = typer.Option("quality", "--strategy", help="Evolution intent label."),
    verifier: str = typer.Option("python -m pytest -q", "--verifier", help="Command that crowns the candidate."),
    base_path: Path = typer.Option(Path.cwd(), "--repo", exists=True, file_okay=False),
    candidate_id: str | None = typer.Option(None, "--candidate-id"),
    actuate_merge: bool = typer.Option(False, "--actuate-merge", help="Actually merge after successful verification."),
    merge_target: str | None = typer.Option(None, "--merge-target"),
    keep_worktree: bool = typer.Option(False, "--keep-worktree"),
) -> None:
    """Apply explicit patches in isolation, execute the verifier, and optionally merge."""

    if not patch:
        raise typer.BadParameter("at least one --patch is required")
    try:
        engine = _engine(
            base_path,
            verifier,
            allow_merge=actuate_merge,
            merge_target=merge_target,
        )
        candidate = engine.create_candidate(_strategy(strategy), candidate_id=candidate_id)
        patch_receipts = [engine.apply_patch(candidate.candidate_id, item) for item in patch]
        validation = asyncio.run(engine.validate_candidate(candidate.candidate_id))
        merge_receipt: dict[str, Any] | None = None
        if actuate_merge:
            if not validation["validation_passed"]:
                raise EvolutionActuationRefused("candidate failed verifier; merge is refused")
            merged = engine.merge_successful_candidate(candidate.candidate_id, target_branch=merge_target)
            merge_receipt = asdict(merged) | {"receipt_id": merged.receipt_id}

        cleanup: dict[str, Any] | None = None
        if not keep_worktree:
            # After a successful merge the topic branch can be deleted safely.
            # Without merge, preserve a failed candidate by default for diagnosis.
            if validation["validation_passed"] and (actuate_merge or not keep_worktree):
                cleanup = engine.cleanup_candidate(candidate.candidate_id)

        _emit(
            {
                "standing": "ALIVE" if validation["validation_passed"] else "BUILD_BROKEN",
                "candidate": asdict(candidate),
                "patch_receipts": patch_receipts,
                "validation": validation,
                "merge_receipt": merge_receipt,
                "cleanup": cleanup,
            }
        )
        if not validation["validation_passed"]:
            raise typer.Exit(1)
    except (EvolutionAdmissionError, EvolutionActuationRefused) as exc:
        typer.echo(f"REFUSED:{type(exc).__name__}: {exc}", err=True)
        raise typer.Exit(2) from exc
    except EvolutionError as exc:
        typer.echo(f"BUILD_BROKEN:{exc}", err=True)
        raise typer.Exit(1) from exc


@app.command("coordinate")
def coordinate(
    patch: list[Path] = typer.Option(
        ...,
        "--patch",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="One patch per isolated candidate; repeat option to compare candidates.",
    ),
    strategy: str = typer.Option("quality", "--strategy"),
    verifier: str = typer.Option("python -m pytest -q", "--verifier"),
    base_path: Path = typer.Option(Path.cwd(), "--repo", exists=True, file_okay=False),
    keep_worktrees: bool = typer.Option(False, "--keep-worktrees"),
) -> None:
    """Validate a reversible portfolio of patch candidates without automatic selection or merge."""

    if not patch:
        raise typer.BadParameter("at least one --patch is required")
    try:
        engine = _engine(base_path, verifier)
        generation = asyncio.run(engine.evolve_generation(_strategy(strategy), patches=patch))
        payload = {
            "standing": "ALIVE" if generation.best_candidate is not None else "BUILD_BROKEN",
            "generation_id": generation.generation_id,
            "candidates": [asdict(candidate) for candidate in generation.candidates],
            "best_candidate": generation.best_candidate.candidate_id if generation.best_candidate else None,
            "selection_rule": "deterministic identity among candidates passing the exact same verifier",
            "actuated": False,
        }
        if not keep_worktrees:
            cleanup_errors: list[dict[str, str]] = []
            for candidate in list(generation.candidates):
                try:
                    engine.cleanup_candidate(candidate.candidate_id)
                except EvolutionError as exc:
                    cleanup_errors.append({"candidate_id": candidate.candidate_id, "error": str(exc)})
            payload["cleanup_errors"] = cleanup_errors
        _emit(payload)
        if generation.best_candidate is None:
            raise typer.Exit(1)
    except EvolutionAdmissionError as exc:
        typer.echo(f"REFUSED:{type(exc).__name__}: {exc}", err=True)
        raise typer.Exit(2) from exc
    except EvolutionError as exc:
        typer.echo(f"BUILD_BROKEN:{exc}", err=True)
        raise typer.Exit(1) from exc


@app.command("monitor")
def monitor(
    candidate_id: str = typer.Argument(...),
    monitor_command: str = typer.Option(..., "--command", help="Observed health command; exit 0 means healthy."),
    verifier: str = typer.Option("python -m pytest -q", "--verifier"),
    base_path: Path = typer.Option(Path.cwd(), "--repo", exists=True, file_okay=False),
) -> None:
    """Execute an explicit monitoring command; no synthetic health is produced."""

    try:
        engine = _engine(base_path, verifier, monitor=monitor_command)
        if candidate_id not in engine.active_candidates:
            raise EvolutionAdmissionError(
                "candidate state is process-local; monitoring requires a candidate created in the same engine session"
            )
        _emit(asyncio.run(engine.monitor_candidate(candidate_id)))
    except EvolutionAdmissionError as exc:
        typer.echo(f"REFUSED:{type(exc).__name__}: {exc}", err=True)
        raise typer.Exit(2) from exc


@app.command("status")
def status(
    base_path: Path = typer.Option(Path.cwd(), "--repo", exists=True, file_okay=False),
    verifier: str = typer.Option("python -m pytest -q", "--verifier"),
) -> None:
    """Report observed Git/worktree state without claiming unavailable integrations."""

    try:
        engine = _engine(base_path, verifier)
        worktrees = engine.run_git(("worktree", "list", "--porcelain"), check=False)
        _emit(
            {
                "standing": "ALIVE" if worktrees.ok else "BUILD_BROKEN",
                "engine": engine.get_evolution_status(),
                "git_worktrees": {
                    "exit_code": worktrees.exit_code,
                    "stdout": worktrees.stdout,
                    "stderr": worktrees.stderr,
                    "receipt_id": worktrees.receipt_id,
                },
            }
        )
        if not worktrees.ok:
            raise typer.Exit(1)
    except EvolutionAdmissionError as exc:
        typer.echo(f"REFUSED:{type(exc).__name__}: {exc}", err=True)
        raise typer.Exit(2) from exc


if __name__ == "__main__":
    app()
