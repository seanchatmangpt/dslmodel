"""OpenTelemetry-enabled SwarmAgent with full observability."""

from __future__ import annotations
import json
import asyncio
import pathlib
import subprocess
import time
import logging
import os
from enum import Enum
from typing import Dict, Type, Optional, Any, List
from abc import ABC
from contextlib import contextmanager

from opentelemetry import trace, context
from opentelemetry.trace import SpanKind, Status, StatusCode
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from dslmodel.mixins import FSMMixin, trigger
from dslmodel.agents.swarm import NextCommand, SpanData, SwarmAgentModel
from .otel_instrumentation import (
    OTelInstrumentation, 
    SwarmSpanAttributes, 
    init_otel, 
    get_otel
)


logger = logging.getLogger(__name__)


class OTelSwarmAgent(FSMMixin, ABC):
    """
    OpenTelemetry-enabled swarm agent with full distributed tracing.
    
    Features:
    - Proper span creation with semantic conventions
    - Context propagation across agent boundaries
    - Metrics for state transitions and command execution
    - Structured logging with trace correlation
    - Integration with OTel Collector
    """
    
    # Must be overridden by subclasses
    StateEnum: Type[Enum]
    TRIGGER_MAP: Dict[str, str]
    LISTEN_FILTER: Optional[str] = None
    
    def __init__(self,
                 service_name: Optional[str] = None,
                 root_dir: Optional[pathlib.Path] = None,
                 otlp_endpoint: Optional[str] = None,
                 enable_console_export: bool = False):
        """
        Initialize OTel-enabled swarm agent.
        
        Args:
            service_name: Service name for OTel (defaults to class name)
            root_dir: Root directory for coordination
            otlp_endpoint: OTLP collector endpoint
            enable_console_export: Enable console span export
        """
        super().__init__()
        
        # Set up paths
        self.root_dir = root_dir or pathlib.Path("~/s2s/agent_coordination").expanduser()
        self.root_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize OpenTelemetry
        self.service_name = service_name or f"{self.__class__.__name__.lower()}-agent"
        self.otel = init_otel(
            service_name=self.service_name,
            otlp_endpoint=otlp_endpoint,
            enable_console_export=enable_console_export
        )
        
        # Initialize FSM
        self.setup_fsm(state_enum=self.StateEnum, initial=list(self.StateEnum)[0])
        
        # Create model representation
        self.model = SwarmAgentModel(
            name=self.__class__.__name__,
            state=self.current_state.name,
            trigger_map=self.TRIGGER_MAP
        )
        
        # Record agent activation
        self.otel.active_agents.add(1, {
            SwarmSpanAttributes.AGENT_NAME: self.service_name
        })
        
        logger.info(f"Initialized {self.service_name} with OTel instrumentation")
    
    def __del__(self):
        """Record agent deactivation."""
        try:
            self.otel.active_agents.add(-1, {
                SwarmSpanAttributes.AGENT_NAME: self.service_name
            })
        except:
            pass
    
    async def consume_spans(self):
        """
        Consume spans from OTel Collector via OTLP Logs.
        
        This replaces file-based span watching with proper OTel integration.
        In production, this would subscribe to a span stream from the collector.
        """
        # For demo purposes, we'll use gRPC streaming from collector
        # In production, use collector's span processors or Kafka
        import grpc
        from opentelemetry.proto.collector.trace.v1 import trace_service_pb2
        from opentelemetry.proto.collector.trace.v1 import trace_service_pb2_grpc
        
        channel = grpc.insecure_channel(self.otel.otlp_endpoint)
        stub = trace_service_pb2_grpc.TraceServiceStub(channel)
        
        # This is a simplified example - real implementation would use
        # proper streaming or queue-based consumption
        logger.info(f"Connected to OTel Collector at {self.otel.otlp_endpoint}")
    
    def run_cli(self, cmd: NextCommand) -> subprocess.CompletedProcess:
        """Execute CLI command with tracing."""
        command_str = " ".join(cmd.path + cmd.args)
        
        with self.otel.trace_span(
            name=f"cli.execute.{cmd.path[0] if cmd.path else cmd.fq_name}",
            kind=SpanKind.CLIENT,
            attributes={
                SwarmSpanAttributes.SWARM_COMMAND: command_str,
                SwarmSpanAttributes.SWARM_COMMAND_ARGS: json.dumps(cmd.args),
                "command.description": cmd.description or ""
            }
        ) as span:
            start_time = time.time()
            try:
                # Build full command
                if cmd.fq_name:
                    # Use fq_name as direct command
                    full_command = [cmd.fq_name] + cmd.args
                else:
                    # Use path-based command
                    full_command = ["python", "-m", "dslmodel.cli"] + cmd.path + cmd.args
                
                # Inject trace context into environment
                env = os.environ.copy()
                carrier = {}
                self.otel.inject_context(carrier)
                env.update(carrier)
                
                result = subprocess.run(
                    full_command,
                    capture_output=True,
                    text=True,
                    env=env
                )
                
                # Record metrics
                success = result.returncode == 0
                self.otel.record_command_execution(
                    agent_name=self.service_name,
                    command=command_str,
                    success=success
                )
                
                # Add result to span
                span.set_attribute("command.exit_code", result.returncode)
                if not success:
                    span.set_attribute("command.stderr", result.stderr[:1000])
                
                return result
                
            finally:
                duration_ms = (time.time() - start_time) * 1000
                span.set_attribute("command.duration_ms", duration_ms)
    
    def forward(self, span_data: Dict[str, Any]) -> Optional[NextCommand]:
        """
        Route spans to handlers with full tracing.
        
        Args:
            span_data: Raw span data from OTel
            
        Returns:
            NextCommand to execute, or None
        """
        # Extract parent context from span
        parent_ctx = self._extract_parent_context(span_data)
        
        with context.attach(parent_ctx):
            span_name = span_data.get("name", "")
            
            # Apply LISTEN_FILTER
            if self.LISTEN_FILTER and not span_name.startswith(self.LISTEN_FILTER):
                return None
            
            # Create processing span with link to triggering span
            with self.otel.trace_span(
                name=f"agent.process_span",
                attributes={
                    SwarmSpanAttributes.AGENT_NAME: self.service_name,
                    SwarmSpanAttributes.AGENT_STATE: self.current_state.name,
                    "span.trigger_name": span_name
                }
            ) as processing_span:
                # Add link to triggering span
                if "trace_id" in span_data and "span_id" in span_data:
                    link = self.otel.create_span_link(
                        trace_id=span_data["trace_id"],
                        span_id=span_data["span_id"],
                        attributes={"link.type": "triggered_by"}
                    )
                    processing_span.add_link(link)
                
                # Route to handler
                span_name_lower = span_name.lower()
                for trigger_key, method_name in self.TRIGGER_MAP.items():
                    if trigger_key in span_name_lower:
                        handler = getattr(self, method_name, None)
                        if handler:
                            # Create SpanData object
                            span_obj = SpanData(
                                name=span_name,
                                trace_id=span_data.get("trace_id", ""),
                                span_id=span_data.get("span_id", ""),
                                parent_span_id=span_data.get("parent_span_id"),
                                attributes=span_data.get("attributes", {}),
                                timestamp=span_data.get("timestamp", time.time())
                            )
                            
                            processing_span.set_attribute("handler.method", method_name)
                            return handler(span_obj)
                
                return None
    
    def _extract_parent_context(self, span_data: Dict[str, Any]) -> context.Context:
        """Extract parent context from span data for propagation."""
        # Build carrier from span data
        carrier = {}
        
        # Add W3C Trace Context headers
        if "trace_id" in span_data and "span_id" in span_data:
            trace_id = span_data["trace_id"]
            parent_id = span_data["span_id"]
            
            # Format: version-trace_id-parent_id-trace_flags
            traceparent = f"00-{trace_id:032x}-{parent_id:016x}-01"
            carrier["traceparent"] = traceparent
            
            # Add any trace state
            if "trace_state" in span_data:
                carrier["tracestate"] = span_data["trace_state"]
        
        # Extract context from carrier
        return self.otel.extract_context(carrier)
    
    def _transition(self, prompt: str, dest_state: Enum) -> None:
        """
        Record state transition with distributed tracing.
        
        Args:
            prompt: Reason for transition
            dest_state: Target state
        """
        with self.otel.trace_span(
            name=f"agent.state_transition",
            attributes={
                SwarmSpanAttributes.AGENT_NAME: self.service_name,
                SwarmSpanAttributes.AGENT_TRANSITION: f"{self.current_state.name} → {dest_state.name}",
                "transition.reason": prompt,
                "from_state": self.current_state.name,
                "to_state": dest_state.name
            }
        ) as span:
            # Record metric
            self.otel.record_state_transition(
                agent_name=self.service_name,
                from_state=self.current_state.name,
                to_state=dest_state.name,
                framework=self.__class__.__name__.replace("Agent", "").lower()
            )
            
            # Update model
            self.model.state = dest_state.name
            
            # Log transition
            logger.info(
                f"State transition: {self.current_state.name} → {dest_state.name}",
                extra={
                    "agent": self.service_name,
                    "transition": prompt
                }
            )
    
    async def arun(self):
        """
        Async run loop with OTel span consumption.
        
        In production, this would consume from a proper span stream
        (Kafka, Redis Streams, etc.) instead of a file.
        """
        logger.info(f"Starting {self.service_name} agent with OTel instrumentation")
        
        with self.otel.trace_span(
            name=f"agent.lifecycle",
            kind=SpanKind.SERVER,
            attributes={
                SwarmSpanAttributes.AGENT_NAME: self.service_name,
                "agent.version": self.model.metadata.get("version", "1.0.0")
            }
        ):
            try:
                # For now, fall back to file watching
                # In production, replace with proper span streaming
                span_file = self.root_dir / "telemetry_spans.jsonl"
                span_file.touch()
                
                # Seek to end
                with open(span_file, "r") as f:
                    f.seek(0, 2)
                    
                    while True:
                        line = f.readline()
                        if not line:
                            await asyncio.sleep(0.1)
                            continue
                        
                        try:
                            span_data = json.loads(line.strip())
                            
                            # Process span
                            start_time = time.time()
                            cmd = self.forward(span_data)
                            
                            # Record processing duration
                            duration_ms = (time.time() - start_time) * 1000
                            self.otel.span_processing_duration.record(
                                duration_ms,
                                attributes={
                                    SwarmSpanAttributes.AGENT_NAME: self.service_name
                                }
                            )
                            
                            # Execute command if returned
                            if cmd:
                                logger.info(f"Executing command: {cmd.description or 'Unknown'}")
                                
                                # Run async command execution
                                loop = asyncio.get_event_loop()
                                result = await loop.run_in_executor(
                                    None, 
                                    self.run_cli, 
                                    cmd
                                )
                                
                                if result.returncode != 0:
                                    logger.error(f"Command failed: {result.stderr}")
                                    
                        except json.JSONDecodeError:
                            logger.warning(f"Invalid JSON in span stream: {line}")
                        except Exception as e:
                            logger.error(f"Error processing span: {e}", exc_info=True)
                            
            except KeyboardInterrupt:
                logger.info(f"Shutting down {self.service_name} agent")
            except Exception as e:
                logger.error(f"Agent error: {e}", exc_info=True)
                raise


# Example: OTel-enabled Roberts Agent
class OTelRobertsAgent(OTelSwarmAgent):
    """Roberts Rules agent with full OpenTelemetry instrumentation."""
    
    from enum import Enum, auto
    
    class RorState(Enum):
        IDLE = auto()
        MOTION_OPEN = auto()
        VOTING = auto()
        CLOSED = auto()
    
    StateEnum = RorState
    LISTEN_FILTER = "swarmsh.roberts."
    TRIGGER_MAP = {
        "open": "open_motion",
        "vote": "call_vote",
        "close": "adjourn",
    }
    
    def setup_triggers(self):
        pass
    
    @trigger(source=RorState.IDLE, dest=RorState.MOTION_OPEN)
    def open_motion(self, span: SpanData) -> Optional[NextCommand]:
        """Open motion with distributed tracing."""
        motion_id = span.attributes.get("motion_id", "unknown")
        meeting_id = span.attributes.get("meeting_id", "board")
        
        # Create span for business logic
        with self.otel.trace_span(
            name="roberts.open_motion",
            attributes={
                "motion.id": motion_id,
                "meeting.id": meeting_id,
                SwarmSpanAttributes.SWARM_FRAMEWORK: "roberts"
            }
        ):
            self._transition(f"Opening motion {motion_id}", self.RorState.MOTION_OPEN)
            
            return NextCommand(
                fq_name="swarmsh.roberts.call-to-order",
                args=["--meeting-id", meeting_id, "--motion-id", motion_id],
                description=f"Call to order for motion {motion_id}"
            )