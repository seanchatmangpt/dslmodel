#!/usr/bin/env python3
"""
5-ONE Git Parliament OTEL Monitoring
===================================

Complete OpenTelemetry instrumentation for the 5-ONE Git Parliament system,
providing comprehensive monitoring for:
- Parliamentary motion lifecycle
- Federated voting and liquid democracy
- Git operations and merge decisions
- Agent coordination and WASM execution
- Security and anomaly detection

This monitoring layer ensures complete observability of the democratic
git governance system with real-time insights and alerts.
"""

import asyncio
import json
import time
import subprocess
import pathlib
import uuid
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hashlib
from functools import wraps

from opentelemetry import trace, metrics, baggage, context
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.trace import TracerProvider, SpanProcessor
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace import Status, StatusCode
# from opentelemetry.instrumentation.utils import unwrap  # Not needed for this implementation

from loguru import logger


# Global tracer for the parliament system
_tracer: Optional[trace.Tracer] = None
_meter: Optional[metrics.Meter] = None


def setup_5one_monitoring(service_name: str = "git-parliament-5one",
                         otlp_endpoint: str = "http://localhost:4317") -> Tuple[trace.Tracer, metrics.Meter]:
    """Setup complete OTEL monitoring for 5-ONE parliament"""
    
    resource = Resource.create({
        "service.name": service_name,
        "service.version": "1.0.0",
        "service.namespace": "5one",
        "deployment.environment": "production",
        "parliament.type": "git_roberts_rules"
    })
    
    # Setup tracing
    tracer_provider = TracerProvider(resource=resource)
    
    try:
        otlp_trace_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
        tracer_provider.add_span_processor(BatchSpanProcessor(otlp_trace_exporter))
        logger.info(f"OTLP trace exporter configured: {otlp_endpoint}")
    except Exception as e:
        logger.warning(f"OTLP trace exporter unavailable: {e}, using console")
        tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    
    trace.set_tracer_provider(tracer_provider)
    
    # Setup metrics
    try:
        otlp_metric_exporter = OTLPMetricExporter(endpoint=otlp_endpoint, insecure=True)
        metric_reader = PeriodicExportingMetricReader(
            exporter=otlp_metric_exporter,
            export_interval_millis=30000
        )
        meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    except Exception as e:
        logger.warning(f"OTLP metric exporter unavailable: {e}")
        meter_provider = MeterProvider(resource=resource)
    
    metrics.set_meter_provider(meter_provider)
    
    global _tracer, _meter
    _tracer = trace.get_tracer(__name__, "1.0.0")
    _meter = metrics.get_meter(__name__, "1.0.0")
    
    # Initialize metrics
    _setup_parliament_metrics()
    
    logger.info("5-ONE Parliament monitoring initialized")
    return _tracer, _meter


def _setup_parliament_metrics():
    """Setup all parliamentary metrics"""
    global motion_counter, vote_counter, delegation_counter
    global motion_duration, vote_tally_duration, git_operation_duration
    global active_motions_gauge, delegation_depth_histogram, quorum_rate_gauge
    global merge_success_counter, security_alert_counter
    
    # Motion metrics
    motion_counter = _meter.create_counter(
        "parliament.motions.created",
        description="Total motions created",
        unit="motion"
    )
    
    vote_counter = _meter.create_counter(
        "parliament.votes.cast",
        description="Total votes cast",
        unit="vote"
    )
    
    delegation_counter = _meter.create_counter(
        "parliament.delegations.created",
        description="Total delegation relationships created",
        unit="delegation"
    )
    
    # Duration metrics
    motion_duration = _meter.create_histogram(
        "parliament.motion.lifecycle_duration_ms",
        description="Duration from motion creation to decision",
        unit="ms"
    )
    
    vote_tally_duration = _meter.create_histogram(
        "parliament.vote.tally_duration_ms",
        description="Duration to tally votes with delegation",
        unit="ms"
    )
    
    git_operation_duration = _meter.create_histogram(
        "parliament.git.operation_duration_ms",
        description="Duration of git operations",
        unit="ms"
    )
    
    # State metrics
    active_motions_gauge = _meter.create_up_down_counter(
        "parliament.motions.active",
        description="Currently active motions"
    )
    
    delegation_depth_histogram = _meter.create_histogram(
        "parliament.delegation.depth",
        description="Depth of delegation chains"
    )
    
    quorum_rate_gauge = _meter.create_gauge(
        "parliament.quorum.rate",
        description="Current quorum participation rate"
    )
    
    # Outcome metrics
    merge_success_counter = _meter.create_counter(
        "parliament.merge.success",
        description="Successful motion merges"
    )
    
    security_alert_counter = _meter.create_counter(
        "parliament.security.alerts",
        description="Security alerts detected"
    )


def parliament_span(operation: str):
    """Decorator to create parliament spans with proper context"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with _tracer.start_as_current_span(
                f"parliament.{operation}",
                kind=trace.SpanKind.INTERNAL
            ) as span:
                span.set_attribute("parliament.operation", operation)
                span.set_attribute("parliament.timestamp", datetime.utcnow().isoformat())
                
                try:
                    result = func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    raise
        
        return wrapper
    return decorator


def git_operation_span(operation: str):
    """Decorator for git operations with timing"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with _tracer.start_as_current_span(
                f"git.{operation}",
                kind=trace.SpanKind.CLIENT
            ) as span:
                span.set_attribute("git.operation", operation)
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    duration_ms = (time.time() - start_time) * 1000
                    
                    git_operation_duration.record(
                        duration_ms,
                        {"operation": operation}
                    )
                    
                    span.set_attribute("git.duration_ms", duration_ms)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except subprocess.CalledProcessError as e:
                    span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR, f"Git error: {e}"))
                    raise
        
        return wrapper
    return decorator


# Instrumented Parliament class
class InstrumentedParliament:
    """Parliament with complete OTEL instrumentation"""
    
    def __init__(self, repo_path: pathlib.Path = None):
        self.repo = repo_path or pathlib.Path(".").resolve()
        self.motion_metadata: Dict[str, Dict[str, Any]] = {}
        
        if not _tracer or not _meter:
            setup_5one_monitoring()
    
    @parliament_span("motion.create")
    def new_motion(self, title: str, body: str) -> str:
        """Create new motion with full tracing"""
        motion_id = f"M{uuid.uuid4().hex[:6]}"
        
        span = trace.get_current_span()
        span.set_attribute("motion.id", motion_id)
        span.set_attribute("motion.title", title)
        span.set_attribute("motion.body_length", len(body))
        
        # Store metadata for lifecycle tracking
        self.motion_metadata[motion_id] = {
            "title": title,
            "created_at": datetime.utcnow(),
            "author": baggage.get_baggage("parliament.author") or "system"
        }
        
        # Create motion file
        path = self.repo / f"motions/{motion_id}.md"
        path.parent.mkdir(exist_ok=True)
        path.write_text(f"# {title}\n\n{body}\n")
        
        # Git operations with tracing
        self._git_add(path)
        self._git_branch(f"motions/{motion_id}")
        self._git_commit(f"motion: {motion_id} {title}")
        
        # Update metrics
        motion_counter.add(1, {
            "motion.type": "proposal",
            "author": self.motion_metadata[motion_id]["author"]
        })
        active_motions_gauge.add(1)
        
        logger.info(f"Motion created: {motion_id} - {title}")
        return motion_id
    
    @parliament_span("motion.second")
    def second(self, motion_sha: str, speaker: str):
        """Second a motion with tracing"""
        span = trace.get_current_span()
        span.set_attribute("motion.sha", motion_sha)
        span.set_attribute("speaker", speaker)
        
        message = json.dumps({
            "speaker": speaker,
            "ts": datetime.utcnow().isoformat(),
            "trace_id": format(span.get_span_context().trace_id, "032x")
        })
        
        self._git_note_add("second", motion_sha, message)
        
        logger.info(f"Motion seconded by {speaker}: {motion_sha}")
    
    @parliament_span("motion.debate")
    def debate(self, motion_sha: str, speaker: str, stance: str, argument: str):
        """Add debate entry with tracing"""
        span = trace.get_current_span()
        span.set_attribute("motion.sha", motion_sha)
        span.set_attribute("speaker", speaker)
        span.set_attribute("debate.stance", stance)
        span.set_attribute("debate.argument_length", len(argument))
        
        message = json.dumps({
            "sp": speaker,
            "st": stance,
            "arg": argument,
            "ts": datetime.utcnow().isoformat()
        })
        
        self._git_note_add("debate", motion_sha, message)
        
        logger.info(f"Debate added by {speaker} ({stance}): {motion_sha}")
    
    @parliament_span("vote.cast")
    def vote(self, motion_id: str, repo_name: str, val: str, weight: float = 1.0):
        """Cast vote with full instrumentation"""
        span = trace.get_current_span()
        span.set_attribute("motion.id", motion_id)
        span.set_attribute("vote.repo", repo_name)
        span.set_attribute("vote.value", val)
        span.set_attribute("vote.weight", weight)
        
        # Validate vote
        if val not in ["for", "against", "abstain"]:
            span.set_status(Status(StatusCode.ERROR, "Invalid vote value"))
            raise ValueError(f"Invalid vote: {val}")
        
        if weight < 0 or weight > 10:
            security_alert_counter.add(1, {"alert.type": "suspicious_weight"})
            span.add_event("security.alert", {"type": "suspicious_vote_weight", "weight": weight})
        
        # Create vote ref
        ref = f"refs/vote/{motion_id}/{repo_name}/{uuid.uuid4().hex}"
        blob = json.dumps({
            "vote": val,
            "weight": weight,
            "timestamp": datetime.utcnow().isoformat(),
            "trace_id": format(span.get_span_context().trace_id, "032x")
        }).encode()
        
        sha = self._git_hash_object(blob)
        self._git_update_ref(ref, sha)
        # Only push if origin exists (skip for local testing)
        try:
            subprocess.run(["git", "remote", "get-url", "origin"], 
                          check=True, capture_output=True, cwd=self.repo)
            self._git_push("origin", ref)
        except subprocess.CalledProcessError:
            # No origin remote, store vote locally only
            logger.info(f"Stored vote locally (no origin): {ref}")
        
        # Update metrics
        vote_counter.add(1, {
            "motion.id": motion_id,
            "vote.value": val,
            "vote.repo": repo_name
        })
        
        logger.info(f"Vote cast: {repo_name} votes {val} on {motion_id} (weight: {weight})")
    
    @git_operation_span("add")
    def _git_add(self, path: pathlib.Path):
        subprocess.run(["git", "add", str(path)], check=True, cwd=self.repo)
    
    @git_operation_span("branch")
    def _git_branch(self, name: str, base: str = "HEAD"):
        subprocess.run(["git", "branch", name, base], check=True, cwd=self.repo)
    
    @git_operation_span("commit")
    def _git_commit(self, message: str):
        subprocess.run(["git", "commit", "-m", message], check=True, cwd=self.repo)
    
    @git_operation_span("notes.add")
    def _git_note_add(self, ref: str, target: str, message: str):
        # Use append instead of add to allow multiple notes on same object
        subprocess.run(
            ["git", "notes", f"--ref={ref}", "append", "-m", message, target],
            check=True, cwd=self.repo
        )
    
    @git_operation_span("hash_object")
    def _git_hash_object(self, blob: bytes) -> str:
        result = subprocess.run(
            ["git", "hash-object", "-w", "--stdin"],
            input=blob, capture_output=True, check=True, cwd=self.repo
        )
        return result.stdout.decode().strip()
    
    @git_operation_span("update_ref")
    def _git_update_ref(self, ref: str, sha: str):
        subprocess.run(["git", "update-ref", ref, sha], check=True, cwd=self.repo)
    
    @git_operation_span("push")
    def _git_push(self, remote: str, refspec: str):
        subprocess.run(["git", "push", remote, refspec], check=True, cwd=self.repo)


# Instrumented voting tally
@parliament_span("vote.tally")
def instrumented_tally(motion_id: str, remotes: list[str], quorum: float = 0.6) -> bool:
    """Tally votes with delegation and full instrumentation"""
    span = trace.get_current_span()
    span.set_attribute("motion.id", motion_id)
    span.set_attribute("tally.remotes", len(remotes))
    span.set_attribute("tally.quorum", quorum)
    
    start_time = time.time()
    
    votes = {}
    delegation_map = {}
    
    # Collect votes and delegations
    for remote in remotes:
        votes_from_remote, delegations_from_remote = _collect_votes_and_delegations(
            motion_id, remote
        )
        votes.update(votes_from_remote)
        delegation_map.update(delegations_from_remote)
    
    # Resolve delegations
    resolved_votes = _resolve_delegations(votes, delegation_map)
    
    # Calculate results
    total_weight = sum(w for _, w in resolved_votes.values())
    yes_weight = sum(w for v, w in resolved_votes.values() if v == "for")
    
    participation_rate = len(resolved_votes) / max(1, len(votes) + len(delegation_map))
    approval_rate = yes_weight / max(total_weight, 1)
    
    # Record metrics
    duration_ms = (time.time() - start_time) * 1000
    vote_tally_duration.record(duration_ms, {"motion.id": motion_id})
    quorum_rate_gauge.set(participation_rate)
    
    # Set span attributes
    span.set_attribute("tally.total_votes", len(resolved_votes))
    span.set_attribute("tally.total_weight", total_weight)
    span.set_attribute("tally.yes_weight", yes_weight)
    span.set_attribute("tally.participation_rate", participation_rate)
    span.set_attribute("tally.approval_rate", approval_rate)
    span.set_attribute("tally.duration_ms", duration_ms)
    
    result = approval_rate >= quorum
    span.set_attribute("tally.result", "accepted" if result else "rejected")
    
    logger.info(
        f"Vote tally for {motion_id}: "
        f"{'ACCEPTED' if result else 'REJECTED'} "
        f"(approval: {approval_rate:.1%}, participation: {participation_rate:.1%})"
    )
    
    return result


def _collect_votes_and_delegations(motion_id: str, remote: str) -> Tuple[Dict, Dict]:
    """Collect votes and delegations from a remote"""
    votes = {}
    delegations = {}
    
    # Collect votes
    try:
        out = subprocess.check_output(
            ["git", "ls-remote", remote, f"refs/vote/{motion_id}/*"],
            stderr=subprocess.DEVNULL
        )
        
        for line in out.decode().splitlines():
            sha, ref = line.split()
            parts = ref.split("/")
            if len(parts) >= 4:
                repo_name = parts[3]
                
                # Fetch vote blob
                blob = subprocess.check_output(
                    ["git", "fetch", remote, sha, "--depth=1", "--stdout"],
                    stderr=subprocess.DEVNULL
                )
                vote_data = json.loads(blob.decode())
                votes[repo_name] = (vote_data["vote"], vote_data.get("weight", 1.0))
    
    except subprocess.CalledProcessError:
        pass  # No votes from this remote
    
    # Collect delegations
    try:
        out = subprocess.check_output(
            ["git", "ls-remote", remote, "refs/delegate/*"],
            stderr=subprocess.DEVNULL
        )
        
        for line in out.decode().splitlines():
            sha, ref = line.split()
            delegator = ref.split("/", 2)[2]
            
            # Fetch delegation target
            delegate = subprocess.check_output(
                ["git", "show", sha],
                stderr=subprocess.DEVNULL
            ).decode().strip()
            
            delegations[delegator] = delegate
    
    except subprocess.CalledProcessError:
        pass  # No delegations from this remote
    
    return votes, delegations


def _resolve_delegations(votes: Dict, delegation_map: Dict) -> Dict:
    """Resolve vote delegations"""
    resolved = {}
    
    for voter, vote_data in votes.items():
        # Follow delegation chain
        final_voter = voter
        visited = set()
        depth = 0
        
        while final_voter in delegation_map and final_voter not in visited:
            visited.add(final_voter)
            final_voter = delegation_map[final_voter]
            depth += 1
            
            if depth > 10:  # Prevent infinite delegation chains
                security_alert_counter.add(1, {"alert.type": "delegation_depth_exceeded"})
                break
        
        # Record delegation depth
        if depth > 0:
            delegation_depth_histogram.record(depth, {"voter": voter})
        
        resolved[final_voter] = vote_data
    
    return resolved


# Instrumented merge oracle
@parliament_span("merge_oracle.decide")
def instrumented_merge_decision(motion_id: str):
    """Decide on motion with full instrumentation"""
    span = trace.get_current_span()
    span.set_attribute("motion.id", motion_id)
    
    # Tally votes
    accepted = instrumented_tally(motion_id, ["origin"])
    
    # Execute decision
    if accepted:
        try:
            subprocess.run(
                ["git", "merge", "--no-ff", f"motions/{motion_id}"],
                check=True
            )
            merge_success_counter.add(1, {"motion.id": motion_id})
            span.set_attribute("merge.outcome", "accepted")
            logger.info(f"Motion {motion_id} merged successfully")
        except subprocess.CalledProcessError as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, "Merge failed"))
            raise
    else:
        subprocess.run(
            ["git", "branch", "-D", f"motions/{motion_id}"],
            check=True
        )
        span.set_attribute("merge.outcome", "rejected")
        logger.info(f"Motion {motion_id} rejected and branch deleted")
    
    active_motions_gauge.add(-1)


# Agent instrumentation wrapper
def instrument_agent(agent_name: str):
    """Decorator to instrument agent actions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            with _tracer.start_as_current_span(
                f"agent.{agent_name}",
                kind=trace.SpanKind.INTERNAL
            ) as span:
                span.set_attribute("agent.name", agent_name)
                span.set_attribute("agent.args", str(args))
                
                # Set agent context
                token = context.attach(
                    baggage.set_baggage("parliament.author", agent_name)
                )
                
                try:
                    result = await func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    raise
                finally:
                    context.detach(token)
        
        return wrapper
    return decorator


# Example instrumented agent
@instrument_agent("motion_author")
async def motion_author_agent(prompt_file: str):
    """Author a motion based on prompt"""
    with open(prompt_file) as f:
        prompt = f.read().strip()
    
    # Generate motion (placeholder for DSPy logic)
    title = f"Motion: {prompt[:50]}"
    body = f"This motion proposes to {prompt}.\n\nRationale: ..."
    
    parliament = InstrumentedParliament()
    motion_id = parliament.new_motion(title, body)
    
    return motion_id


# Test the complete system
async def test_5one_parliament():
    """Test the instrumented parliament system"""
    
    # Setup monitoring
    setup_5one_monitoring()
    
    parliament = InstrumentedParliament()
    
    # Create motion
    motion_id = parliament.new_motion(
        "Adopt OTEL v1.4",
        "This motion proposes adopting OpenTelemetry v1.4 for enhanced observability."
    )
    
    # Get motion SHA (for demo, use HEAD)
    motion_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"]
    ).decode().strip()
    
    # Second the motion
    parliament.second(motion_sha, "alice")
    
    # Debate
    parliament.debate(motion_sha, "bob", "pro", "OTEL provides excellent observability")
    parliament.debate(motion_sha, "charlie", "con", "Migration cost is high")
    
    # Vote
    parliament.vote(motion_id, "repo_alice", "for", 1.0)
    parliament.vote(motion_id, "repo_bob", "for", 1.0)
    parliament.vote(motion_id, "repo_charlie", "against", 1.0)
    
    # Tally and decide
    instrumented_merge_decision(motion_id)
    
    print(f"Parliament test complete for motion {motion_id}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_5one_parliament())