# coordination_cli.py
"""
Typer port of coordination_helper.sh (happy path, no error handling).
"""

from __future__ import annotations
import os, json, time, secrets, datetime, pathlib, random
import typer

###############################################################################
# Constants & Paths
###############################################################################
app                 = typer.Typer(help="SwarmSH - Agent Coordination CLI")
work_app            = typer.Typer(help="Work-item commands")
ai_app              = typer.Typer(help="AI / Claude helpers")
scrum_app           = typer.Typer(help="Scrum@Scale ceremonies")
util_app            = typer.Typer(help="Utility & maintenance")

app.add_typer(work_app,  name="work")
app.add_typer(ai_app,    name="ai")
app.add_typer(scrum_app, name="scrum")
app.add_typer(util_app,  name="util")

ROOT                = pathlib.Path(os.getenv("COORDINATION_DIR",
                                             "~/s2s/agent_coordination")).expanduser()
WORK_CLAIMS         = ROOT / "work_claims.json"
FAST_CLAIMS         = ROOT / "work_claims_fast.jsonl"
AGENT_STATUS        = ROOT / "agent_status.json"
COORD_LOG           = ROOT / "coordination_log.json"
ROOT.mkdir(parents=True, exist_ok=True)

OTEL_SERVICE_NAME   = "s2s-coordination"
# -----------------------------------------------------------------------------
def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

def _ns_id(prefix: str) -> str:
    return f"{prefix}_{time.time_ns()}"

def _read_json(path: pathlib.Path, default):
    if path.exists():
        return json.loads(path.read_text())
    return default

def _write_json(path: pathlib.Path, data):
    path.write_text(json.dumps(data, indent=2))

def log_span(name: str, attrs: dict[str, str]|None=None):
    """One-liner stub.  Replace with OTLP exporter later."""
    span = {"ts": _now_iso(), "name": name, "attrs": attrs or {}}
    with open(ROOT / "telemetry_spans.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(span) + "\n")

def ask_claude(prompt: str) -> dict:
    """Placeholder AI helper."""
    random.seed(prompt);  # deterministic-ish dummy
    return {"analysis": "stub", "confidence": round(random.random(), 2)}

###############################################################################
# Work management
###############################################################################
@work_app.command("claim")
def claim(work_type: str,
          description: str,
          priority: str = "medium",
          team: str = "autonomous_team"):
    """Claim a new work item (fast-path)."""
    agent_id     = os.getenv("AGENT_ID", _ns_id("agent"))
    work_item_id = _ns_id("work")
    entry = {
        "work_item_id": work_item_id,
        "agent_id": agent_id,
        "claimed_at": _now_iso(),
        "work_type": work_type,
        "priority": priority,
        "description": description,
        "status": "active",
        "team": team,
    }
    with open(FAST_CLAIMS, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry)+"\n")
    log_span("s2s.work.claim_fast", {"work_item_id": work_item_id})
    typer.echo(json.dumps({"ok": True, "work_item_id": work_item_id}))

@work_app.command("progress")
def progress(work_id: str, percent: int = typer.Argument(..., min=0, max=100)):
    """Update % progress (works only on big JSON file)."""
    claims = _read_json(WORK_CLAIMS, [])
    for w in claims:
        if w["work_item_id"] == work_id:
            w["progress"] = percent
            w["last_update"] = _now_iso()
            break
    _write_json(WORK_CLAIMS, claims)
    log_span("s2s.work.progress", {"work_item_id": work_id, "percent": str(percent)})
    typer.echo(json.dumps({"ok": True}))

@work_app.command("complete")
def complete(work_id: str, result: str = "success", points: int = 5):
    """Mark work item done and add to velocity log."""
    # update claim
    claims = _read_json(WORK_CLAIMS, [])
    for w in claims:
        if w["work_item_id"] == work_id:
            w.update({"status": "completed", "completed_at": _now_iso(), "result": result})
            break
    _write_json(WORK_CLAIMS, claims)
    # coordination log
    done = _read_json(COORD_LOG, [])
    done.append({"work_item_id": work_id, "result": result, "velocity_points": points,
                 "ts": _now_iso()})
    _write_json(COORD_LOG, done)
    log_span("s2s.work.complete", {"work_item_id": work_id})
    typer.echo(json.dumps({"ok": True}))

@work_app.command("list")
def list_work(team: str = "all"):
    """List active work (fast-path JSONL scan)."""
    if not FAST_CLAIMS.exists():
        return
    for line in FAST_CLAIMS.read_text().splitlines():
        w = json.loads(line)
        if w["status"] == "active" and (team == "all" or w["team"] == team):
            typer.echo(f"{w['work_item_id']} {w['work_type']} ({w['priority']}) [{w['team']}]")

###############################################################################
# AI helpers (stubs)
###############################################################################
@ai_app.command("priorities")
def ai_priorities():
    data = ask_claude("priorities")
    (ROOT / "claude_priority_analysis.json").write_text(json.dumps(data, indent=2))
    typer.echo(json.dumps(data))

@ai_app.command("health")
def ai_health():
    data = ask_claude("health")
    (ROOT / "claude_health_analysis.json").write_text(json.dumps(data, indent=2))
    typer.echo(json.dumps(data))

###############################################################################
# Scrum ceremonies (static printers)
###############################################################################
@scrum_app.command("dashboard")
def dashboard():
    typer.echo("🚀 Scrum Dashboard — active items:")
    list_work()

@scrum_app.command("pi-planning")
def pi_planning():
    typer.echo("🎯 Running PI Planning… (stub)")
    log_span("scrum.pi_planning")

###############################################################################
# Utilities
###############################################################################
@util_app.command("optimize")
def optimize():
    """Archive completed work into backups/ and keep active list small."""
    claims = _read_json(WORK_CLAIMS, [])
    active = [w for w in claims if w.get("status") != "completed"]
    archive = [w for w in claims if w.get("status") == "completed"]
    if archive:
        arch_dir = ROOT / "archived_claims"
        arch_dir.mkdir(exist_ok=True)
        fname = arch_dir / f"completed_{int(time.time())}.json"
        _write_json(fname, archive)
    _write_json(WORK_CLAIMS, active)
    typer.echo(f"Archived {len(archive)} items")

@util_app.command("generate-id")
def gen_id():
    typer.echo(_ns_id("agent"))

###############################################################################
# Bootstrap
###############################################################################
if __name__ == "__main__":
    app()