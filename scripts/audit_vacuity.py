#!/usr/bin/env python3
"""Audit every reachable branch/file for stub or vacuous implementations.

The scanner is deliberately repository-graph aware: identical Git blobs are parsed
once, then findings are projected back onto every branch/path occurrence. Python
receives AST-level checks; other implementation text receives conservative marker
checks. Intentional abstract/protocol methods are classified rather than accused.
"""

from __future__ import annotations

import argparse
import ast
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from typing import Iterable

SEVERITY_ORDER = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
CODE_SUFFIXES = {
    ".py", ".pyi", ".js", ".jsx", ".ts", ".tsx", ".vue", ".rs", ".go", ".sh",
    ".bash", ".zsh", ".toml", ".yaml", ".yml", ".json", ".j2", ".ejs", ".t",
}
SPECIAL_CODE_NAMES = {"Dockerfile", "Makefile", "justfile", "Procfile"}
MAX_BLOB_BYTES = 2_000_000
TEXT_MARKERS = (
    (re.compile(r"\bTODO\b", re.IGNORECASE), "todo_marker", "medium"),
    (re.compile(r"\bFIXME\b|\bXXX\b", re.IGNORECASE), "fixme_marker", "medium"),
    (re.compile(r"\bplaceholder\b|\bstub(?:bed)?\b", re.IGNORECASE), "placeholder_marker", "high"),
    (re.compile(r"mock implementation|for demonstration|would use .+ in production", re.IGNORECASE), "mock_implementation", "critical"),
    (re.compile(r"not implemented|notimplemented", re.IGNORECASE), "not_implemented_marker", "high"),
    (re.compile(r"\bcoming soon\b", re.IGNORECASE), "coming_soon_marker", "high"),
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
    """Return (display_branch, git_ref) pairs without duplicate local/remote refs."""
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
            name = ref.removeprefix("refs/remotes/origin/")
            candidates[name] = ref
        elif ref.startswith("refs/heads/"):
            name = ref.removeprefix("refs/heads/")
            candidates.setdefault(name, ref)
    if not candidates:
        return discover_refs(repo, False)
    return sorted(candidates.items())


def is_scannable(path: str) -> bool:
    p = PurePosixPath(path)
    return p.suffix.lower() in CODE_SUFFIXES or p.name in SPECIAL_CODE_NAMES


def classify_path(path: str) -> str:
    parts = set(PurePosixPath(path).parts)
    name = PurePosixPath(path).name.lower()
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
    if "docs" in parts or PurePosixPath(path).suffix.lower() in {".md", ".rst", ".html"}:
        return "DOCUMENTATION"
    if "wip" in parts:
        return "WIP"
    return "ACTIONABLE"


def list_blob_occurrences(repo: Path, refs: Iterable[tuple[str, str]]) -> tuple[dict[str, list[Occurrence]], int]:
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
        newline = proc.stdout.read(1)
        if newline != b"\n":
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
        if isinstance(dec, ast.Name):
            names.add(dec.id)
        elif isinstance(dec, ast.Attribute):
            names.add(dec.attr)
        elif isinstance(dec, ast.Call):
            target = dec.func
            if isinstance(target, ast.Name):
                names.add(target.id)
            elif isinstance(target, ast.Attribute):
                names.add(target.attr)
    return names


def _without_docstring(body: list[ast.stmt]) -> list[ast.stmt]:
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
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
    if isinstance(value, ast.Call) and isinstance(value.func, ast.Name) and value.func.id in {"dict", "list", "set", "tuple"} and not value.args and not value.keywords:
        return True, value.func.id
    return False, None


def python_findings(text: str) -> list[tuple[int, str | None, str, str, str]]:
    """Return line, symbol, kind, severity, detail for AST-level findings."""
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return [(exc.lineno or 1, None, "syntax_error", "critical", str(exc))]

    findings: list[tuple[int, str | None, str, str, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            body = _without_docstring(node.body)
            decorators = _decorator_names(node)
            intentional_interface = bool(decorators & {"abstractmethod", "overload"})
            if len(body) == 1 and isinstance(body[0], ast.Pass):
                if not intentional_interface:
                    findings.append((node.lineno, node.name, "pass_body", "high", "function body is only pass"))
                continue
            if len(body) == 1 and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and body[0].value.value is Ellipsis:
                if not intentional_interface:
                    findings.append((node.lineno, node.name, "ellipsis_body", "high", "function body is only ellipsis"))
                continue
            if len(body) == 1 and _raise_name(body[0]) == "NotImplementedError":
                if not intentional_interface:
                    findings.append((node.lineno, node.name, "not_implemented", "high", "function only raises NotImplementedError"))
                continue
            if len(body) == 1:
                is_constant, value = _constant_return(body[0])
                if is_constant:
                    if value is None:
                        findings.append((node.lineno, node.name, "constant_none_return", "medium", "function always returns None"))
                    elif value in {"dict", "list", "set", "tuple"}:
                        findings.append((node.lineno, node.name, "empty_container_return", "medium", f"function always returns empty {value}"))
                    elif isinstance(value, bool):
                        findings.append((node.lineno, node.name, "constant_bool_return", "medium", f"function always returns {value}"))
                    elif isinstance(value, str) and re.search(r"\b(?:ok|success|alive|placeholder|stub|todo)\b", value, re.IGNORECASE):
                        findings.append((node.lineno, node.name, "constant_status_return", "high", f"function always returns status-like literal {value!r}"))
        elif isinstance(node, ast.ExceptHandler):
            body = _without_docstring(node.body)
            if len(body) == 1 and isinstance(body[0], ast.Pass):
                findings.append((node.lineno, None, "swallowed_exception", "medium", "exception handler silently passes"))
    return findings


def text_findings(text: str) -> list[tuple[int, str | None, str, str, str]]:
    findings: list[tuple[int, str | None, str, str, str]] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        for pattern, kind, severity in TEXT_MARKERS:
            if pattern.search(stripped):
                findings.append((line_no, None, kind, severity, stripped[:300]))
    return findings


def audit(repo: Path, all_branches: bool) -> dict[str, object]:
    refs = discover_refs(repo, all_branches)
    by_blob, occurrence_count = list_blob_occurrences(repo, refs)
    blobs = read_blobs(repo, by_blob)
    all_findings: list[Finding] = []
    parse_cache: dict[tuple[str, str], list[tuple[int, str | None, str, str, str]]] = {}

    for sha, occurrences in by_blob.items():
        raw = blobs.get(sha, b"")
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        suffixes = {PurePosixPath(item.path).suffix.lower() for item in occurrences}
        cache_key = (sha, "python" if ".py" in suffixes or ".pyi" in suffixes else "text")
        if cache_key not in parse_cache:
            detected = text_findings(text)
            if cache_key[1] == "python":
                detected.extend(python_findings(text))
            # Stable dedup within one blob.
            parse_cache[cache_key] = sorted(set(detected), key=lambda item: (item[0], item[2], item[4]))
        for occurrence in occurrences:
            disposition = classify_path(occurrence.path)
            for line, symbol, kind, severity, detail in parse_cache[cache_key]:
                effective = severity
                if disposition != "ACTIONABLE" and severity in {"critical", "high"}:
                    effective = "medium"
                all_findings.append(
                    Finding(
                        branch=occurrence.branch,
                        path=occurrence.path,
                        line=line,
                        symbol=symbol,
                        kind=kind,
                        severity=effective,
                        disposition=disposition,
                        detail=detail,
                        blob=sha,
                    )
                )

    actionable = [item for item in all_findings if item.actionable]
    counts = Counter(item.severity for item in actionable)
    unique_actionable = {
        (item.blob, item.line, item.symbol, item.kind, item.severity, item.detail)
        for item in actionable
    }
    return {
        "standing": "BUILD_BROKEN" if any(SEVERITY_ORDER[item.severity] >= SEVERITY_ORDER["high"] for item in actionable) else "ALIVE",
        "branches": [name for name, _ in refs],
        "branch_count": len(refs),
        "file_occurrences_scanned": occurrence_count,
        "unique_blobs_scanned": len(blobs),
        "actionable_occurrences": len(actionable),
        "unique_actionable_findings": len(unique_actionable),
        "actionable_by_severity": dict(sorted(counts.items())),
        "findings": [asdict(item) | {"actionable": item.actionable} for item in all_findings],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--all-branches", action="store_true")
    parser.add_argument("--json", type=Path, dest="json_path")
    parser.add_argument("--fail-on", choices=["none", "low", "medium", "high", "critical"], default="high")
    parser.add_argument("--max-print", type=int, default=100)
    args = parser.parse_args(argv)

    report = audit(args.repo.resolve(), args.all_branches)
    if args.json_path:
        args.json_path.parent.mkdir(parents=True, exist_ok=True)
        args.json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps({k: v for k, v in report.items() if k != "findings"}, indent=2, sort_keys=True))
    actionable = [item for item in report["findings"] if item["actionable"]]
    actionable.sort(key=lambda item: (-SEVERITY_ORDER[item["severity"]], item["branch"], item["path"], item["line"], item["kind"]))
    for item in actionable[: args.max_print]:
        symbol = f"::{item['symbol']}" if item["symbol"] else ""
        print(
            f"{item['severity'].upper():8} {item['branch']}:{item['path']}:{item['line']}{symbol} "
            f"[{item['kind']}] {item['detail']}"
        )
    if len(actionable) > args.max_print:
        print(f"... {len(actionable) - args.max_print} additional actionable occurrences in JSON report")

    if args.fail_on == "none":
        return 0
    threshold = SEVERITY_ORDER[args.fail_on]
    return 1 if any(SEVERITY_ORDER[item["severity"]] >= threshold for item in actionable) else 0


if __name__ == "__main__":
    sys.exit(main())
