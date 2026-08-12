"""Execution-backed evolution experiments using Git worktrees.

This module does not invent mutations, fitness, validation results, deployment
success, or monitoring data. Construction is supplied as patch artifacts;
validation is observed command execution; merge is an explicit actuation path
that is disabled unless the caller grants authority.
"""

from __future__ import annotations

import asyncio
from dataclasses import asdict, dataclass, field
from enum import Enum
from hashlib import sha256
import json
from pathlib import Path
import shlex
import subprocess
import time
from typing import Any, Iterable, Sequence
import uuid


class EvolutionError(RuntimeError):
    """Base error for evolution experiment failures."""


class EvolutionAdmissionError(EvolutionError):
    """Raised when an experiment input cannot be admitted."""


class EvolutionActuationRefused(EvolutionError):
    """Raised when a state-changing operation lacks explicit authority."""


class EvolutionStrategy(str, Enum):
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    COORDINATION_IMPROVEMENT = "coordination_improvement"
    FEATURE_ENHANCEMENT = "feature_enhancement"
    RELIABILITY_IMPROVEMENT = "reliability_improvement"


@dataclass(frozen=True, slots=True)
class CommandReceipt:
    """Observed execution evidence for one command."""

    argv: tuple[str, ...]
    cwd: str
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float

    @property
    def ok(self) -> bool:
        return self.exit_code == 0

    @property
    def receipt_id(self) -> str:
        payload = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))
        return sha256(payload.encode("utf-8")).hexdigest()


@dataclass(slots=True)
class EvolutionCandidate:
    candidate_id: str
    strategy: EvolutionStrategy
    description: str
    worktree_path: str
    branch_name: str
    base_commit: str
    applied_patches: list[str] = field(default_factory=list)
    validation_results: dict[str, Any] | None = None
    fitness_score: float = 0.0


@dataclass(slots=True)
class EvolutionGeneration:
    generation_id: str
    candidates: list[EvolutionCandidate]
    best_candidate: EvolutionCandidate | None
    fitness_improvement: float
    deployed: bool = False


@dataclass(frozen=True, slots=True)
class MergeReceipt:
    experiment_id: str
    source_branch: str
    target_branch: str
    before_sha: str
    after_sha: str
    command: CommandReceipt

    @property
    def receipt_id(self) -> str:
        payload = json.dumps(
            {
                "experiment_id": self.experiment_id,
                "source_branch": self.source_branch,
                "target_branch": self.target_branch,
                "before_sha": self.before_sha,
                "after_sha": self.after_sha,
                "command_receipt": self.command.receipt_id,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return sha256(payload.encode("utf-8")).hexdigest()


class WorktreeEvolutionEngine:
    """Apply explicit patches in isolated worktrees and validate by execution."""

    def __init__(
        self,
        base_path: str | Path = ".",
        *,
        verifier_command: Sequence[str] = ("python", "-m", "pytest", "-q"),
        worktrees_root: str | Path | None = None,
        allow_merge: bool = False,
        merge_target: str | None = None,
        monitor_command: Sequence[str] | None = None,
        population_size: int = 1,
        mutation_rate: float = 0.0,
    ) -> None:
        self.base_path = Path(base_path).resolve()
        if not (self.base_path / ".git").exists():
            # Worktrees have a .git *file*, so exists() is the right predicate.
            raise EvolutionAdmissionError(f"base_path is not a Git working tree: {self.base_path}")
        if not verifier_command:
            raise EvolutionAdmissionError("verifier_command must not be empty")
        self.verifier_command = tuple(str(item) for item in verifier_command)
        self.monitor_command = tuple(str(item) for item in monitor_command) if monitor_command else None
        self.allow_merge = allow_merge
        self.merge_target = merge_target
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.worktrees_root = (
            Path(worktrees_root).resolve()
            if worktrees_root is not None
            else self.base_path.parent / f".{self.base_path.name}-evolution-worktrees"
        )
        self.worktrees_root.mkdir(parents=True, exist_ok=True)
        self.active_candidates: dict[str, EvolutionCandidate] = {}
        self.evolution_history: list[EvolutionGeneration] = []
        self.current_generation = 0

    @staticmethod
    def parse_command(command: str) -> tuple[str, ...]:
        parsed = tuple(shlex.split(command))
        if not parsed:
            raise EvolutionAdmissionError("command must not be empty")
        return parsed

    @staticmethod
    def _completed_receipt(
        argv: Sequence[str],
        cwd: Path,
        completed: subprocess.CompletedProcess[str],
        started: float,
    ) -> CommandReceipt:
        return CommandReceipt(
            argv=tuple(argv),
            cwd=str(cwd),
            exit_code=completed.returncode,
            stdout=completed.stdout[-16000:],
            stderr=completed.stderr[-16000:],
            duration_seconds=max(0.0, time.monotonic() - started),
        )

    def run_command(
        self,
        argv: Sequence[str],
        *,
        cwd: Path | None = None,
        check: bool = False,
    ) -> CommandReceipt:
        if not argv:
            raise EvolutionAdmissionError("cannot execute an empty command")
        target = (cwd or self.base_path).resolve()
        started = time.monotonic()
        completed = subprocess.run(
            list(argv),
            cwd=target,
            capture_output=True,
            text=True,
            check=False,
        )
        receipt = self._completed_receipt(argv, target, completed, started)
        if check and not receipt.ok:
            raise EvolutionError(
                f"command failed ({receipt.exit_code}): {' '.join(receipt.argv)}\n{receipt.stderr or receipt.stdout}"
            )
        return receipt

    def run_git(self, args: Sequence[str], *, cwd: Path | None = None, check: bool = True) -> CommandReceipt:
        return self.run_command(("git", *args), cwd=cwd, check=check)

    def _head_sha(self, cwd: Path | None = None) -> str:
        return self.run_git(("rev-parse", "HEAD"), cwd=cwd).stdout.strip()

    def _current_branch(self, cwd: Path | None = None) -> str:
        branch = self.run_git(("branch", "--show-current"), cwd=cwd).stdout.strip()
        if not branch:
            raise EvolutionAdmissionError("operation requires a named Git branch, not detached HEAD")
        return branch

    def create_candidate(
        self,
        strategy: EvolutionStrategy,
        *,
        candidate_id: str | None = None,
    ) -> EvolutionCandidate:
        candidate_id = candidate_id or f"exp-{uuid.uuid4().hex[:12]}"
        if candidate_id in self.active_candidates:
            raise EvolutionAdmissionError(f"candidate already exists: {candidate_id}")
        if any(character not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for character in candidate_id):
            raise EvolutionAdmissionError("candidate_id may contain only letters, numbers, '-' and '_'")
        base_commit = self._head_sha()
        branch_name = f"evolution/{candidate_id}"
        worktree_path = self.worktrees_root / candidate_id
        if worktree_path.exists():
            raise EvolutionAdmissionError(f"worktree path already exists: {worktree_path}")
        self.run_git(("worktree", "add", "-b", branch_name, str(worktree_path), base_commit))
        candidate = EvolutionCandidate(
            candidate_id=candidate_id,
            strategy=strategy,
            description=f"{strategy.value} candidate",
            worktree_path=str(worktree_path),
            branch_name=branch_name,
            base_commit=base_commit,
        )
        self.active_candidates[candidate_id] = candidate
        return candidate

    def apply_patch(self, candidate_id: str, patch_path: str | Path) -> dict[str, Any]:
        candidate = self._require_candidate(candidate_id)
        patch = Path(patch_path).resolve()
        if not patch.is_file():
            raise EvolutionAdmissionError(f"patch does not exist: {patch}")
        worktree = Path(candidate.worktree_path)
        patch_bytes = patch.read_bytes()
        patch_digest = sha256(patch_bytes).hexdigest()
        check_receipt = self.run_git(("apply", "--check", str(patch)), cwd=worktree, check=False)
        if not check_receipt.ok:
            raise EvolutionAdmissionError(
                f"patch is not applicable: {patch}\n{check_receipt.stderr or check_receipt.stdout}"
            )
        self.run_git(("apply", str(patch)), cwd=worktree)
        diff_check = self.run_git(("diff", "--check"), cwd=worktree, check=False)
        if not diff_check.ok:
            self.run_git(("reset", "--hard", "HEAD"), cwd=worktree)
            raise EvolutionAdmissionError(f"patch creates invalid diff: {diff_check.stderr or diff_check.stdout}")
        self.run_git(("add", "-A"), cwd=worktree)
        staged = self.run_git(("diff", "--cached", "--quiet"), cwd=worktree, check=False)
        if staged.exit_code == 0:
            raise EvolutionAdmissionError("patch produced no staged change")
        commit = self.run_command(
            (
                "git",
                "-c",
                "user.name=DSLModel Evolution",
                "-c",
                "user.email=evolution@localhost",
                "commit",
                "-m",
                f"evolution: apply {patch.name}",
            ),
            cwd=worktree,
            check=True,
        )
        candidate.applied_patches.append(patch_digest)
        return {
            "candidate_id": candidate_id,
            "patch": str(patch),
            "patch_sha256": patch_digest,
            "commit_sha": self._head_sha(worktree),
            "commit_receipt": commit.receipt_id,
        }

    async def validate_candidate(self, candidate_id: str) -> dict[str, Any]:
        candidate = self._require_candidate(candidate_id)
        worktree = Path(candidate.worktree_path)
        diff_check = self.run_git(("diff", "--check", "HEAD^", "HEAD"), cwd=worktree, check=False)
        verifier = await self._run_async(self.verifier_command, cwd=worktree)
        validation_passed = diff_check.ok and verifier.ok
        # Fitness is intentionally a binary consequence of the declared verifier.
        # No synthetic performance or quality metric is manufactured here.
        fitness = 1.0 if validation_passed else 0.0
        result = {
            "validation_passed": validation_passed,
            "fitness_score": fitness,
            "fitness_improvement": 0.0,
            "tests_total": 1,
            "tests_passed": 1 if validation_passed else 0,
            "verifier": asdict(verifier) | {"receipt_id": verifier.receipt_id},
            "diff_check": asdict(diff_check) | {"receipt_id": diff_check.receipt_id},
            "candidate_head": self._head_sha(worktree),
            "base_commit": candidate.base_commit,
        }
        candidate.validation_results = result
        candidate.fitness_score = fitness
        return result

    async def _run_async(self, argv: Sequence[str], *, cwd: Path) -> CommandReceipt:
        started = time.monotonic()
        process = await asyncio.create_subprocess_exec(
            *argv,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        return CommandReceipt(
            argv=tuple(argv),
            cwd=str(cwd),
            exit_code=process.returncode,
            stdout=stdout.decode("utf-8", errors="replace")[-16000:],
            stderr=stderr.decode("utf-8", errors="replace")[-16000:],
            duration_seconds=max(0.0, time.monotonic() - started),
        )

    async def evolve_generation(
        self,
        strategy: EvolutionStrategy = EvolutionStrategy.COORDINATION_IMPROVEMENT,
        *,
        patches: Iterable[str | Path] = (),
    ) -> EvolutionGeneration:
        """Construct one candidate per supplied patch and execute its verifier."""

        supplied = tuple(patches)
        if not supplied:
            raise EvolutionAdmissionError("evolve_generation requires explicit patch artifacts")
        generation_id = f"gen-{self.current_generation:03d}-{uuid.uuid4().hex[:8]}"
        candidates: list[EvolutionCandidate] = []
        for index, patch in enumerate(supplied):
            candidate = self.create_candidate(strategy, candidate_id=f"{generation_id}-cand-{index:02d}")
            self.apply_patch(candidate.candidate_id, patch)
            await self.validate_candidate(candidate.candidate_id)
            candidates.append(candidate)
        best = self._select_best_candidate(candidates)
        generation = EvolutionGeneration(
            generation_id=generation_id,
            candidates=candidates,
            best_candidate=best,
            fitness_improvement=0.0,
        )
        self.evolution_history.append(generation)
        self.current_generation += 1
        return generation

    @staticmethod
    def _select_best_candidate(candidates: Sequence[EvolutionCandidate]) -> EvolutionCandidate | None:
        admitted = [candidate for candidate in candidates if candidate.validation_results and candidate.validation_results["validation_passed"]]
        if not admitted:
            return None
        # All admitted candidates passed the same verifier. Preserve combinatorial
        # optionality by deterministic identity rather than fabricating ranking.
        return min(admitted, key=lambda candidate: candidate.candidate_id)

    def merge_successful_candidate(self, candidate_id: str, *, target_branch: str | None = None) -> MergeReceipt:
        """Actuate a verified merge only when authority was granted at construction."""

        if not self.allow_merge:
            raise EvolutionActuationRefused("merge authority is disabled; construct engine with allow_merge=True")
        candidate = self._require_candidate(candidate_id)
        if not candidate.validation_results or not candidate.validation_results.get("validation_passed"):
            raise EvolutionActuationRefused("candidate has no successful execution-backed validation receipt")
        target = target_branch or self.merge_target or self._current_branch()
        current = self._current_branch()
        if current != target:
            raise EvolutionActuationRefused(
                f"base checkout is on {current!r}; refusing implicit switch to merge target {target!r}"
            )
        before = self._head_sha()
        merge = self.run_git(
            ("merge", "--no-ff", "--no-edit", candidate.branch_name),
            check=False,
        )
        if not merge.ok:
            self.run_git(("merge", "--abort"), check=False)
            raise EvolutionError(f"merge failed: {merge.stderr or merge.stdout}")
        after = self._head_sha()
        return MergeReceipt(
            experiment_id=candidate.candidate_id,
            source_branch=candidate.branch_name,
            target_branch=target,
            before_sha=before,
            after_sha=after,
            command=merge,
        )

    async def monitor_candidate(self, candidate_id: str) -> dict[str, Any]:
        """Execute a caller-supplied monitoring command; never synthesize health."""

        self._require_candidate(candidate_id)
        if self.monitor_command is None:
            raise EvolutionAdmissionError("monitoring requires an explicit monitor_command")
        receipt = await self._run_async(self.monitor_command, cwd=self.base_path)
        return {
            "healthy": receipt.ok,
            "command": asdict(receipt) | {"receipt_id": receipt.receipt_id},
        }

    def cleanup_candidate(self, candidate_id: str, *, delete_branch: bool = True) -> dict[str, Any]:
        candidate = self._require_candidate(candidate_id)
        worktree = Path(candidate.worktree_path)
        remove = self.run_git(("worktree", "remove", str(worktree)), check=False)
        if not remove.ok:
            raise EvolutionError(f"worktree removal failed: {remove.stderr or remove.stdout}")
        branch_receipt: CommandReceipt | None = None
        if delete_branch:
            branch_receipt = self.run_git(("branch", "-d", candidate.branch_name), check=False)
            if not branch_receipt.ok:
                raise EvolutionError(f"branch deletion failed: {branch_receipt.stderr or branch_receipt.stdout}")
        del self.active_candidates[candidate_id]
        return {
            "candidate_id": candidate_id,
            "worktree_removed": True,
            "worktree_receipt": remove.receipt_id,
            "branch_deleted": bool(branch_receipt),
            "branch_receipt": branch_receipt.receipt_id if branch_receipt else None,
        }

    def _require_candidate(self, candidate_id: str) -> EvolutionCandidate:
        try:
            return self.active_candidates[candidate_id]
        except KeyError as exc:
            raise EvolutionAdmissionError(f"unknown candidate: {candidate_id}") from exc

    def get_evolution_status(self) -> dict[str, Any]:
        return {
            "current_generation": self.current_generation,
            "total_generations": len(self.evolution_history),
            "active_candidates": sorted(self.active_candidates),
            "verifier_command": list(self.verifier_command),
            "allow_merge": self.allow_merge,
            "merge_target": self.merge_target,
            "monitor_command": list(self.monitor_command) if self.monitor_command else None,
        }
