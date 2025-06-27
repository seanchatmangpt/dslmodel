# Troubleshooting Guide

## Overview

This guide provides systematic approaches to diagnosing and resolving SwarmAgent issues. Following CLAUDE.md principles, all troubleshooting relies on **OpenTelemetry traces**, **logs**, and **metrics** rather than assumptions.

## Diagnostic Commands

### Quick Health Check
```bash
# Overall system status
dsl swarm status

# Validate span processing
dsl swarm validate

# Check recent activity
dsl swarm monitor --last 10
```

### Detailed Diagnostics
```bash
# Enable debug logging
export SWARM_DEBUG=1

# Check Weaver compliance
weaver registry check -r src/dslmodel/weaver/registry/

# Generate diagnostic report
dsl swarm validate --performance --report --output diag_report.json
```

## Common Issues

### 1. Agents Not Responding

**Symptoms**:
- No coordination events in monitoring
- Spans emitted but no state transitions
- Commands not generated

**Diagnosis**:
```bash
# Check agent process status
dsl swarm status

# Verify span filtering
cat ~/.swarm_coordination/telemetry_spans.jsonl | grep "roberts"

# Test manual span emission
dsl swarm emit 'swarmsh.roberts.open' --attrs '{"motion_id": "test123"}'
```

**Root Causes & Solutions**:

**A. Agent Process Not Running**:
```bash
# Check if agents are running
ps aux | grep "dsl swarm start"

# Start missing agents
dsl swarm start roberts --background
dsl swarm start scrum --background
dsl swarm start lean --background
```

**B. Span Filter Mismatch**:
```python
# Check LISTEN_FILTER in agent
class RobertsAgent(SwarmAgent):
    LISTEN_FILTER = "swarmsh.roberts"  # Must match span prefix
```

**C. Coordination Directory Issues**:
```bash
# Check directory permissions
ls -la ~/.swarm_coordination/
chmod 755 ~/.swarm_coordination/

# Verify file access
touch ~/.swarm_coordination/test_file && rm ~/.swarm_coordination/test_file
```

### 2. State Transition Failures

**Symptoms**:
- Agents stuck in intermediate states
- Unexpected state transitions
- State machine errors in logs

**Diagnosis**:
```bash
# Check current agent states
python -c "
from dslmodel.agents.examples.roberts_agent import RobertsAgent
agent = RobertsAgent()
print(f'Roberts state: {agent.current_state}')
"

# Review state transition logs
grep "state transition" ~/.swarm_coordination/agent.log
```

**Root Causes & Solutions**:

**A. Invalid State Transitions**:
```python
# Verify @trigger decorators match state flow
@trigger(source=RorState.VOTING, dest=RorState.CLOSED)  # ✅ Valid
@trigger(source=RorState.IDLE, dest=RorState.CLOSED)    # ❌ Invalid
```

**B. Exception During Transition**:
```python
# Add error handling to trigger methods
@trigger(source=RorState.IDLE, dest=RorState.MOTION_OPEN)
def open_motion(self, span: SpanData) -> Optional[NextCommand]:
    try:
        # Process span
        return self._create_command(span)
    except Exception as e:
        self.logger.error(f"Transition failed: {e}")
        # Reset to safe state
        self.current_state = RorState.IDLE
        return None
```

**C. Concurrent State Modifications**:
```bash
# Check for multiple agent instances
ps aux | grep "roberts" | wc -l
# Should be 1, kill extras if > 1
```

### 3. Span Processing Errors

**Symptoms**:
- Spans in JSONL but not processed
- JSON parsing errors
- Missing required attributes

**Diagnosis**:
```bash
# Validate span format
tail -5 ~/.swarm_coordination/telemetry_spans.jsonl | jq '.'

# Check for malformed spans
grep -v '^{' ~/.swarm_coordination/telemetry_spans.jsonl

# Verify required attributes
jq '.attributes | has("motion_id")' ~/.swarm_coordination/telemetry_spans.jsonl
```

**Root Causes & Solutions**:

**A. Malformed JSON**:
```bash
# Find and remove malformed lines
python -c "
import json
with open('~/.swarm_coordination/telemetry_spans.jsonl', 'r') as f:
    for i, line in enumerate(f):
        try:
            json.loads(line)
        except json.JSONDecodeError as e:
            print(f'Line {i+1}: {e}')
            print(f'Content: {line}')
"
```

**B. Missing Required Attributes**:
```python
# Add attribute validation
def parse_span(self, line: str) -> Optional[SpanData]:
    try:
        data = json.loads(line)
        span = SpanData(**data)
        
        # Validate required attributes
        required_attrs = self.get_required_attributes(span.name)
        for attr in required_attrs:
            if attr not in span.attributes:
                self.logger.warning(f"Missing required attribute: {attr}")
                return None
                
        return span
    except Exception as e:
        self.logger.error(f"Span parsing failed: {e}")
        return None
```

### 4. Performance Issues

**Symptoms**:
- High latency in coordination
- Memory usage growing continuously
- CPU usage spikes

**Diagnosis**:
```bash
# Monitor resource usage
top -p $(pgrep -f "dsl swarm")

# Check memory leaks
ps -o pid,rss,vsz,comm -p $(pgrep -f "dsl swarm")

# Measure processing latency
time dsl swarm emit 'test.span' --attrs '{}'
```

**Root Causes & Solutions**:

**A. Memory Leaks**:
```python
# Check for growing state
class SwarmAgent:
    def __init__(self):
        self._span_cache = {}  # ❌ Can grow unbounded
        
    # Better: Use LRU cache
    from functools import lru_cache
    
    @lru_cache(maxsize=1000)
    def process_span_cached(self, span_key: str):
        # Cached processing
        pass
```

**B. Inefficient Span Processing**:
```python
# Profile span processing
import cProfile
import pstats

def profile_agent():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Run agent for sample period
    agent.run_for_duration(60)  # 60 seconds
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)
```

**C. File I/O Bottlenecks**:
```python
# Use more efficient file watching
import asyncio
from watchdog.observers import Observer

class AsyncSpanWatcher:
    async def watch_spans(self):
        # Async file monitoring
        async for span in self.watch_file_async():
            await self.process_span_async(span)
```

### 5. Coordination Flow Issues

**Symptoms**:
- Agents not coordinating properly
- Commands not triggering downstream agents
- Workflow loops or dead ends

**Diagnosis**:
```bash
# Trace coordination flow
dsl swarm monitor --follow --filter "coordination"

# Check command generation
grep "NextCommand" ~/.swarm_coordination/agent.log

# Verify agent listening
dsl swarm validate --agents
```

**Root Causes & Solutions**:

**A. Command Format Issues**:
```python
# Verify NextCommand format
return NextCommand(
    fq_name="swarmsh.scrum.sprint-planning",  # ✅ Valid format
    args=["--sprint-number", "42"],
    description="Trigger sprint planning"
)

# ❌ Invalid formats:
# return "start scrum"  # String instead of NextCommand
# return NextCommand("scrum.plan")  # Missing fq_name format
```

**B. Agent Registration Problems**:
```python
# Verify TRIGGER_MAP completeness
TRIGGER_MAP = {
    "swarmsh.roberts.open": "handle_open",
    "swarmsh.roberts.vote": "handle_vote", 
    "swarmsh.roberts.close": "handle_close"
    # Missing trigger mappings cause ignored spans
}
```

**C. Circular Dependencies**:
```python
# Check for coordination loops
def detect_coordination_loops():
    coordination_graph = build_coordination_graph()
    cycles = find_cycles(coordination_graph)
    if cycles:
        print(f"Detected coordination loops: {cycles}")
```

### 6. OpenTelemetry Integration Issues

**Symptoms**:
- Traces not appearing in collector
- Export failures
- Missing span attributes

**Diagnosis**:
```bash
# Test OTLP endpoint
curl -v -X POST $OTEL_EXPORTER_OTLP_ENDPOINT/v1/traces \
  -H "Content-Type: application/json" \
  -d '{"resourceSpans":[]}'

# Check exporter configuration
env | grep OTEL_

# Validate span format
python -c "
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
exporter = OTLPSpanExporter()
print('OTLP Exporter OK')
"
```

**Root Causes & Solutions**:

**A. Endpoint Configuration**:
```bash
# Correct OTLP endpoint format
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318  # HTTP
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317  # gRPC

# Test connectivity
telnet localhost 4318
```

**B. Authentication Issues**:
```bash
# Configure headers for authenticated endpoints
export OTEL_EXPORTER_OTLP_HEADERS="x-honeycomb-team=YOUR_API_KEY"
export OTEL_EXPORTER_OTLP_HEADERS="authorization=Bearer YOUR_TOKEN"
```

**C. Span Export Failures**:
```python
# Add export error handling
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

class RobustSpanExporter:
    def __init__(self):
        self.exporter = OTLPSpanExporter()
        
    def export_span(self, span):
        try:
            result = self.exporter.export([span])
            if result != SpanExportResult.SUCCESS:
                self.logger.warning(f"Span export failed: {result}")
        except Exception as e:
            self.logger.error(f"Export error: {e}")
            # Fallback to local storage
            self.store_span_locally(span)
```

## Debugging Techniques

### 1. Enable Debug Logging

```bash
# Environment variables
export SWARM_DEBUG=1
export SWARM_LOG_LEVEL=DEBUG
export PYTHONPATH="${PYTHONPATH}:src"

# Application logging
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from dslmodel.agents.examples.roberts_agent import RobertsAgent
agent = RobertsAgent()
agent.run()
"
```

### 2. Trace Coordination Flow

```python
# Add detailed tracing to agents
from opentelemetry import trace

class DebuggableSwarmAgent(SwarmAgent):
    def forward(self, trace_data: str) -> Optional[NextCommand]:
        tracer = trace.get_tracer(__name__)
        
        with tracer.start_as_current_span("agent.forward") as span:
            span.set_attribute("agent.name", self.__class__.__name__)
            span.set_attribute("trace_data.length", len(trace_data))
            
            try:
                parsed_span = self.parse_span(trace_data)
                span.set_attribute("span.parsed", parsed_span is not None)
                
                if parsed_span:
                    span.set_attribute("span.name", parsed_span.name)
                    result = self._process_span(parsed_span)
                    span.set_attribute("result.type", type(result).__name__)
                    return result
                    
            except Exception as e:
                span.set_attribute("error.type", type(e).__name__)
                span.set_attribute("error.message", str(e))
                raise
                
            return None
```

### 3. Interactive Debugging

```python
# Debug agent behavior interactively
import pdb
from dslmodel.agents.examples.roberts_agent import RobertsAgent

def debug_agent():
    agent = RobertsAgent()
    
    # Set breakpoint before processing
    pdb.set_trace()
    
    # Test span
    test_span = {
        "name": "swarmsh.roberts.open",
        "attributes": {"motion_id": "debug_test"}
    }
    
    result = agent.forward(json.dumps(test_span))
    print(f"Result: {result}")
    print(f"State: {agent.current_state}")

if __name__ == "__main__":
    debug_agent()
```

### 4. Mock External Dependencies

```python
# Mock external systems for testing
from unittest.mock import Mock, patch

class TestableDevOpsAgent(DevOpsAgent):
    def __init__(self, mock_external_calls=False):
        super().__init__()
        if mock_external_calls:
            self.setup_mocks()
    
    def setup_mocks(self):
        # Mock Jira API
        self.jira_client = Mock()
        self.jira_client.create_issue.return_value = {"key": "TEST-123"}
        
        # Mock Slack API
        self.slack_client = Mock()
        self.slack_client.chat_postMessage.return_value = {"ok": True}

# Test with mocks
agent = TestableDevOpsAgent(mock_external_calls=True)
```

## Monitoring and Alerting

### 1. Health Check Endpoints

```python
# Add health endpoints to agents
from flask import Flask, jsonify

class MonitorableSwarmAgent(SwarmAgent):
    def __init__(self):
        super().__init__()
        self.health_app = Flask(__name__)
        self.setup_health_endpoints()
    
    def setup_health_endpoints(self):
        @self.health_app.route('/health')
        def health():
            return jsonify({
                "status": "healthy" if self.is_healthy() else "unhealthy",
                "state": self.current_state.value,
                "uptime": time.time() - self.start_time,
                "spans_processed": self.spans_processed_count
            })
        
        @self.health_app.route('/metrics')
        def metrics():
            return jsonify({
                "spans_processed_total": self.spans_processed_count,
                "state_transitions_total": self.transitions_count,
                "errors_total": self.error_count,
                "processing_time_avg": self.avg_processing_time
            })
    
    def is_healthy(self) -> bool:
        # Check if agent is functioning properly
        return (
            self.error_rate < 0.1 and  # <10% error rate
            self.last_activity_time > (time.time() - 300)  # Active in last 5 min
        )
```

### 2. Automated Monitoring

```bash
#!/bin/bash
# monitor-agents.sh - Automated agent monitoring script

check_agent_health() {
    local agent_name=$1
    local health_url="http://localhost:8080/health"
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$health_url")
    
    if [ "$response" = "200" ]; then
        echo "✅ $agent_name: Healthy"
        return 0
    else
        echo "❌ $agent_name: Unhealthy (HTTP $response)"
        return 1
    fi
}

# Check all agents
agents=("roberts" "scrum" "lean")
unhealthy_count=0

for agent in "${agents[@]}"; do
    if ! check_agent_health "$agent"; then
        ((unhealthy_count++))
    fi
done

if [ $unhealthy_count -gt 0 ]; then
    echo "🚨 $unhealthy_count agents are unhealthy"
    # Send alert
    curl -X POST "$SLACK_WEBHOOK" -d "{\"text\": \"SwarmAgent alert: $unhealthy_count agents unhealthy\"}"
    exit 1
fi

echo "🎉 All agents healthy"
```

### 3. Log Analysis

```python
# Automated log analysis for issues
import re
from collections import Counter

def analyze_agent_logs(log_file_path: str):
    error_patterns = {
        'parsing_errors': r'Span parsing failed',
        'state_errors': r'Invalid state transition',
        'network_errors': r'Connection.*failed',
        'timeout_errors': r'Timeout.*expired'
    }
    
    error_counts = Counter()
    
    with open(log_file_path, 'r') as f:
        for line in f:
            for error_type, pattern in error_patterns.items():
                if re.search(pattern, line):
                    error_counts[error_type] += 1
    
    print("Error Analysis:")
    for error_type, count in error_counts.items():
        if count > 0:
            print(f"  {error_type}: {count} occurrences")
    
    return error_counts

# Generate recommendations
def get_recommendations(error_counts):
    recommendations = []
    
    if error_counts['parsing_errors'] > 10:
        recommendations.append("High span parsing errors - check JSONL format")
    
    if error_counts['state_errors'] > 5:
        recommendations.append("State transition issues - review FSM logic")
    
    if error_counts['network_errors'] > 3:
        recommendations.append("Network connectivity issues - check OTEL endpoint")
    
    return recommendations
```

## Recovery Procedures

### 1. Agent Recovery

```bash
#!/bin/bash
# recover-agents.sh - Automated agent recovery

recover_agent() {
    local agent_name=$1
    
    echo "Recovering $agent_name agent..."
    
    # 1. Stop existing instances
    pkill -f "dsl swarm start $agent_name"
    
    # 2. Clean up coordination data if corrupted
    if [ "$CLEAN_DATA" = "true" ]; then
        echo "Cleaning coordination data..."
        rm -f ~/.swarm_coordination/agent_state_${agent_name}.json
    fi
    
    # 3. Restart agent
    echo "Starting $agent_name agent..."
    dsl swarm start "$agent_name" --background
    
    # 4. Verify recovery
    sleep 5
    if check_agent_health "$agent_name"; then
        echo "✅ $agent_name recovered successfully"
        return 0
    else
        echo "❌ $agent_name recovery failed"
        return 1
    fi
}

# Recover all agents
for agent in roberts scrum lean; do
    recover_agent "$agent"
done
```

### 2. Data Recovery

```bash
# Restore coordination data from backup
restore_coordination_data() {
    local backup_file=$1
    local coord_dir="$HOME/.swarm_coordination"
    
    echo "Restoring coordination data from $backup_file..."
    
    # Backup current state
    mv "$coord_dir" "${coord_dir}.backup.$(date +%s)"
    
    # Restore from backup
    mkdir -p "$coord_dir"
    tar -xzf "$backup_file" -C "$coord_dir"
    
    # Verify restoration
    if [ -f "$coord_dir/telemetry_spans.jsonl" ]; then
        echo "✅ Coordination data restored successfully"
        return 0
    else
        echo "❌ Data restoration failed"
        return 1
    fi
}
```

### 3. Emergency Procedures

```bash
# Emergency stop all agents
emergency_stop() {
    echo "🚨 Emergency stop initiated"
    
    # Stop all SwarmAgent processes
    pkill -f "dsl swarm start"
    
    # Stop coordination monitoring
    pkill -f "dsl swarm monitor"
    
    echo "✅ All SwarmAgent processes stopped"
}

# Emergency reset
emergency_reset() {
    echo "🚨 Emergency reset initiated"
    
    # Stop all processes
    emergency_stop
    
    # Clear coordination data
    rm -rf ~/.swarm_coordination/telemetry_spans.jsonl
    rm -rf ~/.swarm_coordination/agent_state_*.json
    
    # Restart with clean state
    mkdir -p ~/.swarm_coordination
    
    echo "✅ Emergency reset completed"
    echo "Run 'dsl swarm start <agent>' to restart agents"
}
```

## Getting Support

### 1. Information to Collect

**Before requesting support, collect**:
```bash
# System information
uname -a
python --version
pip list | grep dslmodel

# Configuration
env | grep SWARM_
cat ~/.swarm_coordination/config.json

# Recent logs
tail -100 ~/.swarm_coordination/agent.log

# Recent spans
tail -20 ~/.swarm_coordination/telemetry_spans.jsonl

# System status
dsl swarm status
dsl swarm validate --report
```

### 2. Support Channels

- **GitHub Issues**: [dslmodel/issues](https://github.com/seanchatmangpt/dslmodel/issues)
- **Documentation**: [docs/](.)
- **CLI Help**: `dsl swarm --help`

### 3. Issue Templates

**Bug Report Template**:
```
## Bug Description
Brief description of the issue

## Environment
- OS: 
- Python version:
- dslmodel version:
- Installation method:

## Steps to Reproduce
1. 
2. 
3. 

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Logs and Traces
Paste relevant logs and OpenTelemetry traces

## Additional Context
Any other relevant information
```

## Next Steps

- **[Performance Validation](PERFORMANCE_VALIDATION.md)** - Validate fixes work
- **[Production Deployment](PRODUCTION_DEPLOYMENT.md)** - Deploy with monitoring
- **[Custom Agents](CUSTOM_AGENTS.md)** - Build robust custom agents