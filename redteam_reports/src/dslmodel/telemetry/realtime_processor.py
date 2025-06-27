"""
Real-time Telemetry Processing Pipeline
Processes live OTEL spans and metrics for autonomous decision making.
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque, defaultdict
from pathlib import Path
import threading
from queue import Queue, Empty
from loguru import logger

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanExporter
from opentelemetry.trace import Status


@dataclass
class TelemetryEvent:
    """Represents a processed telemetry event."""
    span_name: str
    attributes: Dict[str, Any]
    timestamp: datetime
    trace_id: str
    duration_ms: Optional[float] = None
    status: str = "OK"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "span_name": self.span_name,
            "attributes": self.attributes,
            "timestamp": self.timestamp.isoformat(),
            "trace_id": self.trace_id,
            "duration_ms": self.duration_ms,
            "status": self.status
        }


@dataclass 
class TelemetryMetrics:
    """Aggregated telemetry metrics over time windows."""
    span_counts: Dict[str, int] = field(default_factory=dict)
    avg_durations: Dict[str, float] = field(default_factory=dict)
    error_rates: Dict[str, float] = field(default_factory=dict)
    throughput_per_second: float = 0.0
    health_indicators: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class TelemetryStreamProcessor:
    """Processes telemetry streams in real-time."""
    
    def __init__(self, window_size_seconds: int = 60):
        """Initialize the processor with configurable time windows."""
        self.window_size = timedelta(seconds=window_size_seconds)
        self.event_buffer = deque(maxlen=10000)  # Circular buffer
        self.metrics_cache = {}
        self.subscribers: List[Callable[[TelemetryEvent], None]] = []
        self.metric_subscribers: List[Callable[[TelemetryMetrics], None]] = []
        self.running = False
        self.processor_thread = None
        self._lock = threading.RLock()
        
        # Pattern detection
        self.pattern_detectors = {
            "error_spike": self._detect_error_spike,
            "latency_increase": self._detect_latency_increase,
            "throughput_drop": self._detect_throughput_drop,
            "cascade_failure": self._detect_cascade_failure
        }
        
        logger.info(f"Telemetry processor initialized with {window_size_seconds}s windows")
    
    def subscribe_to_events(self, callback: Callable[[TelemetryEvent], None]):
        """Subscribe to individual telemetry events."""
        self.subscribers.append(callback)
        logger.debug(f"Added event subscriber: {callback.__name__}")
    
    def subscribe_to_metrics(self, callback: Callable[[TelemetryMetrics], None]):
        """Subscribe to aggregated metrics."""
        self.metric_subscribers.append(callback)
        logger.debug(f"Added metrics subscriber: {callback.__name__}")
    
    def ingest_span(self, span_data: Dict[str, Any]):
        """Ingest a new telemetry span."""
        try:
            event = TelemetryEvent(
                span_name=span_data.get("name", "unknown"),
                attributes=span_data.get("attributes", {}),
                timestamp=datetime.fromisoformat(span_data.get("timestamp", datetime.now().isoformat())),
                trace_id=span_data.get("trace_id", "unknown"),
                duration_ms=span_data.get("duration_ms"),
                status=span_data.get("status", "OK")
            )
            
            with self._lock:
                self.event_buffer.append(event)
            
            # Notify event subscribers
            for subscriber in self.subscribers:
                try:
                    subscriber(event)
                except Exception as e:
                    logger.error(f"Event subscriber error: {e}")
            
        except Exception as e:
            logger.error(f"Failed to ingest span: {e}")
    
    def start_processing(self):
        """Start the real-time processing loop."""
        if self.running:
            return
        
        self.running = True
        self.processor_thread = threading.Thread(target=self._processing_loop, daemon=True)
        self.processor_thread.start()
        logger.info("Started real-time telemetry processing")
    
    def stop_processing(self):
        """Stop the processing loop."""
        self.running = False
        if self.processor_thread:
            self.processor_thread.join(timeout=5.0)
        logger.info("Stopped telemetry processing")
    
    def _processing_loop(self):
        """Main processing loop that runs in background thread."""
        while self.running:
            try:
                # Generate metrics every 10 seconds
                metrics = self._compute_metrics()
                
                # Detect patterns
                patterns = self._detect_patterns(metrics)
                if patterns:
                    logger.warning(f"Detected patterns: {list(patterns.keys())}")
                    metrics.health_indicators.update(patterns)
                
                # Notify metric subscribers
                for subscriber in self.metric_subscribers:
                    try:
                        subscriber(metrics)
                    except Exception as e:
                        logger.error(f"Metrics subscriber error: {e}")
                
                # Cache metrics
                self.metrics_cache[datetime.now()] = metrics
                
                # Clean old cache entries
                cutoff = datetime.now() - timedelta(hours=1)
                self.metrics_cache = {
                    ts: m for ts, m in self.metrics_cache.items() 
                    if ts > cutoff
                }
                
            except Exception as e:
                logger.error(f"Processing loop error: {e}")
            
            time.sleep(10)  # Process every 10 seconds
    
    def _compute_metrics(self) -> TelemetryMetrics:
        """Compute aggregated metrics from recent events."""
        with self._lock:
            # Get events from current window
            cutoff = datetime.now() - self.window_size
            recent_events = [e for e in self.event_buffer if e.timestamp > cutoff]
        
        if not recent_events:
            return TelemetryMetrics()
        
        # Aggregate by span name
        span_groups = defaultdict(list)
        for event in recent_events:
            span_groups[event.span_name].append(event)
        
        metrics = TelemetryMetrics()
        
        # Compute per-span metrics
        for span_name, events in span_groups.items():
            metrics.span_counts[span_name] = len(events)
            
            # Average duration
            durations = [e.duration_ms for e in events if e.duration_ms is not None]
            if durations:
                metrics.avg_durations[span_name] = sum(durations) / len(durations)
            
            # Error rate
            errors = len([e for e in events if e.status != "OK"])
            metrics.error_rates[span_name] = errors / len(events) if events else 0.0
        
        # Overall throughput
        window_seconds = self.window_size.total_seconds()
        metrics.throughput_per_second = len(recent_events) / window_seconds
        
        return metrics
    
    def _detect_patterns(self, current_metrics: TelemetryMetrics) -> Dict[str, float]:
        """Detect anomaly patterns in telemetry data."""
        patterns = {}
        
        for pattern_name, detector in self.pattern_detectors.items():
            try:
                score = detector(current_metrics)
                if score > 0.5:  # Threshold for pattern detection
                    patterns[pattern_name] = score
            except Exception as e:
                logger.error(f"Pattern detection error for {pattern_name}: {e}")
        
        return patterns
    
    def _detect_error_spike(self, metrics: TelemetryMetrics) -> float:
        """Detect sudden increase in error rates."""
        if not metrics.error_rates:
            return 0.0
        
        avg_error_rate = sum(metrics.error_rates.values()) / len(metrics.error_rates)
        return min(avg_error_rate * 10, 1.0)  # Scale to 0-1
    
    def _detect_latency_increase(self, metrics: TelemetryMetrics) -> float:
        """Detect latency increases."""
        if not metrics.avg_durations:
            return 0.0
        
        # Compare with historical baseline (simplified)
        recent_avg = sum(metrics.avg_durations.values()) / len(metrics.avg_durations)
        baseline = 1000.0  # ms - should be computed from historical data
        
        if recent_avg > baseline * 1.5:  # 50% increase
            return min((recent_avg - baseline) / baseline, 1.0)
        
        return 0.0
    
    def _detect_throughput_drop(self, metrics: TelemetryMetrics) -> float:
        """Detect throughput drops."""
        baseline_throughput = 10.0  # req/sec - should be computed from historical
        
        if metrics.throughput_per_second < baseline_throughput * 0.7:  # 30% drop
            return min((baseline_throughput - metrics.throughput_per_second) / baseline_throughput, 1.0)
        
        return 0.0
    
    def _detect_cascade_failure(self, metrics: TelemetryMetrics) -> float:
        """Detect potential cascade failures."""
        if not metrics.error_rates:
            return 0.0
        
        # Look for multiple services with high error rates
        high_error_services = sum(1 for rate in metrics.error_rates.values() if rate > 0.1)
        total_services = len(metrics.error_rates)
        
        if total_services > 0:
            cascade_score = high_error_services / total_services
            return cascade_score if cascade_score > 0.3 else 0.0
        
        return 0.0
    
    def get_current_metrics(self) -> Optional[TelemetryMetrics]:
        """Get the most recent metrics."""
        if not self.metrics_cache:
            return self._compute_metrics()
        
        latest_time = max(self.metrics_cache.keys())
        return self.metrics_cache[latest_time]
    
    def get_health_score(self) -> float:
        """Compute overall system health score from telemetry."""
        metrics = self.get_current_metrics()
        if not metrics:
            return 0.5  # Neutral score when no data
        
        # Compute health based on multiple factors
        error_penalty = sum(metrics.error_rates.values()) / max(len(metrics.error_rates), 1)
        throughput_score = min(metrics.throughput_per_second / 10.0, 1.0)  # Normalize to baseline
        pattern_penalty = sum(metrics.health_indicators.values()) / max(len(metrics.health_indicators), 1)
        
        health_score = (throughput_score * 0.4) + ((1.0 - error_penalty) * 0.4) + ((1.0 - pattern_penalty) * 0.2)
        return max(0.0, min(1.0, health_score))


class TelemetryFileIngester:
    """Ingests telemetry from coordination files."""
    
    def __init__(self, processor: TelemetryStreamProcessor, coordination_dir: Path):
        self.processor = processor
        self.coordination_dir = coordination_dir
        self.last_check = datetime.now()
        self.running = False
        self.ingester_thread = None
    
    def start_ingesting(self):
        """Start ingesting telemetry files."""
        if self.running:
            return
        
        self.running = True
        self.ingester_thread = threading.Thread(target=self._ingestion_loop, daemon=True)
        self.ingester_thread.start()
        logger.info(f"Started telemetry ingestion from {self.coordination_dir}")
    
    def stop_ingesting(self):
        """Stop ingesting."""
        self.running = False
        if self.ingester_thread:
            self.ingester_thread.join(timeout=5.0)
        logger.info("Stopped telemetry ingestion")
    
    def _ingestion_loop(self):
        """Main ingestion loop."""
        while self.running:
            try:
                self._process_telemetry_files()
            except Exception as e:
                logger.error(f"Telemetry ingestion error: {e}")
            
            time.sleep(5)  # Check every 5 seconds
    
    def _process_telemetry_files(self):
        """Process new telemetry files."""
        if not self.coordination_dir.exists():
            return
        
        # Look for telemetry files
        for telemetry_file in self.coordination_dir.glob("telemetry_*.json"):
            try:
                # Check if file is newer than last check
                if telemetry_file.stat().st_mtime > self.last_check.timestamp():
                    with open(telemetry_file) as f:
                        data = json.load(f)
                    
                    # Convert to span format and ingest
                    span_data = {
                        "name": "swarmsh.coordination.telemetry",
                        "attributes": data.get("metrics", {}),
                        "timestamp": data.get("timestamp", datetime.now().isoformat()),
                        "trace_id": data.get("id", "unknown"),
                        "status": "OK"
                    }
                    
                    self.processor.ingest_span(span_data)
                    
            except Exception as e:
                logger.error(f"Error processing {telemetry_file}: {e}")
        
        self.last_check = datetime.now()


# Singleton processor instance
_global_processor: Optional[TelemetryStreamProcessor] = None


def get_telemetry_processor() -> TelemetryStreamProcessor:
    """Get the global telemetry processor instance."""
    global _global_processor
    if _global_processor is None:
        _global_processor = TelemetryStreamProcessor()
        _global_processor.start_processing()
    return _global_processor


def setup_telemetry_ingestion(coordination_dir: Path) -> TelemetryFileIngester:
    """Setup telemetry ingestion from coordination directory."""
    processor = get_telemetry_processor()
    ingester = TelemetryFileIngester(processor, coordination_dir)
    ingester.start_ingesting()
    return ingester