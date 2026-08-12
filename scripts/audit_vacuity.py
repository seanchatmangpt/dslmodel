#!/usr/bin/env python3
"""Audit implementation substance across the repository branch graph.

Every implementation-file occurrence is inspected, identical Git blobs are
parsed once, and findings are projected back to branch/path identity. Only the
canonical shipped/build surface has production standing; preserved source and
historical branch-only code remain visible evidence without silently acquiring
runtime authority.
"""

from __future__ import annotations

import argparse
import ast
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tokenize
import tomllib
from typing import Iterable

SEVERITY_ORDER = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
CODE_SUFFIXES = {
    ".py",
    ".pyi",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".vue",
    ".rs",
    ".go",
    ".sh",
    ".bash",
    ".zsh",
    ".toml",
    ".yaml",
    ".yml",
    ".json",
    ".j2",
    ".ejs",
    ".t",
}
SPECIAL_CODE_NAMES = {"Dockerfile", "Makefile", "justfile", "Procfile"}
MAX_BLOB_BYTES = 2_000_000

MARKERS = (
    (re.compile(r"\bTODO\b", re.IGNORECASE), "todo_marker", "medium"),
    (re.compile(r"\bFIXME\b|\bXXX\b", re.IGNORECASE), "fixme_marker", "medium"),
    (re.compile(r"\bplaceholder\b|\bstub(?:bed)?\b", re.IGNORECASE), "placeholder_marker", "high"),
    (
        re.compile(
            r"mock implementation|mock validator|mock analyzer|mock engine|"
            r"for demonstration|would use .+ in production",
            re.IGNORECASE,
        ),
        "mock_implementation",
        "critical",
    ),
    (re.compile(r"not implemented|notimplemented", re.IGNORECASE), "not_implemented_marker", "high"),
    (re.compile(r"\bcoming soon\b", re.IGNORECASE), "coming_soon_marker", "high"),
    (
        re.compile(r"simulate(?:d|s|ing)? (?:validation|test|metric|fitness|result)", re.IGNORECASE),
        "synthetic_validation_marker",
        "critical",
    ),
    (re.compile(r"\b(?:todo!|unimplemented!)\s*\(", re.IGNORECASE), "language_stub_macro", "high"),
)


@dataclass(frozen=True, slots=True)
class Finding:
    branch: str
    path: str
    line: int
    symbol: str | None
    kind: str
    severity: str
    disposition: str
    detail: str
    blob: str
    present_on_canonical: bool
    historical_unique: bool

    @property
    def actionable(self) -> bool:
        return self.disposition == "ACTIONABLE"


@dataclass(frozen=True, slots=True)
class Occurrence:
    branch: str
    path: str


def _run(repo: Path, *args: str) -> bytes:
    try:
        return subprocess.check_output(args, cwd=repo, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"command failed ({exc.returncode}): {' '.join(args)}\n"
            f"{exc.output.decode('utf-8', errors='replace')}"
        ) from exc


def discover_refs(repo: Path, all_branches: bool) -> list[tuple[str, str]]:
    """Return deduplicated ``(branch-name, git-ref)`` pairs."""

    if not all_branches:
        head = _run(repo, "git", "rev-parse", "--abbrev-ref", "HEAD").decode().strip()
        return [(head, "HEAD")]

    raw = _run(
        repo,
        "git",
        "for-each-ref",
        "--format=%(refname)",
        "refs/remotes/origin",
        "refs/heads",
    ).decode()
    candidates: dict[str, str] = {}
    for ref in raw.splitlines():
        if ref == "refs/remotes/origin/HEAD":
            continue
        if ref.startswith("refs/remotes/origin/"):
            candidates[ref.removeprefix("refs/remotes/origin/")] = ref
        elif ref.startswith("refs/heads/"):
            candidates.setdefault(ref.removeprefix("refs/heads/"), ref)
    if not candidates:
        return discover_refs(repo, False)
    return sorted(candidates.items())


def default_canonical_branch(repo: Path) -> str:
    explicit = os.getenv("GITHUB_HEAD_REF")
    if explicit:
        return explicit
    current = _run(repo, "git", "rev-parse", "--abbrev-ref", "HEAD").decode().strip()
    if current != "HEAD":
        return current
    return "main"


def load_shipped_files(repo: Path) -> set[str]:
    """Read the wheel's exact file boundary from the canonical manifest."""

    manifest = tomllib.loads((repo / "pyproject.toml").read_text(encoding="utf-8"))
    wheel = manifest.get("tool", {}).get("hatch", {}).get("build", {}).get("targets", {}).get("wheel", {})
    included = wheel.get("only-include")
    if not isinstance(included, list) or not included:
        raise RuntimeError("wheel build must declare a non-empty tool.hatch.build.targets.wheel.only-include")
    return {str(PurePosixPath(str(path))) for path in included}


def is_scannable(path: str) -> bool:
    p = PurePosixPath(path)
    return p.suffix.lower() in CODE_SUFFIXES or p.name in SPECIAL_CODE_NAMES


def _source_disposition(path: str) -> str | None:
    p = PurePosixPath(path)
    parts = set(p.parts)
    name = p.name.lower()
    if "generated" in parts:
        return "GENERATED_PROJECTION"
    if "redteam_reports" in parts:
        return "SNAPSHOT_COPY"
    if "tests" in parts or name.startswith("test_") or name.endswith("_test.py"):
        return "TEST_FIXTURE"
    if "examples" in parts or "demo" in name or name.endswith("_example.py"):
        return "EXAMPLE"
    if "templates" in parts or "_templates" in parts or name.endswith((".j2", ".ejs", ".t")):
        return "TEMPLATE"
    if "wip" in parts:
        return "WIP"
    return None


def classify_path(path: str, branch: str, canonical_branch: str, shipped_files: set[str]) -> str:
    """Classify standing before judging a finding."""

    structural = _source_disposition(path)
    if structural is not None:
        return structural
    if branch != canonical_branch:
        return "HISTORICAL_BRANCH"
    normalized = str(PurePosixPath(path))
    if normalized in shipped_files:
        return "ACTIONABLE"
    if normalized == "pyproject.toml" or PurePosixPath(path).name in SPECIAL_CODE_NAMES:
        return "ACTIONABLE"
    if normalized.startswith("scripts/") or normalized.startswith(".github/"):
        return "ACTIONABLE"
    return "PRESERVED_NOT_SHIPPED"


def list_blob_occurrences(
    repo: Path,
    refs: Iterable[tuple[str, str]],
) -> tuple[dict[str, list[Occurrence]], int]:
    by_blob: dict[str, list[Occurrence]] = defaultdict(list)
    occurrence_count = 0
    for branch, ref in refs:
        raw = _run(repo, "git", "ls-tree", "-r", "-z", "-l", ref)
        for record in raw.split(b"\0"):
            if not record:
                continue
            meta, raw_path = record.split(b"\t", 1)
            fields = meta.decode().split()
            if len(fields) != 4 or fields[1] != "blob":
                continue
            _mode, _kind, sha, size_text = fields
            path = raw_path.decode("utf-8", errors="surrogateescape")
            if not is_scannable(path):
                continue
            try:
                size = int(size_text)
            except ValueError:
                continue
            if size > MAX_BLOB_BYTES:
                continue
            by_blob[sha].append(Occurrence(branch=branch, path=path))
            occurrence_count += 1
    return by_blob, occurrence_count


def read_blobs(repo: Path, shas: Iterable[str]) -> dict[str, bytes]:
    ordered = list(shas)
    if not ordered:
        return {}
    proc = subprocess.Popen(
        ["git", "cat-file", "--batch"],
        cwd=repo,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert proc.stdin is not None and proc.stdout is not None
    for sha in ordered:
        proc.stdin.write(f"{sha}\n".encode())
    proc.stdin.close()

    result: dict[str, bytes] = {}
    for requested in ordered:
        header = proc.stdout.readline().decode().strip()
        parts = header.split()
        if len(parts) != 3 or parts[1] != "blob":
            raise RuntimeError(f"unexpected git cat-file header for {requested}: {header!r}")
        actual_sha, _kind, size_text = parts
        size = int(size_text)
        payload = proc.stdout.read(size)
        if proc.stdout.read(1) != b"\n":
            raise RuntimeError(f"malformed git cat-file stream for {requested}")
        result[actual_sha] = payload
    stderr = proc.stderr.read() if proc.stderr is not None else b""
    code = proc.wait()
    if code != 0:
        raise RuntimeError(stderr.decode("utf-8", errors="replace"))
    return result


def _decorator_names(node: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    names: set[str] = set()
    for dec in node.decorator_list:
        target: ast.expr = dec.func if isinstance(dec, ast.Call) else dec
        if isinstance(target, ast.Name):
            names.add(target.id)
        elif isinstance(target, ast.Attribute):
            names.add(target.attr)
    return names


def _without_docstring(body: list[ast.stmt]) -> list[ast.stmt]:
    if (
        body
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
        and isinstance(body[0].value.value, str)
    ):
        return body[1:]
    return body


def _raise_name(stmt: ast.stmt) -> str | None:
    if not isinstance(stmt, ast.Raise) or stmt.exc is None:
        return None
    exc = stmt.exc.func if isinstance(stmt.exc, ast.Call) else stmt.exc
    if isinstance(exc, ast.Name):
        return exc.id
    if isinstance(exc, ast.Attribute):
        return exc.attr
    return None


def _constant_return(stmt: ast.stmt) -> tuple[bool, object]:
    if not isinstance(stmt, ast.Return):
        return False, None
    value = stmt.value
    if value is None:
        return True, None
    if isinstance(value, ast.Constant):
        return True, value.value
    if isinstance(value, (ast.List, ast.Tuple, ast.Set)) and not value.elts:
        return True, type(value).__name__.lower()
    if isinstance(value, ast.Dict) and not value.keys:
        return True, "dict"
    if (
        isinstance(value, ast.Call)
        and isinstance(value.func, ast.Name)
        and value.func.id in {"dict", "list", "set", "tuple"}
        and not value.args
        and not value.keywords
    ):
        return True, value.func.id
    return False, None


def _call_name(node: ast.Call) -> str | None:
    target = node.func
    if isinstance(target, ast.Name):
        return target.id
    if isinstance(target, ast.Attribute):
        prefix = target.value.id if isinstance(target.value, ast.Name) else None
        return f"{prefix}.{target.attr}" if prefix else target.attr
    return None


def _marker_findings(text: str) -> list[tuple[int, str | None, str, str, str]]:
    findings: list[tuple[int, str | None, str, str, str]] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        for pattern, kind, severity in MARKERS:
            if pattern.search(stripped):
                findings.append((line_no, None, kind, severity, stripped[:300]))
    return findings


def _python_comment_findings(text: str) -> list[tuple[int, str | None, str, str, str]]:
    findings: list[tuple[int, str | None, str, str, str]] = []
    try:
        tokens = tokenize.generate_tokens(io.StringIO(text).readline)
        for token in tokens:
            if token.type != tokenize.COMMENT:
                continue
            for pattern, kind, severity in MARKERS:
                if pattern.search(token.string):
                    findings.append((token.start[0], None, kind, severity, token.string[:300]))
    except (tokenize.TokenError, IndentationError):
        return findings
    return findings


def python_findings(text: str) -> list[tuple[int, str | None, str, str, str]]:
    """Return AST/comment findings for Python without matching arbitrary literals."""

    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return [(exc.lineno or 1, None, "syntax_error", "critical", str(exc))]

    findings = _python_comment_findings(text)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            body = _without_docstring(node.body)
            intentional_interface = bool(_decorator_names(node) & {"abstractmethod", "overload"})
            if len(body) == 1 and isinstance(body[0], ast.Pass):
                if not intentional_interface:
                    findings.append((node.lineno, node.name, "pass_body", "high", "function body is only pass"))
                continue
            if (
                len(body) == 1
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and body[0].value.value is Ellipsis
            ):
                if not intentional_interface:
                    findings.append((node.lineno, node.name, "ellipsis_body", "high", "function body is only ellipsis"))
                continue
            if len(body) == 1 and _raise_name(body[0]) == "NotImplementedError":
                if not intentional_interface:
                    findings.append(
                        (node.lineno, node.name, "not_implemented", "high", "function only raises NotImplementedError")
                    )
                continue
            if len(body) == 1:
                is_constant, value = _constant_return(body[0])
                if is_constant:
                    if value is None:
                        findings.append(
                            (node.lineno, node.name, "constant_none_return", "medium", "function always returns None")
                        )
                    elif value in {"dict", "list", "set", "tuple"}:
                        findings.append(
                            (
                                node.lineno,
                                node.name,
                                "empty_container_return",
                                "medium",
                                f"function always returns empty {value}",
                            )
                        )
                    elif isinstance(value, bool):
                        findings.append(
                            (
                                node.lineno,
                                node.name,
                                "constant_bool_return",
                                "medium",
                                f"function always returns {value}",
                            )
                        )
                    elif isinstance(value, str) and re.search(
                        r"\b(?:ok|success|alive|placeholder|todo)\b", value, re.IGNORECASE
                    ):
                        findings.append(
                            (
                                node.lineno,
                                node.name,
                                "constant_status_return",
                                "high",
                                f"function always returns status-like literal {value!r}",
                            )
                        )

            semantic_name = node.name.lower()
            validation_function = any(
                word in semantic_name
                for word in ("validat", "fitness", "benchmark", "evaluate", "analy")
            )
            if validation_function:
                for descendant in ast.walk(node):
                    if isinstance(descendant, ast.Call):
                        call_name = _call_name(descendant)
                        if call_name in {
                            "random.random",
                            "random.uniform",
                            "random.randint",
                            "random.choice",
                        }:
                            findings.append(
                                (
                                    descendant.lineno,
                                    node.name,
                                    "randomized_validation",
                                    "critical",
                                    f"validation-like function derives evidence from {call_name}",
                                )
                            )
        elif isinstance(node, ast.ExceptHandler):
            body = _without_docstring(node.body)
            if len(body) == 1 and isinstance(body[0], ast.Pass):
                findings.append(
                    (node.lineno, None, "swallowed_exception", "medium", "exception handler silently passes")
                )
    return findings


def audit(repo: Path, all_branches: bool, canonical_branch: str) -> dict[str, object]:
    refs = discover_refs(repo, all_branches)
    branch_names = {name for name, _ in refs}
    if canonical_branch not in branch_names:
        raise RuntimeError(
            f"canonical branch {canonical_branch!r} is not among observed refs: {sorted(branch_names)}"
        )
    shipped_files = load_shipped_files(repo)
    by_blob, occurrence_count = list_blob_occurrences(repo, refs)
    blobs = read_blobs(repo, by_blob)
    canonical_blobs = {
        sha
        for sha, occurrences in by_blob.items()
        if any(item.branch == canonical_branch for item in occurrences)
    }

    all_findings: list[Finding] = []
    parse_cache: dict[tuple[str, str], list[tuple[int, str | None, str, str, str]]] = {}
    disposition_occurrences: Counter[str] = Counter()

    for sha, occurrences in by_blob.items():
        raw = blobs.get(sha, b"")
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        is_python = any(PurePosixPath(item.path).suffix.lower() in {".py", ".pyi"} for item in occurrences)
        cache_key = (sha, "python" if is_python else "text")
        if cache_key not in parse_cache:
            detected = python_findings(text) if is_python else _marker_findings(text)
            parse_cache[cache_key] = sorted(set(detected), key=lambda item: (item[0], item[2], item[4]))

        present_on_canonical = sha in canonical_blobs
        for occurrence in occurrences:
            disposition = classify_path(
                occurrence.path,
                occurrence.branch,
                canonical_branch,
                shipped_files,
            )
            disposition_occurrences[disposition] += 1
            historical_unique = occurrence.branch != canonical_branch and not present_on_canonical
            for line, symbol, kind, severity, detail in parse_cache[cache_key]:
                all_findings.append(
                    Finding(
                        branch=occurrence.branch,
                        path=occurrence.path,
                        line=line,
                        symbol=symbol,
                        kind=kind,
                        severity=severity,
                        disposition=disposition,
                        detail=detail,
                        blob=sha,
                        present_on_canonical=present_on_canonical,
                        historical_unique=historical_unique,
                    )
                )

    actionable = [item for item in all_findings if item.actionable]
    historical_unique = [item for item in all_findings if item.historical_unique]
    actionable_counts = Counter(item.severity for item in actionable)
    historical_counts = Counter(item.severity for item in historical_unique)
    unique_actionable = {
        (item.blob, item.line, item.symbol, item.kind, item.severity, item.detail)
        for item in actionable
    }
    unique_historical = {
        (item.blob, item.line, item.symbol, item.kind, item.severity, item.detail)
        for item in historical_unique
    }
    broken = any(SEVERITY_ORDER[item.severity] >= SEVERITY_ORDER["high"] for item in actionable)
    return {
        "standing": "BUILD_BROKEN" if broken else "ALIVE",
        "canonical_branch": canonical_branch,
        "branches": sorted(branch_names),
        "branch_count": len(branch_names),
        "shipped_file_count": len(shipped_files),
        "shipped_files": sorted(shipped_files),
        "file_occurrences_scanned": occurrence_count,
        "unique_blobs_scanned": len(blobs),
        "disposition_occurrences": dict(sorted(disposition_occurrences.items())),
        "actionable_occurrences": len(actionable),
        "unique_actionable_findings": len(unique_actionable),
        "actionable_by_severity": dict(sorted(actionable_counts.items())),
        "historical_unique_occurrences": len(historical_unique),
        "unique_historical_findings": len(unique_historical),
        "historical_unique_by_severity": dict(sorted(historical_counts.items())),
        "findings": [asdict(item) | {"actionable": item.actionable} for item in all_findings],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--all-branches", action="store_true")
    parser.add_argument("--canonical-branch")
    parser.add_argument("--json", type=Path, dest="json_path")
    parser.add_argument("--fail-on", choices=["none", "low", "medium", "high", "critical"], default="high")
    parser.add_argument("--max-print", type=int, default=100)
    args = parser.parse_args(argv)

    repo = args.repo.resolve()
    canonical = args.canonical_branch or default_canonical_branch(repo)
    report = audit(repo, args.all_branches, canonical)
    if args.json_path:
        args.json_path.parent.mkdir(parents=True, exist_ok=True)
        args.json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({key: value for key, value in report.items() if key != "findings"}, indent=2, sort_keys=True))
    findings = report["findings"]
    ordered = sorted(
        findings,
        key=lambda item: (
            0 if item["actionable"] else 1,
            -SEVERITY_ORDER[item["severity"]],
            item["branch"],
            item["path"],
            item["line"],
            item["kind"],
        ),
    )
    for item in ordered[: args.max_print]:
        symbol = f"::{item['symbol']}" if item["symbol"] else ""
        marker = "DO" if item["actionable"] else item["disposition"]
        print(
            f"{item['severity'].upper():8} {marker:24} "
            f"{item['branch']}:{item['path']}:{item['line']}{symbol} "
            f"[{item['kind']}] {item['detail']}"
        )
    if len(ordered) > args.max_print:
        print(f"... {len(ordered) - args.max_print} additional occurrences in JSON report")

    if args.fail_on == "none":
        return 0
    threshold = SEVERITY_ORDER[args.fail_on]
    actionable = [item for item in findings if item["actionable"]]
    return 1 if any(SEVERITY_ORDER[item["severity"]] >= threshold for item in actionable) else 0


if __name__ == "__main__":
    sys.exit(main())
