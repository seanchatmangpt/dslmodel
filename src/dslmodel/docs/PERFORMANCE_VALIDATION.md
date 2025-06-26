# Performance Validation

## Overview

Following CLAUDE.md principles, all SwarmAgent performance claims must be validated through **OpenTelemetry traces**, **benchmarks**, and **metrics**. This guide provides comprehensive validation methods.

## Validation Principles

### Never Trust Claims - Only Verify
- **❌ Don't**: Trust performance assertions without measurement
- **✅ Do**: Measure via OpenTelemetry traces and benchmarks
- **✅ Do**: Report actual metrics from running systems
- **✅ Do**: Validate with real workloads under load

### OpenTelemetry First
All performance validation uses OpenTelemetry instrumentation:
- **Span timing** for operation latency
- **Metrics** for throughput and resource usage  
- **Traces** for end-to-end coordination timing
- **Logs** for error analysis

## Validation Methods

### 1. Basic Performance Test

**Run built-in performance validation**:
```bash
dsl swarm validate --performance
```

Expected output:
```
🔍 SwarmAgent Performance Validation

⏱️  Span Processing Latency
   • Average: 8.3ms (target: <10ms) ✅
   • 95th percentile: 15.2ms
   • 99th percentile: 28.1ms

🔄 State Transition Speed  
   • Average: 3.7ms (target: <5ms) ✅
   • Fastest: 1.2ms
   • Slowest: 12.8ms

📊 Throughput
   • Spans/second: 1,247 (target: >1000) ✅
   • Coordination cycles/min: 847

💾 Memory Usage
   • Per agent: 42MB (target: <50MB) ✅
   • Peak usage: 156MB (3 agents)

🎯 Coordination Latency
   • End-to-end: 87ms (target: <100ms) ✅
   • Cross-agent handoff: 23ms
```

### 2. Load Testing

**Generate sustained load**:
```bash
# Generate 1000 spans with 10 concurrent agents
python -c "
from dslmodel.agents.examples.load_test import LoadTester
tester = LoadTester(agents=10, spans=1000, duration=60)
results = tester.run()
print(f'Throughput: {results.spans_per_second:.1f} spans/sec')
print(f'Latency P95: {results.latency_p95:.1f}ms')
print(f'Memory peak: {results.memory_peak_mb:.1f}MB')
"
```

**With OTEL trace validation**:
```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
dsl swarm demo full --load-test --agents 5 --duration 300
```

### 3. Benchmark Suite

**Run comprehensive benchmarks**:
```bash
# Full benchmark suite
python -m dslmodel.agents.examples.benchmark_suite

# Specific benchmarks
python -m dslmodel.agents.examples.benchmark_suite --test span_processing
python -m dslmodel.agents.examples.benchmark_suite --test state_transitions  
python -m dslmodel.agents.examples.benchmark_suite --test coordination_flow
```

### 4. Real Workload Validation

**Governance workflow timing**:
```bash
# Time complete governance → delivery cycle
time_start=$(date +%s%N)

dsl swarm emit 'swarmsh.roberts.open' --attrs '{"motion_id": "perf_test", "meeting_id": "validation"}'
dsl swarm emit 'swarmsh.roberts.vote' --attrs '{"motion_id": "perf_test", "voting_method": "ballot"}'  
dsl swarm emit 'swarmsh.roberts.close' --attrs '{"motion_id": "perf_test", "vote_result": "passed"}'

# Wait for scrum agent response
sleep 1

time_end=$(date +%s%N)
duration_ms=$(( (time_end - time_start) / 1000000 ))
echo "Governance cycle: ${duration_ms}ms"
```

## OpenTelemetry Validation

### Span Analysis

**Extract span timing from traces**:
```bash
# Generate traced workflow
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
dsl swarm demo full

# Query Jaeger for span metrics
curl -s "http://localhost:16686/api/traces?service=swarm-agent&limit=100" | jq '
  .data[].spans[] | 
  select(.operationName | startswith("swarm.agent")) |
  {
    operation: .operationName,
    duration_ms: (.duration / 1000),
    agent: .tags[] | select(.key == "swarm.agent.name") | .value
  }
' | jq -s 'group_by(.operation) | map({
  operation: .[0].operation,
  count: length,
  avg_duration_ms: (map(.duration_ms) | add / length),
  max_duration_ms: (map(.duration_ms) | max)
})'
```

### Custom Instrumentation

**Add performance spans to agent code**:
```python
from opentelemetry import trace
tracer = trace.get_tracer(__name__)

@trigger(source=RorState.IDLE, dest=RorState.MOTION_OPEN)
def open_motion(self, span: SpanData) -> Optional[NextCommand]:
    with tracer.start_as_current_span("roberts.open_motion") as perf_span:
        perf_span.set_attribute("motion_id", span.attributes.get("motion_id"))
        
        start_time = time.time()
        result = self._process_motion(span)
        processing_time = (time.time() - start_time) * 1000
        
        perf_span.set_attribute("processing_time_ms", processing_time)
        perf_span.set_attribute("result_type", type(result).__name__)
        
        return result
```

### Metrics Collection

**Enable OpenTelemetry metrics**:
```python
from opentelemetry.metrics import get_meter
meter = get_meter(__name__)

# Counter for coordination events
coordination_counter = meter.create_counter(
    "swarm.coordination.events",
    description="Number of coordination events processed"
)

# Histogram for processing latency
processing_histogram = meter.create_histogram(
    "swarm.processing.duration",
    description="Time spent processing coordination events",
    unit="ms"
)

# Gauge for active agents
active_agents_gauge = meter.create_gauge(
    "swarm.agents.active",
    description="Number of active agents"
)
```

## Benchmark Scenarios

### 1. Single Agent Performance

**Test individual agent performance**:
```python
import time
from dslmodel.agents.examples.roberts_agent import RobertsAgent

def benchmark_single_agent():
    agent = RobertsAgent()
    spans = generate_test_spans(1000)
    
    start_time = time.time()
    for span in spans:
        result = agent.forward(span)
    end_time = time.time()
    
    total_time = end_time - start_time
    spans_per_second = len(spans) / total_time
    avg_latency = (total_time / len(spans)) * 1000
    
    print(f"Single agent throughput: {spans_per_second:.1f} spans/sec")
    print(f"Average latency: {avg_latency:.1f}ms")
```

### 2. Multi-Agent Coordination

**Test agent-to-agent coordination timing**:
```python
def benchmark_coordination():
    # Start all agents
    roberts = RobertsAgent()
    scrum = ScrumAgent() 
    lean = LeanAgent()
    
    # Measure governance → delivery handoff
    start_time = time.time()
    
    # Roberts processes vote
    vote_span = create_span("swarmsh.roberts.vote", {"vote_result": "passed"})
    roberts_result = roberts.forward(vote_span)
    
    # Scrum receives triggered command  
    if roberts_result:
        scrum_span = command_to_span(roberts_result)
        scrum_result = scrum.forward(scrum_span)
    
    handoff_time = (time.time() - start_time) * 1000
    print(f"Governance→Delivery handoff: {handoff_time:.1f}ms")
```

### 3. Stress Testing

**High-throughput stress test**:
```python
import concurrent.futures
import threading

def stress_test(num_agents=10, spans_per_agent=100, duration_seconds=60):
    agents = [create_random_agent() for _ in range(num_agents)]
    
    results = []
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_agents) as executor:
        futures = []
        
        for agent in agents:
            future = executor.submit(run_agent_load, agent, spans_per_agent, duration_seconds)
            futures.append(future)
        
        for future in concurrent.futures.as_completed(futures):
            agent_results = future.result()
            results.append(agent_results)
    
    total_time = time.time() - start_time
    total_spans = sum(r.spans_processed for r in results)
    total_throughput = total_spans / total_time
    
    print(f"Stress test results:")
    print(f"  Agents: {num_agents}")
    print(f"  Total spans: {total_spans}")
    print(f"  Duration: {total_time:.1f}s")
    print(f"  Throughput: {total_throughput:.1f} spans/sec")
    print(f"  Memory peak: {get_memory_peak():.1f}MB")
```

## Continuous Validation

### Automated Performance Testing

**GitHub Actions workflow** (`.github/workflows/performance.yml`):
```yaml
name: Performance Validation
on: [push, pull_request]

jobs:
  performance:
    runs-on: ubuntu-latest
    services:
      jaeger:
        image: jaegertracing/all-in-one:latest
        ports:
          - 14268:14268
          - 16686:16686
          
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.12'
        
    - name: Install dependencies
      run: pip install .[otel,test]
      
    - name: Run performance benchmarks
      env:
        OTEL_EXPORTER_OTLP_ENDPOINT: http://localhost:14268
      run: |
        python -m dslmodel.agents.examples.benchmark_suite --ci
        dsl swarm validate --performance --ci
        
    - name: Performance regression check
      run: |
        python scripts/check_performance_regression.py \
          --baseline benchmarks/baseline.json \
          --current benchmarks/current.json \
          --tolerance 10
```

### Performance Monitoring

**Production performance dashboard**:
```python
# Grafana dashboard query examples
SPAN_PROCESSING_LATENCY = """
histogram_quantile(0.95, 
  rate(swarm_processing_duration_bucket[5m])
)
"""

COORDINATION_THROUGHPUT = """
rate(swarm_coordination_events_total[1m])
"""

AGENT_MEMORY_USAGE = """
swarm_agents_memory_bytes / 1024 / 1024
"""

ERROR_RATE = """
rate(swarm_coordination_errors_total[5m]) / 
rate(swarm_coordination_events_total[5m])
"""
```

## Performance Targets

### Latency Targets

| Operation | Target | Measurement |
|-----------|--------|-------------|
| Span processing | <10ms | OTEL span duration |
| State transition | <5ms | FSM transition time |
| Command emission | <2ms | NextCommand creation |
| Cross-agent handoff | <50ms | End-to-end coordination |

### Throughput Targets  

| Metric | Target | Measurement |
|--------|--------|-------------|
| Spans per second | >1000 | Total system throughput |
| Coordination cycles/min | >500 | Complete workflows |
| Concurrent agents | >20 | Without performance degradation |

### Resource Targets

| Resource | Target | Measurement |
|----------|--------|-------------|
| Memory per agent | <50MB | RSS memory usage |
| CPU per agent | <5% | CPU utilization |
| Storage growth | <1MB/hour | Coordination logs |

## Validation Reports

### Generate Performance Report

```bash
# Comprehensive performance report
dsl swarm validate --performance --report --output performance_report.json

# Convert to human-readable format
python -c "
import json
with open('performance_report.json') as f:
    data = json.load(f)
    
print('SwarmAgent Performance Report')
print('=' * 30)
print(f'Test timestamp: {data[\"timestamp\"]}')
print(f'Test duration: {data[\"duration_seconds\"]}s')
print()
print('Latency Results:')
for metric, value in data['latency'].items():
    target = value['target']
    actual = value['actual']
    status = '✅' if actual <= target else '❌'
    print(f'  {metric}: {actual:.1f}ms (target: <{target}ms) {status}')
print()
print('Throughput Results:')
for metric, value in data['throughput'].items():
    target = value['target']
    actual = value['actual']
    status = '✅' if actual >= target else '❌'
    print(f'  {metric}: {actual:.1f} (target: >{target}) {status}')
"
```

### Trace Analysis

**Extract coordination patterns from traces**:
```bash
# Get coordination flow timing from Jaeger
curl -s "http://localhost:16686/api/traces?service=swarm-agent&operation=governance.cycle" | \
jq '.data[].spans | map(select(.operationName | contains("coordination"))) | 
    group_by(.operationName) | 
    map({
      operation: .[0].operationName,
      avg_duration_ms: (map(.duration) | add / length / 1000),
      count: length
    })'
```

## Next Steps

- **[Production Deployment](PRODUCTION_DEPLOYMENT.md)** - Deploy with monitoring
- **[Troubleshooting](TROUBLESHOOTING.md)** - Debug performance issues
- **[Custom Agents](CUSTOM_AGENTS.md)** - Optimize new agent types