"""Base implementation of swarm agents using FSMMixin."""

from __future__ import annotations
import json
import time
import pathlib
import subprocess
import asyncio
from enum import Enum
from typing import Dict, Type, Optional, Any
from abc import ABC, abstractmethod

from dslmodel.mixins import FSMMixin, trigger
from .swarm_models import NextCommand, SpanData, SwarmAgentModel

# Import generated Weaver models if available
try:
    from dslmodel.otel.models.swarm_attributes import (
        SwarmSpanAttributes, RobertsSpanAttributes, ScrumSpanAttributes, 
        LeanSpanAttributes, PingSpanAttributes, TransitionSpanAttributes
    )
    WEAVER_MODELS_AVAILABLE = True
except ImportError:
    WEAVER_MODELS_AVAILABLE = False


class SwarmAgent(FSMMixin, ABC):
    """
    Lightweight swarm agent that reacts to OpenTelemetry spans.
    
    Integrates with dslmodel's FSMMixin for state management and
    watches a JSONL stream of telemetry spans to trigger actions.
    """
    
    # Must be overridden by subclasses
    StateEnum: Type[Enum]
    TRIGGER_MAP: Dict[str, str]  # keyword -> method name mapping
    LISTEN_FILTER: Optional[str] = None  # Optional span name prefix filter
    
    def __init__(self, 
                 root_dir: Optional[pathlib.Path] = None,
                 span_file: str = "telemetry_spans.jsonl",
                 cli_command: Optional[list] = None):
        """
        Initialize swarm agent.
        
        Args:
            root_dir: Root directory for agent coordination (default: ~/s2s/agent_coordination)
            span_file: Name of the JSONL file containing spans
            cli_command: CLI command to execute (default: ["python", "coordination_cli.py"])
        """
        super().__init__()
        
        # Set up paths
        self.root_dir = root_dir or pathlib.Path("~/s2s/agent_coordination").expanduser()
        self.span_stream = self.root_dir / span_file
        self.cli_command = cli_command or ["python", str(self.root_dir / "coordination_cli.py")]
        
        # Initialize FSM
        self.setup_fsm(state_enum=self.StateEnum, initial=list(self.StateEnum)[0])
        
        # Create model representation
        self.model = SwarmAgentModel(
            name=self.__class__.__name__,
            state=self.current_state.name,
            trigger_map=self.TRIGGER_MAP
        )
    
    def run_cli(self, cmd: NextCommand) -> subprocess.CompletedProcess:
        """Execute a CLI command."""
        full_command = self.cli_command + cmd.path + cmd.args
        return subprocess.run(full_command, capture_output=True, text=True)
    
    async def arun_cli(self, cmd: NextCommand) -> tuple[str, str]:
        """Asynchronously execute a CLI command."""
        full_command = self.cli_command + cmd.path + cmd.args
        proc = await asyncio.create_subprocess_exec(
            *full_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        return stdout.decode(), stderr.decode()
    
    def forward(self, span: SpanData) -> Optional[NextCommand]:
        """
        Route spans to appropriate handler methods based on trigger mapping.
        
        Args:
            span: Parsed span data
            
        Returns:
            NextCommand to execute, or None if no matching trigger
        """
        # Apply LISTEN_FILTER if configured
        if self.LISTEN_FILTER and not span.name.startswith(self.LISTEN_FILTER):
            return None
            
        span_name_lower = span.name.lower()
        
        for trigger_key, method_name in self.TRIGGER_MAP.items():
            if trigger_key in span_name_lower:
                handler = getattr(self, method_name, None)
                if handler:
                    return handler(span)
        
        return None
    
    def _transition(self, prompt: str, dest_state: Enum) -> None:
        """
        Record state transition with span emission.
        
        Args:
            prompt: The prompt/reason for transition
            dest_state: Target state
        """
        # Emit transition span with Weaver-compliant attributes
        transition_span = {
            "name": f"swarm.agent.transition",
            "trace_id": f"trace_{int(time.time() * 1000)}",
            "span_id": f"span_{int(time.time() * 1000000)}",
            "timestamp": time.time(),
            "attributes": {
                "swarm.agent.name": self.__class__.__name__,
                "swarm.agent.transition.from": self.current_state.name,
                "swarm.agent.transition.to": dest_state.name,
                "prompt": prompt
            }
        }
        
        # Validate with Weaver models if available
        if WEAVER_MODELS_AVAILABLE:
            try:
                # Validate attributes match semantic conventions
                attrs = TransitionSpanAttributes(
                    agent_name=self.__class__.__name__,
                    transition_from=self.current_state.name,
                    transition_to=dest_state.name,
                    prompt=prompt
                )
                # Use validated attributes
                transition_span["attributes"].update(attrs.model_dump(exclude_none=True))
            except Exception as e:
                print(f"⚠️ Weaver validation failed: {e}")
        
        # Write to span stream
        with self.span_stream.open("a") as f:
            f.write(json.dumps(transition_span) + "\n")
        
        # Update model state
        self.model.state = dest_state.name
    
    def parse_span(self, line: str) -> Optional[SpanData]:
        """Parse a JSONL line into SpanData."""
        try:
            data = json.loads(line)
            return SpanData(**data)
        except (json.JSONDecodeError, ValueError):
            return None
    
    def run(self):
        """
        Watch span stream file and react to new spans.
        
        This is the main event loop for the agent.
        """
        # Ensure span file exists
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self.span_stream.touch()
        
        print(f"🔄 {self.__class__.__name__} starting - watching {self.span_stream}")
        
        with self.span_stream.open() as f:
            # Seek to end of file
            f.seek(0, 2)
            
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.2)
                    continue
                
                span = self.parse_span(line.strip())
                if not span:
                    continue
                
                # Update model state
                self.model.state = self.current_state.name
                
                # Forward to handler
                cmd = self.forward(span)
                if cmd:
                    print(f"📌 Executing: {' '.join(cmd.path + cmd.args)}")
                    result = self.run_cli(cmd)
                    if result.returncode != 0:
                        print(f"❌ Command failed: {result.stderr}")
    
    async def arun(self):
        """
        Async version of run() for better integration with async codebases.
        """
        # Ensure span file exists
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self.span_stream.touch()
        
        print(f"🔄 {self.__class__.__name__} starting (async) - watching {self.span_stream}")
        
        # Use aiofiles if available, otherwise fall back to sync with executor
        try:
            import aiofiles
            async with aiofiles.open(self.span_stream, mode='r') as f:
                await f.seek(0, 2)
                while True:
                    line = await f.readline()
                    if not line:
                        await asyncio.sleep(0.2)
                        continue
                    
                    span = self.parse_span(line.strip())
                    if not span:
                        continue
                    
                    self.model.state = self.current_state.name
                    cmd = self.forward(span)
                    if cmd:
                        print(f"📌 Executing: {' '.join(cmd.path + cmd.args)}")
                        stdout, stderr = await self.arun_cli(cmd)
                        if stderr:
                            print(f"❌ Command error: {stderr}")
        except ImportError:
            # Fallback to sync version in executor
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.run)
    
    @abstractmethod
    def setup_triggers(self):
        """
        Setup trigger methods for state transitions.
        
        Subclasses should implement this to define their state machine.
        """
        pass