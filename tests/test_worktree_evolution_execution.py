from __future__ import annotations

import asyncio
import importlib.util
from pathlib import Path
import subprocess
import sys

import pytest


MODULE_PATH = Path(__file__).parents[1] / "src" / "dslmodel" / "evolution" / "worktree_evolution_engine.py"
spec = importlib.util.spec_from_file_location("worktree_evolution_engine_under_test", MODULE_PATH)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

EvolutionActuationRefused = module.EvolutionActuationRefused
EvolutionStrategy = module.EvolutionStrategy
WorktreeEvolutionEngine = module.WorktreeEvolutionEngine


def run(*argv: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, cwd=cwd, capture_output=True, text=True, check=True)


def initialize_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    run("git", "init", "-b", "main", cwd=repo)
    (repo / "value.txt").write_text("old\n", encoding="utf-8")
    run("git", "add", "value.txt", cwd=repo)
    run(
        "git",
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.invalid",
        "commit",
        "-m",
        "initial",
        cwd=repo,
    )
    return repo


def make_patch(tmp_path: Path) -> Path:
    patch = tmp_path / "candidate.patch"
    patch.write_text(
        """--- a/value.txt
+++ b/value.txt
@@ -1 +1 @@
-old
+new
""",
        encoding="utf-8",
    )
    return patch


def verifier() -> tuple[str, ...]:
    return (
        sys.executable,
        "-c",
        "from pathlib import Path; assert Path('value.txt').read_text().strip() == 'new'",
    )


def test_candidate_patch_and_validation_are_execution_backed(tmp_path: Path) -> None:
    repo = initialize_repo(tmp_path)
    patch = make_patch(tmp_path)
    engine = WorktreeEvolutionEngine(repo, verifier_command=verifier())
    candidate = engine.create_candidate(EvolutionStrategy.RELIABILITY_IMPROVEMENT, candidate_id="candidate-one")

    patch_receipt = engine.apply_patch(candidate.candidate_id, patch)
    validation = asyncio.run(engine.validate_candidate(candidate.candidate_id))

    assert patch_receipt["patch_sha256"]
    assert patch_receipt["commit_sha"] != candidate.base_commit
    assert validation["validation_passed"] is True
    assert validation["tests_passed"] == validation["tests_total"] == 1
    assert validation["fitness_score"] == 1.0
    assert validation["verifier"]["exit_code"] == 0
    assert validation["verifier"]["receipt_id"]
    with pytest.raises(EvolutionActuationRefused, match="merge authority"):
        engine.merge_successful_candidate(candidate.candidate_id)

    cleanup = engine.cleanup_candidate(candidate.candidate_id, delete_branch=False)
    assert cleanup["worktree_removed"] is True
    assert cleanup["branch_deleted"] is False


def test_failed_verifier_cannot_be_merged(tmp_path: Path) -> None:
    repo = initialize_repo(tmp_path)
    patch = make_patch(tmp_path)
    engine = WorktreeEvolutionEngine(
        repo,
        verifier_command=(sys.executable, "-c", "raise SystemExit(7)"),
        allow_merge=True,
        merge_target="main",
    )
    candidate = engine.create_candidate(EvolutionStrategy.RELIABILITY_IMPROVEMENT, candidate_id="candidate-bad")
    engine.apply_patch(candidate.candidate_id, patch)
    validation = asyncio.run(engine.validate_candidate(candidate.candidate_id))

    assert validation["validation_passed"] is False
    assert validation["verifier"]["exit_code"] == 7
    assert validation["fitness_score"] == 0.0
    with pytest.raises(EvolutionActuationRefused, match="no successful"):
        engine.merge_successful_candidate(candidate.candidate_id)


def test_explicit_merge_actuation_has_before_after_receipt(tmp_path: Path) -> None:
    repo = initialize_repo(tmp_path)
    patch = make_patch(tmp_path)
    engine = WorktreeEvolutionEngine(
        repo,
        verifier_command=verifier(),
        allow_merge=True,
        merge_target="main",
    )
    candidate = engine.create_candidate(EvolutionStrategy.RELIABILITY_IMPROVEMENT, candidate_id="candidate-merge")
    engine.apply_patch(candidate.candidate_id, patch)
    validation = asyncio.run(engine.validate_candidate(candidate.candidate_id))
    assert validation["validation_passed"] is True

    receipt = engine.merge_successful_candidate(candidate.candidate_id)
    assert receipt.before_sha != receipt.after_sha
    assert receipt.command.exit_code == 0
    assert receipt.receipt_id
    assert (repo / "value.txt").read_text(encoding="utf-8") == "new\n"

    cleanup = engine.cleanup_candidate(candidate.candidate_id, delete_branch=True)
    assert cleanup["worktree_removed"] is True
    assert cleanup["branch_deleted"] is True
