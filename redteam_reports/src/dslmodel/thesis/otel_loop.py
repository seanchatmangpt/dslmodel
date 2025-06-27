"""
thesis_otel_loop.py
───────────────────────────────────────────────────────────────────────────────
Full OTEL Ecosystem Loop for SwarmSH Thesis
• Semantic conventions → WeaverForge → Runtime spans → Analysis → Feedback
• Demonstrates the complete auto-TRIZ loop with real telemetry
• Shows how contradictions in traces update semantic conventions
"""

from __future__ import annotations
import json
import time
import random
from enum import Enum
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timezone
from pathlib import Path
from pydantic import BaseModel, Field

# Simulated OTEL imports (would be real in production)
from dataclasses import dataclass
from collections import defaultdict

# Import thesis components
from .thesis_complete import (
    ThesisComplete, SpanSpec, InversionPair, 
    TRIZMap, FeedbackLoopStep, FeedbackLoopPhase
)


# ─────────────────────────────────────────────────────────────────────────────
# 1. OTEL Trace Simulation (would use real OTEL SDK in production)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class SpanContext:
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None

@dataclass
class SpanData:
    name: str
    context: SpanContext
    start_time: float
    end_time: float
    attributes: Dict[str, Any]
    status: str = "OK"
    events: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.events is None:
            self.events = []

    @property
    def duration_ms(self) -> float:
        return (self.end_time - self.start_time) * 1000


class TraceCollector:
    """Simulated trace collector that stores spans for analysis"""
    
    def __init__(self):
        self.spans: List[SpanData] = []
        self.traces: Dict[str, List[SpanData]] = defaultdict(list)
    
    def add_span(self, span: SpanData):
        self.spans.append(span)
        self.traces[span.context.trace_id].append(span)
    
    def get_trace(self, trace_id: str) -> List[SpanData]:
        return self.traces.get(trace_id, [])
    
    def get_recent_spans(self, limit: int = 100) -> List[SpanData]:
        return sorted(self.spans, key=lambda s: s.start_time, reverse=True)[:limit]


# ─────────────────────────────────────────────────────────────────────────────
# 2. Semantic Convention Models
# ─────────────────────────────────────────────────────────────────────────────

class SemanticAttribute(BaseModel):
    id: str
    type: str
    brief: str
    requirement_level: str = "recommended"
    examples: List[Any] = Field(default_factory=list)
    
class SemanticGroup(BaseModel):
    id: str
    type: str
    prefix: str
    brief: str
    attributes: List[SemanticAttribute]
    
class SemanticConvention(BaseModel):
    groups: List[SemanticGroup]
    version: str = "1.0.0"
    
    def to_weaver_yaml(self) -> str:
        """Generate WeaverForge-compatible YAML"""
        lines = [f"# Generated at {datetime.now(timezone.utc).isoformat()}"]
        lines.append(f"version: {self.version}")
        lines.append("groups:")
        
        for group in self.groups:
            lines.append(f"  - id: {group.id}")
            lines.append(f"    type: {group.type}")
            lines.append(f"    prefix: {group.prefix}")
            lines.append(f"    brief: '{group.brief}'")
            lines.append("    attributes:")
            
            for attr in group.attributes:
                lines.append(f"      - id: {attr.id}")
                lines.append(f"        type: {attr.type}")
                lines.append(f"        brief: '{attr.brief}'")
                lines.append(f"        requirement_level: {attr.requirement_level}")
                if attr.examples:
                    lines.append(f"        examples: {attr.examples}")
        
        return '\n'.join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Contradiction Detection Engine
# ─────────────────────────────────────────────────────────────────────────────

class ContradictionType(str, Enum):
    PERFORMANCE = "performance"
    RETRY_STORM = "retry_storm"
    MISSING_SPAN = "missing_span"
    ORDERING = "ordering"
    RESOURCE = "resource"
    SEMANTIC = "semantic"

class Contradiction(BaseModel):
    type: ContradictionType
    severity: float = Field(..., ge=0.0, le=1.0)
    description: str
    affected_spans: List[str]
    suggested_resolution: str
    trace_evidence: List[str] = Field(default_factory=list)

class ContradictionDetector:
    """Analyzes traces to find contradictions per TRIZ principles"""
    
    def __init__(self, collector: TraceCollector):
        self.collector = collector
        self.thresholds = {
            "slow_span_ms": 1000,
            "retry_threshold": 3,
            "error_rate": 0.1
        }
    
    def detect_contradictions(self) -> List[Contradiction]:
        """Detect contradictions in recent traces"""
        contradictions = []
        
        # Check for performance contradictions
        slow_spans = [s for s in self.collector.get_recent_spans() 
                      if s.duration_ms > self.thresholds["slow_span_ms"]]
        if slow_spans:
            contradictions.append(Contradiction(
                type=ContradictionType.PERFORMANCE,
                severity=min(1.0, len(slow_spans) / 10),
                description=f"Found {len(slow_spans)} slow spans exceeding {self.thresholds['slow_span_ms']}ms",
                affected_spans=[s.name for s in slow_spans[:5]],
                suggested_resolution="Add span.sampling_priority attribute to reduce overhead",
                trace_evidence=[s.context.trace_id for s in slow_spans[:3]]
            ))
        
        # Check for retry storms
        retry_spans = defaultdict(int)
        for span in self.collector.get_recent_spans():
            if "retry_count" in span.attributes:
                retry_count = span.attributes["retry_count"]
                if retry_count >= self.thresholds["retry_threshold"]:
                    retry_spans[span.name] += 1
        
        for span_name, count in retry_spans.items():
            if count > 5:
                contradictions.append(Contradiction(
                    type=ContradictionType.RETRY_STORM,
                    severity=min(1.0, count / 20),
                    description=f"Retry storm detected for {span_name}",
                    affected_spans=[span_name],
                    suggested_resolution="Add circuit breaker span attributes",
                    trace_evidence=[]
                ))
        
        # Check for missing expected spans
        expected_patterns = [
            ("swarmsh.init", "swarmsh.ready"),
            ("swarmsh.request", "swarmsh.response"),
            ("swarmsh.thesis.telemetry_as_system", "swarmsh.thesis.span_drives_code")
        ]
        
        span_names = {s.name for s in self.collector.get_recent_spans()}
        for start, end in expected_patterns:
            if start in span_names and end not in span_names:
                contradictions.append(Contradiction(
                    type=ContradictionType.MISSING_SPAN,
                    severity=0.7,
                    description=f"Expected span '{end}' missing after '{start}'",
                    affected_spans=[start],
                    suggested_resolution=f"Add semantic convention for '{end}' span",
                    trace_evidence=[]
                ))
        
        return contradictions


# ─────────────────────────────────────────────────────────────────────────────
# 4. LLM Resolution Engine (simulated)
# ─────────────────────────────────────────────────────────────────────────────

class ResolutionProposal(BaseModel):
    contradiction: Contradiction
    new_attributes: List[SemanticAttribute]
    modified_attributes: List[Tuple[str, SemanticAttribute]]
    rationale: str
    triz_principle: Optional[int] = None
    triz_name: Optional[str] = None

class LLMResolver:
    """Simulated LLM that proposes semantic convention updates"""
    
    def __init__(self):
        self.triz_mappings = {
            ContradictionType.PERFORMANCE: (35, "Parameter Change"),
            ContradictionType.RETRY_STORM: (25, "Self-Service"), 
            ContradictionType.MISSING_SPAN: (10, "Preliminary Action"),
            ContradictionType.ORDERING: (13, "The Other Way Around"),
            ContradictionType.RESOURCE: (2, "Taking Out"),
            ContradictionType.SEMANTIC: (1, "Segmentation")
        }
    
    def propose_resolution(self, contradiction: Contradiction, 
                          current_convention: SemanticConvention) -> ResolutionProposal:
        """Propose semantic convention changes to resolve contradiction"""
        
        triz_num, triz_name = self.triz_mappings.get(
            contradiction.type, (40, "Composite Materials")
        )
        
        new_attributes = []
        modified_attributes = []
        
        if contradiction.type == ContradictionType.PERFORMANCE:
            new_attributes.append(SemanticAttribute(
                id="sampling_priority",
                type="int",
                brief="Sampling priority (0-100) for performance-sensitive spans",
                requirement_level="conditionally_required",
                examples=[0, 50, 100]
            ))
            new_attributes.append(SemanticAttribute(
                id="performance_budget_ms",
                type="int",
                brief="Expected performance budget in milliseconds",
                requirement_level="recommended",
                examples=[100, 500, 1000]
            ))
            
        elif contradiction.type == ContradictionType.RETRY_STORM:
            new_attributes.append(SemanticAttribute(
                id="circuit_breaker.state",
                type="string",
                brief="Circuit breaker state",
                requirement_level="recommended",
                examples=["open", "closed", "half_open"]
            ))
            new_attributes.append(SemanticAttribute(
                id="circuit_breaker.failure_threshold",
                type="int",
                brief="Number of failures before opening circuit",
                requirement_level="recommended",
                examples=[5, 10]
            ))
            
        elif contradiction.type == ContradictionType.MISSING_SPAN:
            # Extract the missing span name
            missing_span = contradiction.description.split("'")[3]
            span_id = missing_span.split('.')[-1]
            
            new_attributes.append(SemanticAttribute(
                id=span_id,
                type="boolean",
                brief=f"Indicates {missing_span} was executed",
                requirement_level="required"
            ))
        
        rationale = (
            f"Applying TRIZ Principle {triz_num} ({triz_name}) to resolve {contradiction.type}. "
            f"The proposed attributes will {'reduce' if contradiction.type == ContradictionType.PERFORMANCE else 'prevent'} "
            f"the issue by providing better observability and control mechanisms."
        )
        
        return ResolutionProposal(
            contradiction=contradiction,
            new_attributes=new_attributes,
            modified_attributes=modified_attributes,
            rationale=rationale,
            triz_principle=triz_num,
            triz_name=triz_name
        )


# ─────────────────────────────────────────────────────────────────────────────
# 5. Auto-TRIZ Feedback Loop Orchestrator
# ─────────────────────────────────────────────────────────────────────────────

class FeedbackLoopState(str, Enum):
    IDLE = "idle"
    COLLECTING = "collecting"
    ANALYZING = "analyzing"
    RESOLVING = "resolving"
    GENERATING = "generating"
    DEPLOYING = "deploying"
    VALIDATING = "validating"

class OTELFeedbackLoop(BaseModel):
    state: FeedbackLoopState = Field(default=FeedbackLoopState.IDLE)
    iteration: int = Field(default=0)
    collector: Optional[TraceCollector] = Field(default=None, exclude=True)
    detector: Optional[ContradictionDetector] = Field(default=None, exclude=True)
    resolver: Optional[LLMResolver] = Field(default=None, exclude=True)
    current_convention: SemanticConvention
    contradiction_history: List[Contradiction] = Field(default_factory=list)
    resolution_history: List[ResolutionProposal] = Field(default_factory=list)
    
    class Config:
        arbitrary_types_allowed = True
    
    def initialize(self):
        """Initialize the feedback loop components"""
        self.collector = TraceCollector()
        self.detector = ContradictionDetector(self.collector)
        self.resolver = LLMResolver()
        self.state = FeedbackLoopState.COLLECTING
    
    def run_iteration(self):
        """Run one complete feedback loop iteration"""
        print(f"\n{'='*60}")
        print(f"Feedback Loop Iteration {self.iteration + 1}")
        print(f"{'='*60}\n")
        
        # Phase 1: PERCEPTION - Collect telemetry
        self.state = FeedbackLoopState.COLLECTING
        print("📡 PERCEPTION: Collecting telemetry...")
        self._simulate_runtime_spans()
        
        # Phase 2: ANALYZING - Detect contradictions
        self.state = FeedbackLoopState.ANALYZING
        print("\n🔍 ANALYZING: Detecting contradictions...")
        contradictions = self.detector.detect_contradictions()
        
        if not contradictions:
            print("✅ No contradictions detected")
            self.state = FeedbackLoopState.IDLE
            return
        
        print(f"⚠️  Found {len(contradictions)} contradictions:")
        for c in contradictions:
            print(f"   - {c.type.value}: {c.description} (severity: {c.severity:.2f})")
            self.contradiction_history.append(c)
        
        # Phase 3: RESOLUTION - LLM proposes fixes
        self.state = FeedbackLoopState.RESOLVING
        print("\n🤖 RESOLUTION: LLM analyzing contradictions...")
        
        for contradiction in contradictions[:3]:  # Process top 3
            proposal = self.resolver.propose_resolution(contradiction, self.current_convention)
            self.resolution_history.append(proposal)
            
            print(f"\n   Proposed fix using TRIZ #{proposal.triz_principle} ({proposal.triz_name}):")
            print(f"   {proposal.rationale}")
            
            if proposal.new_attributes:
                print(f"   New attributes to add:")
                for attr in proposal.new_attributes:
                    print(f"     - {attr.id}: {attr.brief}")
        
        # Phase 4: GENERATION - Update semantic conventions
        self.state = FeedbackLoopState.GENERATING
        print("\n⚙️  GENERATION: Updating semantic conventions...")
        self._apply_resolutions(contradictions[:3])
        
        # Phase 5: DEPLOYMENT - Simulate WeaverForge generation
        self.state = FeedbackLoopState.DEPLOYING
        print("\n🚀 DEPLOYMENT: Generating new code via WeaverForge...")
        yaml_content = self.current_convention.to_weaver_yaml()
        print(f"   Generated {len(yaml_content.splitlines())} lines of YAML")
        print("   Would trigger: weaver forge generate --output ./generated")
        
        # Phase 6: VALIDATION - Check if contradictions resolved
        self.state = FeedbackLoopState.VALIDATING
        print("\n✓ VALIDATION: Checking resolution effectiveness...")
        # In real system, would wait for new traces with updated code
        print("   Simulating validation with new traces...")
        
        self.iteration += 1
        self.state = FeedbackLoopState.IDLE
        
        print(f"\n{'='*60}")
        print(f"Iteration {self.iteration} complete")
        print(f"{'='*60}")
    
    def _simulate_runtime_spans(self):
        """Simulate runtime span generation"""
        import uuid
        
        # Generate some normal spans
        trace_id = str(uuid.uuid4())
        base_time = time.time()
        
        spans = [
            SpanData(
                name="swarmsh.init",
                context=SpanContext(trace_id=trace_id, span_id=str(uuid.uuid4())),
                start_time=base_time,
                end_time=base_time + 0.1,
                attributes={"version": "1.0.0"}
            ),
            SpanData(
                name="swarmsh.thesis.telemetry_as_system",
                context=SpanContext(trace_id=trace_id, span_id=str(uuid.uuid4())),
                start_time=base_time + 0.1,
                end_time=base_time + 0.15,
                attributes={"validated": True}
            ),
            SpanData(
                name="swarmsh.ready",
                context=SpanContext(trace_id=trace_id, span_id=str(uuid.uuid4())),
                start_time=base_time + 0.15,
                end_time=base_time + 0.2,
                attributes={"components": ["telemetry", "llm", "forge"]}
            )
        ]
        
        # Add some problematic spans based on iteration
        if self.iteration % 2 == 0:
            # Slow span
            spans.append(SpanData(
                name="swarmsh.process.heavy_computation",
                context=SpanContext(trace_id=trace_id, span_id=str(uuid.uuid4())),
                start_time=base_time + 0.2,
                end_time=base_time + 2.5,  # 2.3 seconds!
                attributes={"data_size": 1000000}
            ))
        
        if self.iteration % 3 == 0:
            # Retry storm
            for i in range(7):
                spans.append(SpanData(
                    name="swarmsh.external.api_call",
                    context=SpanContext(trace_id=str(uuid.uuid4()), span_id=str(uuid.uuid4())),
                    start_time=base_time + 0.3 + i * 0.1,
                    end_time=base_time + 0.35 + i * 0.1,
                    attributes={"retry_count": 4, "endpoint": "/unstable"},
                    status="ERROR"
                ))
        
        # Add all spans to collector
        for span in spans:
            self.collector.add_span(span)
        
        print(f"   Generated {len(spans)} spans in trace {trace_id[:8]}...")
    
    def _apply_resolutions(self, contradictions: List[Contradiction]):
        """Apply proposed resolutions to semantic conventions"""
        # Get the thesis group
        thesis_group = next((g for g in self.current_convention.groups 
                            if g.id == "swarmsh.thesis"), None)
        
        if not thesis_group:
            return
        
        # Apply resolutions
        applied_count = 0
        for contradiction in contradictions:
            proposal = next((p for p in self.resolution_history 
                           if p.contradiction == contradiction), None)
            if proposal and proposal.new_attributes:
                # Add new attributes to the group
                for attr in proposal.new_attributes:
                    if not any(a.id == attr.id for a in thesis_group.attributes):
                        thesis_group.attributes.append(attr)
                        applied_count += 1
                        print(f"   + Added attribute: {attr.id}")
        
        print(f"   Applied {applied_count} semantic convention updates")


# ─────────────────────────────────────────────────────────────────────────────
# 6. Complete Loop Demo
# ─────────────────────────────────────────────────────────────────────────────

def create_initial_convention() -> SemanticConvention:
    """Create the initial thesis semantic convention"""
    return SemanticConvention(
        groups=[
            SemanticGroup(
                id="swarmsh.thesis",
                type="span",
                prefix="swarmsh.thesis",
                brief="SwarmSH thesis claims as telemetry",
                attributes=[
                    SemanticAttribute(
                        id="telemetry_as_system",
                        type="boolean",
                        brief="Telemetry is the system, not an add-on."
                    ),
                    SemanticAttribute(
                        id="span_drives_code",
                        type="boolean", 
                        brief="Spans generate code & CLI."
                    ),
                    SemanticAttribute(
                        id="trace_to_prompt_emergence",
                        type="boolean",
                        brief="Traces → LLM prompts (emergent)."
                    ),
                    SemanticAttribute(
                        id="telemetry_communication_channel",
                        type="boolean",
                        brief="Spans are the agent messaging bus."
                    ),
                    SemanticAttribute(
                        id="system_models_itself",
                        type="boolean",
                        brief="Trace graph is a live self-model."
                    )
                ]
            )
        ]
    )


def demo_otel_loop():
    """Demonstrate the complete OTEL ecosystem feedback loop"""
    print("🌊 SwarmSH OTEL Ecosystem Loop Demo")
    print("="*60)
    
    # Create initial setup
    initial_convention = create_initial_convention()
    loop = OTELFeedbackLoop(current_convention=initial_convention)
    loop.initialize()
    
    # Run multiple iterations
    for i in range(3):
        if i > 0:
            print("\n🔄 Waiting before next iteration...")
            time.sleep(1)  # Simulate time passing
        
        loop.run_iteration()
    
    # Summary
    print("\n" + "="*60)
    print("📊 FEEDBACK LOOP SUMMARY")
    print("="*60)
    print(f"Iterations completed: {loop.iteration}")
    print(f"Contradictions found: {len(loop.contradiction_history)}")
    print(f"Resolutions proposed: {len(loop.resolution_history)}")
    print(f"Semantic attributes: {len(loop.current_convention.groups[0].attributes)}")
    
    # Show growth
    initial_attrs = len(create_initial_convention().groups[0].attributes)
    final_attrs = len(loop.current_convention.groups[0].attributes)
    print(f"Attribute growth: {initial_attrs} → {final_attrs} (+{final_attrs - initial_attrs})")
    
    # Save final convention
    yaml_path = Path("thesis_semconv_evolved.yaml")
    yaml_path.write_text(loop.current_convention.to_weaver_yaml())
    print(f"\n💾 Final semantic convention saved to: {yaml_path}")


if __name__ == "__main__":
    demo_otel_loop()