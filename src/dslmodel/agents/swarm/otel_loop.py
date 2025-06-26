#!/usr/bin/env python3
"""
Full OpenTelemetry Ecosystem Loop for SwarmAgent Framework.

This module demonstrates the complete telemetry loop:
1. CLI commands generate OTEL spans
2. Spans are exported to multiple destinations (console, JSONL, OTLP)
3. SwarmAgents listen to span stream and react
4. Agent reactions generate new CLI commands
5. New commands generate new spans, continuing the loop
"""

import json
import time
import asyncio
import pathlib
import subprocess
from typing import Dict, Any, Optional, List
from contextlib import contextmanager
from datetime import datetime

# OpenTelemetry imports
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SpanExporter,
    SpanExportResult
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace import Status, StatusCode
from opentelemetry.instrumentation.utils import unwrap
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader
)

# Local imports
from dslmodel.agents.swarm import SwarmAgent, NextCommand, SpanData


class JSONLSpanExporter(SpanExporter):
    """
    Custom span exporter that writes to JSONL file for SwarmAgent consumption.
    
    This bridges the gap between OpenTelemetry SDK and the SwarmAgent framework.
    """
    
    def __init__(self, output_file: pathlib.Path):
        self.output_file = output_file
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        self.output_file.touch()
    
    def export(self, spans) -> SpanExportResult:
        """Export spans to JSONL file."""
        try:
            with self.output_file.open("a") as f:
                for span in spans:
                    # Convert OTEL span to SwarmAgent format
                    span_data = {
                        "name": span.name,
                        "trace_id": format(span.context.trace_id, "032x"),
                        "span_id": format(span.context.span_id, "016x"),
                        "parent_span_id": format(span.parent.span_id, "016x") if span.parent else None,
                        "timestamp": span.start_time / 1e9,  # Convert to seconds
                        "duration_ms": (span.end_time - span.start_time) / 1e6 if span.end_time else None,
                        "attributes": dict(span.attributes) if span.attributes else {},
                        "status": span.status.status_code.name if span.status else "UNSET",
                        "events": [
                            {
                                "name": event.name,
                                "timestamp": event.timestamp / 1e9,
                                "attributes": dict(event.attributes) if event.attributes else {}
                            }
                            for event in span.events
                        ] if span.events else []
                    }
                    f.write(json.dumps(span_data) + "\n")
            return SpanExportResult.SUCCESS
        except Exception as e:
            print(f"Failed to export spans: {e}")
            return SpanExportResult.FAILURE
    
    def shutdown(self):
        """Shutdown the exporter."""
        pass


class SwarmTelemetry:
    """
    Manages OpenTelemetry setup for the Swarm ecosystem.
    
    Provides tracers, meters, and span context management.
    """
    
    def __init__(self, 
                 service_name: str = "swarm-ecosystem",
                 span_file: pathlib.Path = None,
                 enable_console: bool = True,
                 enable_otlp: bool = False):
        """
        Initialize telemetry with multiple exporters.
        
        Args:
            service_name: Name of the service
            span_file: Path to JSONL file for SwarmAgent consumption
            enable_console: Enable console output for debugging
            enable_otlp: Enable OTLP export (requires collector)
        """
        self.service_name = service_name
        self.span_file = span_file or pathlib.Path("~/s2s/agent_coordination/telemetry_spans.jsonl").expanduser()
        
        # Create resource
        resource = Resource.create({
            ResourceAttributes.SERVICE_NAME: service_name,
            ResourceAttributes.SERVICE_VERSION: "1.0.0",
            "swarm.framework": "dslmodel",
            "swarm.ecosystem": "true"
        })
        
        # Setup tracing
        self.tracer_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(self.tracer_provider)
        
        # Add exporters
        if enable_console:
            self.tracer_provider.add_span_processor(
                BatchSpanProcessor(ConsoleSpanExporter())
            )
        
        # Always add JSONL exporter for SwarmAgent
        self.tracer_provider.add_span_processor(
            BatchSpanProcessor(JSONLSpanExporter(self.span_file))
        )
        
        if enable_otlp:
            try:
                from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
                otlp_exporter = OTLPSpanExporter(
                    endpoint="localhost:4317",
                    insecure=True
                )
                self.tracer_provider.add_span_processor(
                    BatchSpanProcessor(otlp_exporter)
                )
            except ImportError:
                print("OTLP exporter not available - install opentelemetry-exporter-otlp")
        
        # Setup metrics
        metric_readers = []
        if enable_console:
            metric_readers.append(
                PeriodicExportingMetricReader(
                    ConsoleMetricExporter(),
                    export_interval_millis=5000
                )
            )
        
        self.meter_provider = MeterProvider(
            resource=resource,
            metric_readers=metric_readers
        )
        metrics.set_meter_provider(self.meter_provider)
        
        # Get tracer and meter
        self.tracer = trace.get_tracer(__name__, "1.0.0")
        self.meter = metrics.get_meter(__name__, "1.0.0")
        
        # Create metrics
        self.span_counter = self.meter.create_counter(
            "swarm.spans.total",
            description="Total number of spans created",
            unit="1"
        )
        
        self.command_counter = self.meter.create_counter(
            "swarm.commands.total",
            description="Total number of commands executed",
            unit="1"
        )
        
        self.loop_duration = self.meter.create_histogram(
            "swarm.loop.duration",
            description="Duration of complete swarm loops",
            unit="ms"
        )


class SwarmCLI:
    """
    OpenTelemetry-instrumented CLI for SwarmAgent ecosystem.
    
    Generates properly instrumented spans for all operations.
    """
    
    def __init__(self, telemetry: SwarmTelemetry):
        self.telemetry = telemetry
        self.tracer = telemetry.tracer
    
    @contextmanager
    def _span(self, name: str, attributes: Dict[str, Any] = None):
        """Create a span with automatic status handling."""
        with self.tracer.start_as_current_span(name) as span:
            if attributes:
                span.set_attributes(attributes)
            
            self.telemetry.span_counter.add(1, {"span.type": name.split(".")[1]})
            
            try:
                yield span
                span.set_status(Status(StatusCode.OK))
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise
    
    def roberts_open_motion(self, motion_id: str, meeting_id: str = "board"):
        """Open a motion in Roberts Rules."""
        with self._span("swarmsh.roberts.open", {
            "motion_id": motion_id,
            "meeting_id": meeting_id,
            "swarm.agent": "roberts",
            "swarm.trigger": "open"
        }) as span:
            span.add_event("motion_opened", {
                "motion.description": f"Motion {motion_id} opened for consideration"
            })
            print(f"📋 Opened motion: {motion_id} in meeting: {meeting_id}")
    
    def roberts_vote(self, motion_id: str, voting_method: str = "voice_vote"):
        """Call for a vote on a motion."""
        with self._span("swarmsh.roberts.vote", {
            "motion_id": motion_id,
            "voting_method": voting_method,
            "swarm.agent": "roberts",
            "swarm.trigger": "vote"
        }) as span:
            span.add_event("vote_called", {
                "vote.method": voting_method
            })
            print(f"🗳️  Calling {voting_method} vote on motion: {motion_id}")
    
    def roberts_close(self, motion_id: str, result: str, votes_yes: int = 0, votes_no: int = 0, **kwargs):
        """Close meeting after vote."""
        with self._span("swarmsh.roberts.close", {
            "motion_id": motion_id,
            "result": result,
            "votes_yes": votes_yes,
            "votes_no": votes_no,
            "swarm.agent": "roberts",
            "swarm.trigger": "close",
            **kwargs
        }) as span:
            span.add_event("motion_result", {
                "result": result,
                "votes.yes": votes_yes,
                "votes.no": votes_no,
                "votes.total": votes_yes + votes_no
            })
            print(f"🔨 Motion {motion_id} {result}: {votes_yes}/{votes_no}")
    
    def scrum_plan(self, sprint_number: str, team_id: str, capacity: int):
        """Start sprint planning."""
        with self._span("swarmsh.scrum.plan", {
            "sprint_number": sprint_number,
            "team_id": team_id,
            "capacity": capacity,
            "swarm.agent": "scrum",
            "swarm.trigger": "plan"
        }) as span:
            span.add_event("sprint_planned", {
                "sprint.capacity": capacity,
                "sprint.team": team_id
            })
            print(f"📅 Planning sprint {sprint_number} for team {team_id} (capacity: {capacity})")
    
    def scrum_review(self, sprint_number: str, velocity: int, defect_rate: float, customer_satisfaction: float):
        """Sprint review with metrics."""
        with self._span("swarmsh.scrum.review", {
            "sprint_number": sprint_number,
            "velocity": velocity,
            "defect_rate": defect_rate,
            "customer_satisfaction": customer_satisfaction,
            "swarm.agent": "scrum",
            "swarm.trigger": "review"
        }) as span:
            # Add metric events
            span.add_event("sprint_metrics", {
                "metrics.velocity": velocity,
                "metrics.defect_rate": defect_rate,
                "metrics.satisfaction": customer_satisfaction
            })
            
            # Check for quality issues
            if defect_rate > 3.0:
                span.add_event("quality_issue_detected", {
                    "issue.type": "high_defect_rate",
                    "issue.threshold": 3.0,
                    "issue.actual": defect_rate
                })
            
            print(f"📊 Sprint {sprint_number} review: velocity={velocity}, defects={defect_rate}%, satisfaction={customer_satisfaction}")
    
    def lean_define(self, project_id: str, problem_statement: str, sponsor: str = "scrum-agent"):
        """Define a Lean Six Sigma project."""
        with self._span("swarmsh.lean.define", {
            "project_id": project_id,
            "problem_statement": problem_statement,
            "sponsor": sponsor,
            "swarm.agent": "lean",
            "swarm.trigger": "define"
        }) as span:
            span.add_event("project_defined", {
                "project.charter": f"Charter created for {project_id}"
            })
            print(f"🎯 Defined Lean project {project_id}: {problem_statement}")
    
    def execute_command(self, cmd: NextCommand):
        """Execute a NextCommand from an agent."""
        command_str = f"{cmd.fq_name} {' '.join(cmd.args)}"
        
        with self._span("swarmsh.command.execute", {
            "command": cmd.fq_name,
            "command.args": json.dumps(cmd.args),
            "command.description": cmd.description
        }) as span:
            self.telemetry.command_counter.add(1, {"command.type": cmd.fq_name.split(".")[1]})
            
            # Parse command and execute appropriate method
            parts = cmd.fq_name.split(".")
            if len(parts) >= 3:
                agent = parts[1]
                action = parts[2]
                
                # Build kwargs from args
                kwargs = {}
                i = 0
                while i < len(cmd.args):
                    if cmd.args[i].startswith("--"):
                        key = cmd.args[i][2:].replace("-", "_")
                        value = cmd.args[i + 1] if i + 1 < len(cmd.args) else True
                        kwargs[key] = value
                        i += 2
                    else:
                        i += 1
                
                # Route to appropriate handler
                if agent == "roberts" and action == "voting":
                    self.roberts_vote(**kwargs)
                elif agent == "scrum" and action == "sprint-planning":
                    self.scrum_plan(**kwargs)
                elif agent == "lean" and action == "define":
                    self.lean_define(**kwargs)
                else:
                    span.add_event("command_not_implemented", {
                        "command": cmd.fq_name
                    })
                    print(f"⚠️  Command not implemented: {cmd.fq_name}")


async def run_ecosystem_loop():
    """
    Demonstrate the complete OpenTelemetry ecosystem loop.
    
    Shows how spans flow through the system and trigger agent actions.
    """
    print("🌟 Starting Full OpenTelemetry Ecosystem Loop")
    print("=" * 60)
    
    # Initialize telemetry
    telemetry = SwarmTelemetry(
        service_name="swarm-ecosystem-demo",
        enable_console=False  # Reduce noise for demo
    )
    
    # Create instrumented CLI
    cli = SwarmCLI(telemetry)
    
    # Import agents
    from dslmodel.agents.examples.roberts_agent import RobertsAgent
    from dslmodel.agents.examples.scrum_agent import ScrumAgent
    from dslmodel.agents.examples.lean_agent import LeanAgent
    
    # Create agents with shared span file
    span_file = telemetry.span_file
    agents = {
        "roberts": RobertsAgent(span_file=span_file.name, root_dir=span_file.parent),
        "scrum": ScrumAgent(span_file=span_file.name, root_dir=span_file.parent),
        "lean": LeanAgent(span_file=span_file.name, root_dir=span_file.parent)
    }
    
    print(f"\n📁 Span file: {span_file}")
    print(f"🤖 Agents initialized: {list(agents.keys())}")
    
    # Start monitoring task
    async def monitor_agents():
        """Monitor agents and execute their commands."""
        print("\n🔄 Starting agent monitor...")
        
        # Track processed spans to avoid duplicates
        processed_spans = set()
        
        while True:
            try:
                # Read new spans
                with span_file.open() as f:
                    for line in f:
                        if not line.strip():
                            continue
                        
                        try:
                            span_dict = json.loads(line)
                            span_id = span_dict.get("span_id")
                            
                            if span_id in processed_spans:
                                continue
                            
                            processed_spans.add(span_id)
                            
                            # Convert to SpanData
                            span = SpanData(**span_dict)
                            
                            # Forward to agents
                            for agent_name, agent in agents.items():
                                cmd = agent.forward(span)
                                if cmd:
                                    print(f"\n🤖 {agent_name} agent reacted:")
                                    print(f"   State: {agent.current_state.name}")
                                    print(f"   Command: {cmd.fq_name}")
                                    
                                    # Execute command with telemetry
                                    with telemetry.tracer.start_as_current_span("swarm.loop.iteration") as loop_span:
                                        loop_span.set_attributes({
                                            "loop.agent": agent_name,
                                            "loop.trigger_span": span.name,
                                            "loop.command": cmd.fq_name
                                        })
                                        
                                        # Execute command
                                        cli.execute_command(cmd)
                                        
                                        # Record loop metrics
                                        telemetry.loop_duration.record(
                                            100,  # Simulated duration
                                            {"loop.type": "agent_reaction"}
                                        )
                        
                        except json.JSONDecodeError:
                            continue
                        except Exception as e:
                            print(f"Error processing span: {e}")
            
            except Exception as e:
                print(f"Monitor error: {e}")
            
            await asyncio.sleep(0.5)
    
    # Start monitor in background
    monitor_task = asyncio.create_task(monitor_agents())
    
    # Run demo scenario
    print("\n🎬 Running demo scenario...")
    print("\n1️⃣  Roberts Rules: Opening motion for Sprint 42")
    
    with telemetry.tracer.start_as_current_span("demo.scenario") as scenario_span:
        # Step 1: Roberts opens motion
        cli.roberts_open_motion("sprint42", "board")
        await asyncio.sleep(1)
        
        # Step 2: Roberts calls vote
        print("\n2️⃣  Roberts Rules: Calling vote")
        cli.roberts_vote("sprint42", "voice_vote")
        await asyncio.sleep(1)
        
        # Step 3: Roberts closes with approval (triggers Scrum)
        print("\n3️⃣  Roberts Rules: Motion passes, triggering Sprint planning")
        cli.roberts_close(
            motion_id="sprint42",
            result="passed",
            votes_yes=7,
            votes_no=2,
            sprint_number="42",
            team_id="alpha"
        )
        await asyncio.sleep(2)
        
        # Step 4: Scrum review with quality issue (triggers Lean)
        print("\n4️⃣  Scrum: Sprint review detects quality issue")
        cli.scrum_review(
            sprint_number="42",
            velocity=45,
            defect_rate=5.2,  # Above threshold!
            customer_satisfaction=7.8
        )
        await asyncio.sleep(2)
        
        # Step 5: Lean improvement process
        print("\n5️⃣  Lean: Running improvement process")
        cli.lean_define(
            project_id="defect-sprint42",
            problem_statement="Defect rate 5.2% exceeds 3% threshold"
        )
        
        scenario_span.add_event("scenario_complete", {
            "steps": 5,
            "agents_involved": 3
        })
    
    # Wait a bit for final reactions
    await asyncio.sleep(3)
    
    # Summary
    print("\n📈 Ecosystem Loop Summary:")
    print(f"   Total spans: {processed_spans.__len__()}")
    print(f"   Agents states:")
    for name, agent in agents.items():
        print(f"     - {name}: {agent.current_state.name}")
    
    print("\n✅ Full OpenTelemetry ecosystem loop demonstrated!")
    print("\nThe loop continues autonomously as new spans are generated...")
    
    # Cancel monitor
    monitor_task.cancel()
    
    # Shutdown telemetry
    telemetry.tracer_provider.shutdown()
    telemetry.meter_provider.shutdown()


if __name__ == "__main__":
    asyncio.run(run_ecosystem_loop())