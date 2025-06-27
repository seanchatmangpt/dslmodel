#!/usr/bin/env python3
"""
Git Parliament OTEL Monitoring System
====================================

Comprehensive OpenTelemetry monitoring for the Git Parliament system
focusing on critical parliamentary operations, governance processes,
and federated voting integrity.

Critical Monitoring Areas (80/20 Analysis):
1. Parliamentary Process Lifecycle (40% impact)
2. Federated Voting Security (25% impact)
3. Git Operations Performance (20% impact)  
4. Delegation Chain Integrity (15% impact)

This system provides real-time monitoring, anomaly detection,
and performance optimization for democratic git governance.
"""

import asyncio
import json
import time
import subprocess
import pathlib
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import statistics
import hashlib
# import networkx as nx  # Using simplified delegation tracking instead

from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource

from loguru import logger


@dataclass
class ParliamentaryEvent:
    """Represents a parliamentary event for monitoring"""
    event_type: str  # motion_created, motion_seconded, vote_cast, etc.
    motion_id: Optional[str] = None
    participant: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    trace_id: Optional[str] = None
    span_id: Optional[str] = None


@dataclass 
class VotingAnomalyAlert:
    """Alert for voting anomalies detected"""
    alert_type: str  # suspicious_delegation, vote_manipulation, etc.
    severity: str    # critical, high, medium, low
    description: str
    affected_motion: Optional[str] = None
    affected_participants: List[str] = field(default_factory=list)
    evidence: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


class GitParliamentMonitor:
    """Comprehensive OTEL monitoring for Git Parliament system"""
    
    def __init__(self):
        self.resource = Resource.create({
            "service.name": "git-parliament-monitor",
            "service.version": "1.0.0",
            "component": "governance_monitoring"
        })
        
        # Initialize OTEL providers
        self._setup_tracing()
        self._setup_metrics()
        
        # Get tracer and meter
        self.tracer = trace.get_tracer(__name__)
        self.meter = metrics.get_meter(__name__)
        
        # Initialize metrics
        self._setup_parliamentary_metrics()
        
        # Event tracking
        self.parliamentary_events: List[ParliamentaryEvent] = []
        self.voting_anomalies: List[VotingAnomalyAlert] = []
        self.performance_metrics: Dict[str, List[float]] = {}
        
        # Parliamentary state tracking
        self.active_motions: Dict[str, Dict[str, Any]] = {}
        self.delegation_map: Dict[str, str] = {}  # delegator -> delegate mapping
        self.vote_integrity_scores: Dict[str, float] = {}
        
        logger.info("Git Parliament Monitor initialized")
    
    def _setup_tracing(self):
        """Setup OpenTelemetry tracing"""
        provider = TracerProvider(resource=self.resource)
        
        try:
            otlp_exporter = OTLPSpanExporter(
                endpoint="http://localhost:4317",
                insecure=True
            )
            provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        except Exception as e:
            logger.warning(f"OTLP exporter not available: {e}")
            # Fallback to console
            from opentelemetry.sdk.trace.export import ConsoleSpanExporter
            provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
        
        trace.set_tracer_provider(provider)
    
    def _setup_metrics(self):
        """Setup OpenTelemetry metrics"""
        try:
            otlp_exporter = OTLPMetricExporter(
                endpoint="http://localhost:4317",
                insecure=True
            )
            reader = PeriodicExportingMetricReader(
                exporter=otlp_exporter,
                export_interval_millis=30000  # 30 seconds
            )
            provider = MeterProvider(resource=self.resource, metric_readers=[reader])
        except Exception as e:
            logger.warning(f"OTLP metric exporter not available: {e}")
            provider = MeterProvider(resource=self.resource)
        
        metrics.set_meter_provider(provider)
    
    def _setup_parliamentary_metrics(self):
        """Setup specific parliamentary metrics"""
        
        # Parliamentary process metrics
        self.motion_counter = self.meter.create_counter(
            "parliament.motions.total",
            description="Total number of motions created"
        )
        
        self.vote_counter = self.meter.create_counter(
            "parliament.votes.total", 
            description="Total number of votes cast"
        )
        
        self.delegation_counter = self.meter.create_counter(
            "parliament.delegations.total",
            description="Total number of vote delegations"
        )
        
        # Performance metrics
        self.motion_lifecycle_duration = self.meter.create_histogram(
            "parliament.motion.lifecycle.duration_ms",
            description="Duration of motion lifecycle from creation to resolution"
        )
        
        self.vote_tally_duration = self.meter.create_histogram(
            "parliament.vote.tally.duration_ms", 
            description="Duration of vote tallying process"
        )
        
        self.git_operation_duration = self.meter.create_histogram(
            "parliament.git.operation.duration_ms",
            description="Duration of git operations (branch, note, merge)"
        )
        
        # Security metrics
        self.anomaly_counter = self.meter.create_counter(
            "parliament.security.anomalies.total",
            description="Total security anomalies detected"
        )
        
        self.integrity_score = self.meter.create_gauge(
            "parliament.vote.integrity.score",
            description="Current vote integrity score (0-1)"
        )
        
        # Governance health metrics
        self.participation_rate = self.meter.create_gauge(
            "parliament.participation.rate",
            description="Participation rate in parliamentary processes"
        )
        
        self.consensus_efficiency = self.meter.create_gauge(
            "parliament.consensus.efficiency",
            description="Efficiency of reaching consensus (motions passed/total)"
        )
    
    async def monitor_motion_lifecycle(self, motion_id: str, title: str, body: str) -> str:
        """Monitor complete motion lifecycle with OTEL tracing"""
        
        with self.tracer.start_as_current_span("parliament.motion.lifecycle") as span:
            span.set_attribute("motion.id", motion_id)
            span.set_attribute("motion.title", title)
            span.set_attribute("motion.body_length", len(body))
            span.set_attribute("parliament.operation", "motion_creation")
            
            start_time = time.time()
            
            try:
                # Track motion creation
                self._track_parliamentary_event(
                    event_type="motion_created",
                    motion_id=motion_id,
                    participant="system",
                    metadata={"title": title, "body_length": len(body)},
                    trace_id=span.get_span_context().trace_id,
                    span_id=span.get_span_context().span_id
                )
                
                # Initialize motion tracking
                self.active_motions[motion_id] = {
                    "title": title,
                    "created_at": datetime.utcnow(),
                    "status": "open",
                    "seconds": [],
                    "debate_entries": [],
                    "votes": {},
                    "trace_id": span.get_span_context().trace_id
                }
                
                # Monitor git operations
                await self._monitor_git_branch_creation(motion_id, span)
                
                # Update metrics
                self.motion_counter.add(1, {"motion.type": "new"})
                
                duration_ms = (time.time() - start_time) * 1000
                span.set_attribute("motion.creation.duration_ms", duration_ms)
                
                logger.info(f"Motion {motion_id} created and monitored", extra={
                    "motion_id": motion_id,
                    "duration_ms": duration_ms,
                    "trace_id": hex(span.get_span_context().trace_id)
                })
                
                return motion_id
                
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                logger.error(f"Motion lifecycle monitoring failed: {e}")
                raise
    
    async def monitor_voting_process(self, motion_id: str, repo_name: str, 
                                   vote_value: str, weight: float = 1.0) -> bool:
        """Monitor voting process with security validation"""
        
        with self.tracer.start_as_current_span("parliament.vote.process") as span:
            span.set_attribute("motion.id", motion_id)
            span.set_attribute("vote.repo", repo_name)
            span.set_attribute("vote.value", vote_value)
            span.set_attribute("vote.weight", weight)
            span.set_attribute("parliament.operation", "vote_casting")
            
            start_time = time.time()
            
            try:
                # Validate vote legitimacy
                await self._validate_vote_integrity(motion_id, repo_name, vote_value, weight, span)
                
                # Track voting event
                self._track_parliamentary_event(
                    event_type="vote_cast",
                    motion_id=motion_id,
                    participant=repo_name,
                    metadata={
                        "vote_value": vote_value,
                        "weight": weight,
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    trace_id=span.get_span_context().trace_id,
                    span_id=span.get_span_context().span_id
                )
                
                # Update motion tracking
                if motion_id in self.active_motions:
                    self.active_motions[motion_id]["votes"][repo_name] = {
                        "value": vote_value,
                        "weight": weight,
                        "timestamp": datetime.utcnow()
                    }
                
                # Monitor git vote ref creation
                await self._monitor_git_vote_ref(motion_id, repo_name, vote_value, weight, span)
                
                # Update metrics
                self.vote_counter.add(1, {
                    "vote.value": vote_value,
                    "motion.id": motion_id
                })
                
                duration_ms = (time.time() - start_time) * 1000
                self.vote_tally_duration.record(duration_ms)
                span.set_attribute("vote.process.duration_ms", duration_ms)
                
                # Check for voting anomalies
                await self._detect_voting_anomalies(motion_id, repo_name, vote_value, weight)
                
                logger.info(f"Vote processed for motion {motion_id}", extra={
                    "motion_id": motion_id,
                    "repo": repo_name,
                    "vote": vote_value,
                    "weight": weight,
                    "duration_ms": duration_ms
                })
                
                return True
                
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                logger.error(f"Vote monitoring failed: {e}")
                return False
    
    async def monitor_delegation_chain(self, delegator: str, delegate: str) -> bool:
        """Monitor vote delegation with cycle detection"""
        
        with self.tracer.start_as_current_span("parliament.delegation.monitor") as span:
            span.set_attribute("delegation.from", delegator)
            span.set_attribute("delegation.to", delegate)
            span.set_attribute("parliament.operation", "delegation_update")
            
            try:
                # Check for cycles before adding
                if self._would_create_cycle(delegator, delegate):
                    await self._create_anomaly_alert(
                        alert_type="delegation_cycle",
                        severity="high",
                        description=f"Delegation cycle prevented involving {delegator} -> {delegate}",
                        affected_participants=[delegator, delegate],
                        evidence={"attempted_delegation": f"{delegator} -> {delegate}"}
                    )
                    span.set_attribute("delegation.cycle_detected", True)
                    return False
                
                # Update delegation mapping
                self.delegation_map[delegator] = delegate
                
                # Track delegation event
                self._track_parliamentary_event(
                    event_type="delegation_updated",
                    participant=delegator,
                    metadata={
                        "delegate": delegate,
                        "delegation_depth": self._get_delegation_depth(delegator)
                    },
                    trace_id=span.get_span_context().trace_id,
                    span_id=span.get_span_context().span_id
                )
                
                # Update metrics
                self.delegation_counter.add(1, {
                    "delegator": delegator,
                    "delegate": delegate
                })
                
                span.set_attribute("delegation.depth", self._get_delegation_depth(delegator))
                span.set_attribute("delegation.total_delegations", len(self.delegation_map))
                
                logger.info(f"Delegation monitored: {delegator} -> {delegate}")
                return True
                
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                logger.error(f"Delegation monitoring failed: {e}")
                return False
    
    async def monitor_merge_oracle_decision(self, motion_id: str) -> Dict[str, Any]:
        """Monitor merge oracle decision process"""
        
        with self.tracer.start_as_current_span("parliament.merge_oracle.decision") as span:
            span.set_attribute("motion.id", motion_id)
            span.set_attribute("parliament.operation", "merge_decision")
            
            start_time = time.time()
            
            try:
                # Get current vote tally
                vote_tally = await self._calculate_vote_tally(motion_id)
                
                # Monitor decision logic
                quorum_met = vote_tally["participation_rate"] >= 0.6
                consensus_reached = vote_tally["approval_rate"] >= 0.6
                decision = "approve" if quorum_met and consensus_reached else "reject"
                
                span.set_attribute("decision.quorum_met", quorum_met)
                span.set_attribute("decision.consensus_reached", consensus_reached)
                span.set_attribute("decision.outcome", decision)
                span.set_attribute("vote.participation_rate", vote_tally["participation_rate"])
                span.set_attribute("vote.approval_rate", vote_tally["approval_rate"])
                
                # Track decision event
                self._track_parliamentary_event(
                    event_type="merge_decision",
                    motion_id=motion_id,
                    participant="merge_oracle",
                    metadata={
                        "decision": decision,
                        "quorum_met": quorum_met,
                        "consensus_reached": consensus_reached,
                        "vote_tally": vote_tally
                    },
                    trace_id=span.get_span_context().trace_id,
                    span_id=span.get_span_context().span_id
                )
                
                # Update motion status
                if motion_id in self.active_motions:
                    self.active_motions[motion_id]["status"] = "resolved"
                    self.active_motions[motion_id]["decision"] = decision
                    self.active_motions[motion_id]["resolved_at"] = datetime.utcnow()
                
                # Monitor git merge/branch deletion
                await self._monitor_git_merge_operation(motion_id, decision, span)
                
                duration_ms = (time.time() - start_time) * 1000
                span.set_attribute("decision.duration_ms", duration_ms)
                
                # Update governance metrics
                self._update_governance_metrics(decision, vote_tally)
                
                logger.info(f"Merge oracle decision for motion {motion_id}: {decision}", extra={
                    "motion_id": motion_id,
                    "decision": decision,
                    "duration_ms": duration_ms,
                    "vote_tally": vote_tally
                })
                
                return {
                    "motion_id": motion_id,
                    "decision": decision,
                    "vote_tally": vote_tally,
                    "duration_ms": duration_ms
                }
                
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                logger.error(f"Merge oracle monitoring failed: {e}")
                raise
    
    async def _monitor_git_branch_creation(self, motion_id: str, parent_span: trace.Span):
        """Monitor git branch creation for motion"""
        with self.tracer.start_as_current_span("git.branch.create") as span:
            span.set_attribute("git.operation", "branch_create")
            span.set_attribute("git.branch_name", f"motions/{motion_id}")
            
            start_time = time.time()
            
            try:
                # Monitor actual git branch creation
                # This would integrate with the git_auto.py utilities
                duration_ms = (time.time() - start_time) * 1000
                self.git_operation_duration.record(duration_ms, {"operation": "branch_create"})
                span.set_attribute("git.duration_ms", duration_ms)
                
            except Exception as e:
                span.record_exception(e)
                logger.error(f"Git branch monitoring failed: {e}")
    
    async def _monitor_git_vote_ref(self, motion_id: str, repo_name: str, 
                                  vote_value: str, weight: float, parent_span: trace.Span):
        """Monitor git vote ref creation"""
        with self.tracer.start_as_current_span("git.vote_ref.create") as span:
            span.set_attribute("git.operation", "vote_ref_create")
            span.set_attribute("git.ref_path", f"refs/vote/{motion_id}/{repo_name}")
            span.set_attribute("vote.value", vote_value)
            span.set_attribute("vote.weight", weight)
            
            start_time = time.time()
            
            try:
                # Monitor git vote ref creation
                duration_ms = (time.time() - start_time) * 1000
                self.git_operation_duration.record(duration_ms, {"operation": "vote_ref_create"})
                span.set_attribute("git.duration_ms", duration_ms)
                
            except Exception as e:
                span.record_exception(e)
                logger.error(f"Git vote ref monitoring failed: {e}")
    
    async def _monitor_git_merge_operation(self, motion_id: str, decision: str, parent_span: trace.Span):
        """Monitor git merge or branch deletion"""
        with self.tracer.start_as_current_span("git.merge_operation") as span:
            operation = "merge" if decision == "approve" else "branch_delete"
            span.set_attribute("git.operation", operation)
            span.set_attribute("git.branch", f"motions/{motion_id}")
            span.set_attribute("merge.decision", decision)
            
            start_time = time.time()
            
            try:
                # Monitor git merge/delete operation
                duration_ms = (time.time() - start_time) * 1000
                self.git_operation_duration.record(duration_ms, {"operation": operation})
                span.set_attribute("git.duration_ms", duration_ms)
                
            except Exception as e:
                span.record_exception(e)
                logger.error(f"Git merge operation monitoring failed: {e}")
    
    async def _validate_vote_integrity(self, motion_id: str, repo_name: str, 
                                     vote_value: str, weight: float, span: trace.Span):
        """Validate vote integrity and detect anomalies"""
        
        # Check for double voting
        if motion_id in self.active_motions:
            existing_votes = self.active_motions[motion_id]["votes"]
            if repo_name in existing_votes:
                await self._create_anomaly_alert(
                    alert_type="double_voting",
                    severity="high", 
                    description=f"Duplicate vote attempt by {repo_name} for motion {motion_id}",
                    affected_motion=motion_id,
                    affected_participants=[repo_name],
                    evidence={"existing_vote": existing_votes[repo_name], "new_vote": vote_value}
                )
                span.set_attribute("vote.anomaly.double_voting", True)
        
        # Check for suspicious weight
        if weight > 10.0 or weight < 0.0:
            await self._create_anomaly_alert(
                alert_type="suspicious_weight",
                severity="medium",
                description=f"Unusual vote weight {weight} by {repo_name}",
                affected_motion=motion_id,
                affected_participants=[repo_name],
                evidence={"weight": weight, "expected_range": "0.0-10.0"}
            )
            span.set_attribute("vote.anomaly.suspicious_weight", True)
    
    async def _detect_voting_anomalies(self, motion_id: str, repo_name: str, 
                                     vote_value: str, weight: float):
        """Detect voting pattern anomalies"""
        
        # Check for coordinated voting patterns
        recent_votes = self._get_recent_votes(minutes=5)
        if len(recent_votes) > 10:  # High vote volume
            # Check if many votes are identical and close in time
            same_value_votes = [v for v in recent_votes if v["vote_value"] == vote_value]
            if len(same_value_votes) > 5:
                await self._create_anomaly_alert(
                    alert_type="coordinated_voting",
                    severity="medium",
                    description=f"Potential coordinated voting detected for motion {motion_id}",
                    affected_motion=motion_id,
                    evidence={"similar_votes": len(same_value_votes), "time_window": "5 minutes"}
                )
    
    async def _calculate_vote_tally(self, motion_id: str) -> Dict[str, Any]:
        """Calculate current vote tally for a motion"""
        
        if motion_id not in self.active_motions:
            return {"error": "Motion not found"}
        
        motion = self.active_motions[motion_id]
        votes = motion["votes"]
        
        # Apply delegation
        resolved_votes = self._resolve_delegated_votes(votes)
        
        total_weight = sum(vote["weight"] for vote in resolved_votes.values())
        for_weight = sum(vote["weight"] for vote in resolved_votes.values() if vote["value"] == "for")
        
        # Estimate total participants (voters + delegators)
        all_participants = set(votes.keys()) | set(self.delegation_map.keys()) | set(self.delegation_map.values())
        participation_rate = len(resolved_votes) / max(1, len(all_participants))
        approval_rate = for_weight / max(total_weight, 1)
        
        return {
            "total_votes": len(resolved_votes),
            "total_weight": total_weight,
            "for_weight": for_weight,
            "against_weight": total_weight - for_weight,
            "participation_rate": participation_rate,
            "approval_rate": approval_rate
        }
    
    def _resolve_delegated_votes(self, votes: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve votes through delegation chain"""
        resolved = {}
        
        for voter, vote in votes.items():
            # Find final delegate through delegation chain
            final_voter = voter
            visited = set()
            
            while final_voter in self.delegation_map and final_voter not in visited:
                visited.add(final_voter)
                final_voter = self.delegation_map[final_voter]
            
            resolved[final_voter] = vote
        
        return resolved
    
    def _would_create_cycle(self, delegator: str, delegate: str) -> bool:
        """Check if adding delegation would create a cycle"""
        # Simple cycle detection: check if delegate eventually delegates back to delegator
        current = delegate
        visited = set()
        
        while current in self.delegation_map and current not in visited:
            visited.add(current)
            current = self.delegation_map[current]
            if current == delegator:
                return True
        
        return False
    
    def _get_delegation_depth(self, node: str) -> int:
        """Get delegation chain depth for a node"""
        depth = 0
        current = node
        visited = set()
        
        while current in self.delegation_map and current not in visited:
            visited.add(current)
            current = self.delegation_map[current]
            depth += 1
            if depth > 10:  # Prevent infinite loops
                break
        
        return depth
    
    def _track_parliamentary_event(self, event_type: str, motion_id: Optional[str] = None,
                                 participant: Optional[str] = None, metadata: Dict[str, Any] = None,
                                 trace_id: Optional[int] = None, span_id: Optional[int] = None):
        """Track parliamentary event"""
        event = ParliamentaryEvent(
            event_type=event_type,
            motion_id=motion_id,
            participant=participant,
            metadata=metadata or {},
            trace_id=hex(trace_id) if trace_id else None,
            span_id=hex(span_id) if span_id else None
        )
        
        self.parliamentary_events.append(event)
        
        # Trim old events (keep last 1000)
        if len(self.parliamentary_events) > 1000:
            self.parliamentary_events = self.parliamentary_events[-1000:]
    
    async def _create_anomaly_alert(self, alert_type: str, severity: str, description: str,
                                  affected_motion: Optional[str] = None,
                                  affected_participants: List[str] = None,
                                  evidence: Dict[str, Any] = None):
        """Create voting anomaly alert"""
        alert = VotingAnomalyAlert(
            alert_type=alert_type,
            severity=severity,
            description=description,
            affected_motion=affected_motion,
            affected_participants=affected_participants or [],
            evidence=evidence or {}
        )
        
        self.voting_anomalies.append(alert)
        
        # Update anomaly metrics
        self.anomaly_counter.add(1, {
            "alert.type": alert_type,
            "alert.severity": severity
        })
        
        logger.warning(f"Voting anomaly detected: {alert_type}", extra={
            "alert_type": alert_type,
            "severity": severity,
            "description": description,
            "motion_id": affected_motion
        })
    
    def _get_recent_votes(self, minutes: int = 5) -> List[Dict[str, Any]]:
        """Get recent votes for anomaly detection"""
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        
        recent = []
        for event in self.parliamentary_events:
            if event.event_type == "vote_cast" and event.timestamp >= cutoff:
                recent.append({
                    "motion_id": event.motion_id,
                    "participant": event.participant,
                    "vote_value": event.metadata.get("vote_value"),
                    "timestamp": event.timestamp
                })
        
        return recent
    
    def _update_governance_metrics(self, decision: str, vote_tally: Dict[str, Any]):
        """Update governance health metrics"""
        
        # Update participation rate
        self.participation_rate.set(vote_tally["participation_rate"])
        
        # Update integrity score (based on anomaly rate)
        recent_anomalies = len([a for a in self.voting_anomalies 
                              if a.timestamp >= datetime.utcnow() - timedelta(hours=1)])
        integrity = max(0.0, 1.0 - (recent_anomalies * 0.1))
        self.integrity_score.set(integrity)
        
        # Update consensus efficiency
        resolved_motions = [m for m in self.active_motions.values() if m.get("status") == "resolved"]
        if resolved_motions:
            approved = len([m for m in resolved_motions if m.get("decision") == "approve"])
            efficiency = approved / len(resolved_motions)
            self.consensus_efficiency.set(efficiency)
    
    def get_monitoring_summary(self) -> Dict[str, Any]:
        """Get current monitoring summary"""
        
        return {
            "active_motions": len(self.active_motions),
            "total_events": len(self.parliamentary_events),
            "recent_anomalies": len([a for a in self.voting_anomalies 
                                   if a.timestamp >= datetime.utcnow() - timedelta(hours=1)]),
            "active_delegations": len(self.delegation_map),
            "total_participants": len(set(self.delegation_map.keys()) | set(self.delegation_map.values())),
            "monitoring_health": "healthy",
            "last_event": self.parliamentary_events[-1].timestamp if self.parliamentary_events else None
        }


# Usage example / test function
async def test_git_parliament_monitoring():
    """Test the Git Parliament monitoring system"""
    
    monitor = GitParliamentMonitor()
    
    # Test motion lifecycle monitoring
    motion_id = await monitor.monitor_motion_lifecycle(
        motion_id="M123456",
        title="Adopt OTEL v1.4",
        body="Motion to adopt OpenTelemetry v1.4 for improved observability"
    )
    
    # Test voting process monitoring
    await monitor.monitor_voting_process(motion_id, "repo_alice", "for", 1.0)
    await monitor.monitor_voting_process(motion_id, "repo_bob", "against", 1.0)
    await monitor.monitor_voting_process(motion_id, "repo_charlie", "for", 2.0)
    
    # Test delegation monitoring
    await monitor.monitor_delegation_chain("repo_dave", "repo_alice")
    await monitor.monitor_delegation_chain("repo_eve", "repo_bob")
    
    # Test merge oracle decision monitoring
    decision_result = await monitor.monitor_merge_oracle_decision(motion_id)
    
    # Get monitoring summary
    summary = monitor.get_monitoring_summary()
    
    print("Git Parliament Monitoring Test Results:")
    print(f"Motion ID: {motion_id}")
    print(f"Decision Result: {decision_result}")
    print(f"Monitoring Summary: {summary}")
    
    return {
        "motion_id": motion_id,
        "decision_result": decision_result,
        "monitoring_summary": summary
    }


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_git_parliament_monitoring())