"""
thesis_otel_integration.py
───────────────────────────────────────────────────────────────────────────────
Real OTEL Ecosystem Integration for SwarmSH Thesis
• Integrates with actual OpenTelemetry SDK and Collector
• Shows WeaverForge code generation pipeline
• Demonstrates real trace analysis and feedback
• Production-ready patterns for telemetry-driven development
"""

from __future__ import annotations
import os
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field

import yaml
import json


# ─────────────────────────────────────────────────────────────────────────────
# 1. OTEL Collector Configuration
# ─────────────────────────────────────────────────────────────────────────────

class OTELCollectorConfig(BaseModel):
    """OpenTelemetry Collector configuration for SwarmSH"""
    
    receivers: Dict[str, Any] = Field(default_factory=lambda: {
        "otlp": {
            "protocols": {
                "grpc": {"endpoint": "0.0.0.0:4317"},
                "http": {"endpoint": "0.0.0.0:4318"}
            }
        }
    })
    
    processors: Dict[str, Any] = Field(default_factory=lambda: {
        "batch": {
            "timeout": "1s",
            "send_batch_size": 1024
        },
        "attributes": {
            "actions": [
                {
                    "key": "swarmsh.version",
                    "value": "1.0.0",
                    "action": "insert"
                }
            ]
        },
        "filter": {
            "traces": {
                "span": [
                    'attributes["swarmsh.thesis.enabled"] == true'
                ]
            }
        }
    })
    
    exporters: Dict[str, Any] = Field(default_factory=lambda: {
        "logging": {
            "loglevel": "debug"
        },
        "jaeger": {
            "endpoint": "jaeger:14250",
            "tls": {"insecure": True}
        },
        "prometheus": {
            "endpoint": "0.0.0.0:8889"
        },
        "file": {
            "path": "/var/log/swarmsh/traces.json",
            "rotation": {
                "max_megabytes": 100,
                "max_days": 7,
                "max_backups": 3
            }
        }
    })
    
    service: Dict[str, Any] = Field(default_factory=lambda: {
        "pipelines": {
            "traces": {
                "receivers": ["otlp"],
                "processors": ["batch", "attributes", "filter"],
                "exporters": ["logging", "jaeger", "file"]
            },
            "metrics": {
                "receivers": ["otlp"],
                "processors": ["batch"],
                "exporters": ["prometheus", "logging"]
            }
        },
        "extensions": {
            "health_check": {},
            "pprof": {},
            "zpages": {}
        }
    })
    
    def to_yaml_file(self, path: Path):
        """Write collector config to YAML file"""
        config = {
            "receivers": self.receivers,
            "processors": self.processors,
            "exporters": self.exporters,
            "service": self.service
        }
        path.write_text(yaml.dump(config, sort_keys=False))


# ─────────────────────────────────────────────────────────────────────────────
# 2. WeaverForge Integration
# ─────────────────────────────────────────────────────────────────────────────

class WeaverForgeConfig(BaseModel):
    """Configuration for OpenTelemetry Weaver Forge"""
    
    semantic_convention_path: Path = Field(..., description="Path to semantic convention YAML")
    output_dir: Path = Field(..., description="Output directory for generated code")
    templates_dir: Optional[Path] = Field(None, description="Custom templates directory")
    languages: List[str] = Field(default=["rust", "python", "go"], description="Target languages")
    
    def generate_weaver_config(self) -> Dict[str, Any]:
        """Generate weaver.yaml configuration"""
        return {
            "params": {
                "attributes": [],
                "metrics": [],
                "spans": []
            },
            "templates": [
                {
                    "pattern": "*.j2",
                    "filter": "."
                }
            ],
            "outputs": {
                "rust": {
                    "dir": str(self.output_dir / "rust")
                },
                "python": {
                    "dir": str(self.output_dir / "python")
                },
                "go": {
                    "dir": str(self.output_dir / "go")
                }
            }
        }
    
    def run_forge(self) -> subprocess.CompletedProcess:
        """Execute WeaverForge code generation"""
        # Create weaver config
        config_path = self.output_dir / "weaver.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(yaml.dump(self.generate_weaver_config()))
        
        # Run weaver forge
        cmd = [
            "weaver", "forge",
            "generate",
            "--config", str(config_path),
            "--semantic-convention", str(self.semantic_convention_path),
            "--output", str(self.output_dir)
        ]
        
        if self.templates_dir:
            cmd.extend(["--templates", str(self.templates_dir)])
        
        return subprocess.run(cmd, capture_output=True, text=True)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Trace Analysis Pipeline
# ─────────────────────────────────────────────────────────────────────────────

class TraceQuery(BaseModel):
    """Query for analyzing traces"""
    service_name: Optional[str] = None
    operation_name: Optional[str] = None
    min_duration_ms: Optional[float] = None
    max_duration_ms: Optional[float] = None
    tags: Dict[str, Any] = Field(default_factory=dict)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: int = Field(default=100)

class TraceAnalyzer(BaseModel):
    """Analyzes traces from OTEL collector exports"""
    
    trace_file_path: Path = Field(..., description="Path to exported traces JSON")
    
    def load_traces(self) -> List[Dict[str, Any]]:
        """Load traces from file export"""
        if not self.trace_file_path.exists():
            return []
        
        traces = []
        with open(self.trace_file_path, 'r') as f:
            for line in f:
                try:
                    trace = json.loads(line)
                    traces.append(trace)
                except json.JSONDecodeError:
                    continue
        return traces
    
    def query_traces(self, query: TraceQuery) -> List[Dict[str, Any]]:
        """Query traces based on criteria"""
        traces = self.load_traces()
        filtered = []
        
        for trace in traces:
            # Apply filters
            if query.service_name and trace.get("serviceName") != query.service_name:
                continue
                
            if query.operation_name and trace.get("operationName") != query.operation_name:
                continue
                
            duration_ms = trace.get("duration", 0) / 1000  # Convert from microseconds
            if query.min_duration_ms and duration_ms < query.min_duration_ms:
                continue
                
            if query.max_duration_ms and duration_ms > query.max_duration_ms:
                continue
            
            # Check tags
            trace_tags = {t["key"]: t["value"] for t in trace.get("tags", [])}
            if not all(trace_tags.get(k) == v for k, v in query.tags.items()):
                continue
            
            filtered.append(trace)
        
        return filtered[:query.limit]
    
    def analyze_patterns(self) -> Dict[str, Any]:
        """Analyze trace patterns for contradictions"""
        traces = self.load_traces()
        
        analysis = {
            "total_traces": len(traces),
            "services": set(),
            "operations": set(),
            "slow_operations": [],
            "error_operations": [],
            "span_statistics": {},
            "contradictions": []
        }
        
        operation_stats = {}
        
        for trace in traces:
            service = trace.get("serviceName", "unknown")
            operation = trace.get("operationName", "unknown")
            duration_ms = trace.get("duration", 0) / 1000
            
            analysis["services"].add(service)
            analysis["operations"].add(operation)
            
            # Track operation statistics
            if operation not in operation_stats:
                operation_stats[operation] = {
                    "count": 0,
                    "total_duration": 0,
                    "errors": 0,
                    "durations": []
                }
            
            stats = operation_stats[operation]
            stats["count"] += 1
            stats["total_duration"] += duration_ms
            stats["durations"].append(duration_ms)
            
            # Check for errors
            for tag in trace.get("tags", []):
                if tag["key"] == "error" and tag["value"]:
                    stats["errors"] += 1
            
            # Flag slow operations
            if duration_ms > 1000:  # 1 second
                analysis["slow_operations"].append({
                    "operation": operation,
                    "duration_ms": duration_ms,
                    "trace_id": trace.get("traceID")
                })
        
        # Calculate statistics
        for operation, stats in operation_stats.items():
            if stats["count"] > 0:
                avg_duration = stats["total_duration"] / stats["count"]
                error_rate = stats["errors"] / stats["count"]
                
                analysis["span_statistics"][operation] = {
                    "count": stats["count"],
                    "avg_duration_ms": avg_duration,
                    "error_rate": error_rate,
                    "p95_duration_ms": sorted(stats["durations"])[int(0.95 * len(stats["durations"]))] if stats["durations"] else 0
                }
                
                # Detect contradictions
                if avg_duration > 500 and stats["count"] > 10:
                    analysis["contradictions"].append({
                        "type": "performance",
                        "operation": operation,
                        "avg_duration_ms": avg_duration,
                        "impact": "high" if avg_duration > 1000 else "medium"
                    })
                
                if error_rate > 0.1:
                    analysis["contradictions"].append({
                        "type": "reliability",
                        "operation": operation,
                        "error_rate": error_rate,
                        "impact": "high" if error_rate > 0.3 else "medium"
                    })
        
        # Convert sets to lists for JSON serialization
        analysis["services"] = list(analysis["services"])
        analysis["operations"] = list(analysis["operations"])
        
        return analysis


# ─────────────────────────────────────────────────────────────────────────────
# 4. Complete Integration Pipeline
# ─────────────────────────────────────────────────────────────────────────────

class OTELIntegrationPipeline(BaseModel):
    """Complete OTEL integration pipeline for SwarmSH thesis"""
    
    workspace_dir: Path = Field(..., description="Workspace directory")
    collector_config: OTELCollectorConfig = Field(default_factory=OTELCollectorConfig)
    
    def setup_workspace(self):
        """Setup the workspace directory structure"""
        dirs = [
            self.workspace_dir / "config",
            self.workspace_dir / "semconv",
            self.workspace_dir / "generated",
            self.workspace_dir / "traces",
            self.workspace_dir / "analysis"
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def generate_docker_compose(self) -> str:
        """Generate docker-compose.yml for OTEL stack"""
        compose = {
            "version": "3.8",
            "services": {
                "otel-collector": {
                    "image": "otel/opentelemetry-collector-contrib:latest",
                    "command": ["--config=/etc/otel-collector-config.yaml"],
                    "volumes": [
                        f"{self.workspace_dir}/config/collector.yaml:/etc/otel-collector-config.yaml",
                        f"{self.workspace_dir}/traces:/var/log/swarmsh"
                    ],
                    "ports": [
                        "4317:4317",   # OTLP gRPC
                        "4318:4318",   # OTLP HTTP
                        "8889:8889",   # Prometheus metrics
                        "13133:13133"  # Health check
                    ]
                },
                "jaeger": {
                    "image": "jaegertracing/all-in-one:latest",
                    "ports": [
                        "16686:16686",  # Jaeger UI
                        "14250:14250"   # gRPC
                    ],
                    "environment": {
                        "COLLECTOR_OTLP_ENABLED": "true"
                    }
                },
                "prometheus": {
                    "image": "prom/prometheus:latest",
                    "volumes": [
                        f"{self.workspace_dir}/config/prometheus.yml:/etc/prometheus/prometheus.yml"
                    ],
                    "ports": ["9090:9090"]
                }
            }
        }
        
        compose_path = self.workspace_dir / "docker-compose.yml"
        compose_path.write_text(yaml.dump(compose, sort_keys=False))
        return str(compose_path)
    
    def generate_prometheus_config(self):
        """Generate Prometheus configuration"""
        config = {
            "global": {
                "scrape_interval": "15s"
            },
            "scrape_configs": [
                {
                    "job_name": "otel-collector",
                    "static_configs": [
                        {"targets": ["otel-collector:8889"]}
                    ]
                }
            ]
        }
        
        config_path = self.workspace_dir / "config" / "prometheus.yml"
        config_path.write_text(yaml.dump(config, sort_keys=False))
    
    def create_example_app(self) -> Path:
        """Create example Python app that emits thesis spans"""
        app_code = '''#!/usr/bin/env python3
"""
SwarmSH Thesis Example App
Emits thesis spans to demonstrate the OTEL ecosystem loop
"""

import time
import random
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configure OTEL
resource = Resource.create({
    "service.name": "swarmsh-thesis",
    "service.version": "1.0.0"
})

provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(
    OTLPSpanExporter(endpoint="localhost:4317", insecure=True)
)
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer("swarmsh.thesis")

def emit_thesis_spans():
    """Emit thesis demonstration spans"""
    with tracer.start_as_current_span("swarmsh.thesis.demo") as demo_span:
        demo_span.set_attribute("swarmsh.thesis.enabled", True)
        
        # Telemetry as system
        with tracer.start_as_current_span("swarmsh.thesis.telemetry_as_system") as span:
            span.set_attribute("validated", True)
            span.set_attribute("brief", "Telemetry is the system, not an add-on.")
            time.sleep(0.1)
        
        # Span drives code
        with tracer.start_as_current_span("swarmsh.thesis.span_drives_code") as span:
            span.set_attribute("code_generated", True)
            span.set_attribute("brief", "Spans generate code & CLI.")
            time.sleep(0.05)
            
            # Simulate slow operation sometimes
            if random.random() < 0.3:
                time.sleep(1.5)
                span.set_attribute("slow_operation", True)
        
        # Trace to prompt emergence
        with tracer.start_as_current_span("swarmsh.thesis.trace_to_prompt_emergence") as span:
            span.set_attribute("prompts_generated", random.randint(1, 5))
            span.set_attribute("brief", "Traces → LLM prompts (emergent).")
            time.sleep(0.08)
        
        # Communication channel
        with tracer.start_as_current_span("swarmsh.thesis.telemetry_communication_channel") as span:
            span.set_attribute("messages_passed", random.randint(10, 100))
            span.set_attribute("brief", "Spans are the agent messaging bus.")
            time.sleep(0.06)
            
            # Simulate errors sometimes
            if random.random() < 0.2:
                span.set_status(trace.Status(trace.StatusCode.ERROR, "Simulated error"))
                span.set_attribute("error", True)
        
        # System models itself
        with tracer.start_as_current_span("swarmsh.thesis.system_models_itself") as span:
            span.set_attribute("model_accuracy", random.uniform(0.8, 1.0))
            span.set_attribute("brief", "Trace graph is a live self-model.")
            time.sleep(0.07)

if __name__ == "__main__":
    print("SwarmSH Thesis Demo - Emitting spans...")
    for i in range(10):
        print(f"  Iteration {i+1}/10")
        emit_thesis_spans()
        time.sleep(1)
    print("Done!")
'''
        
        app_path = self.workspace_dir / "example_app.py"
        app_path.write_text(app_code)
        app_path.chmod(0o755)
        return app_path
    
    def run_pipeline(self):
        """Run the complete OTEL integration pipeline"""
        print("🚀 SwarmSH OTEL Integration Pipeline")
        print("="*60)
        
        # Setup
        print("\n📁 Setting up workspace...")
        self.setup_workspace()
        
        # Generate configs
        print("📝 Generating configurations...")
        self.collector_config.to_yaml_file(self.workspace_dir / "config" / "collector.yaml")
        self.generate_prometheus_config()
        compose_file = self.generate_docker_compose()
        
        # Create example app
        print("🐍 Creating example application...")
        app_path = self.create_example_app()
        
        # Generate instructions
        instructions = f"""
        
📋 OTEL Integration Setup Instructions:

1. Start the OTEL stack:
   cd {self.workspace_dir}
   docker-compose up -d

2. Wait for services to start:
   docker-compose ps

3. Run the example app:
   pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp
   python {app_path}

4. View traces in Jaeger:
   http://localhost:16686

5. View metrics in Prometheus:
   http://localhost:9090

6. Analyze exported traces:
   cat {self.workspace_dir}/traces/traces.json | jq '.'

7. Stop the stack:
   docker-compose down

Generated files:
- {self.workspace_dir}/config/collector.yaml
- {self.workspace_dir}/config/prometheus.yml
- {compose_file}
- {app_path}
"""
        
        print(instructions)
        
        # Save instructions
        instructions_path = self.workspace_dir / "README.md"
        instructions_path.write_text(instructions)
        
        return self.workspace_dir


# ─────────────────────────────────────────────────────────────────────────────
# 5. Demo Script
# ─────────────────────────────────────────────────────────────────────────────

def demo_otel_integration():
    """Demonstrate the complete OTEL integration"""
    
    # Create workspace
    workspace = Path(tempfile.mkdtemp(prefix="swarmsh_otel_"))
    print(f"📂 Workspace: {workspace}")
    
    # Create pipeline
    pipeline = OTELIntegrationPipeline(workspace_dir=workspace)
    
    # Run pipeline
    result_dir = pipeline.run_pipeline()
    
    # Create analyzer
    analyzer = TraceAnalyzer(trace_file_path=workspace / "traces" / "traces.json")
    
    print("\n📊 Trace Analysis (after running example app):")
    print("Run the example app first, then re-run this script to see analysis")
    
    # If traces exist, analyze them
    if analyzer.trace_file_path.exists():
        analysis = analyzer.analyze_patterns()
        print(json.dumps(analysis, indent=2))
        
        # Save analysis
        analysis_path = workspace / "analysis" / "trace_analysis.json"
        analysis_path.write_text(json.dumps(analysis, indent=2))
        print(f"\n💾 Analysis saved to: {analysis_path}")


if __name__ == "__main__":
    demo_otel_integration()