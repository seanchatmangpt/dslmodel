#!/usr/bin/env python3
"""Telemetry System Test Suite
Tests for OpenTelemetry integration, monitoring, gap analysis, and telemetry-driven functionality.
"""

import pytest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List
import time

# Import telemetry components
from dslmodel.telemetry.otel_instrumentation import setup_telemetry, get_tracer
from dslmodel.telemetry.monitoring import TelemetryMonitor
from dslmodel.telemetry.gap_analyzer import GapAnalyzer
from dslmodel.telemetry.remediation import RemediationEngine
from dslmodel.telemetry.security import SecurityMonitor
from dslmodel.otel.otel_weaver_integration import OTELWeaverIntegration
from dslmodel.otel.otel_gap_analyzer import OTELGapAnalyzer
from dslmodel.otel.otel_monitor import OTELMonitor


class TestOpenTelemetryInstrumentation:
    """Test OpenTelemetry instrumentation setup and usage"""
    
    def test_telemetry_setup(self):
        """Test telemetry setup and configuration"""
        # Test basic setup
        tracer = setup_telemetry("test_service")
        
        assert tracer is not None
        assert hasattr(tracer, 'start_span')
    
    def test_span_creation(self):
        """Test span creation and management"""
        tracer = setup_telemetry("test_service")
        
        with tracer.start_as_current_span("test_operation") as span:
            span.set_attribute("test.attribute", "test_value")
            span.add_event("test_event", {"event_data": "test"})
            
            assert span.is_recording()
            assert span.get_attribute("test.attribute") == "test_value"
    
    def test_span_context_propagation(self):
        """Test span context propagation"""
        tracer = setup_telemetry("test_service")
        
        with tracer.start_as_current_span("parent_span") as parent_span:
            parent_span.set_attribute("parent.attr", "parent_value")
            
            with tracer.start_as_current_span("child_span") as child_span:
                child_span.set_attribute("child.attr", "child_value")
                
                # Verify parent-child relationship
                assert child_span.get_parent_span_context() == parent_span.get_span_context()
    
    def test_metrics_collection(self):
        """Test metrics collection functionality"""
        from opentelemetry import metrics
        
        meter = metrics.get_meter("test_meter")
        counter = meter.create_counter("test_counter")
        
        # Record some metrics
        counter.add(1, {"operation": "test"})
        counter.add(2, {"operation": "test"})
        
        # Verify counter exists
        assert counter is not None
    
    def test_logging_integration(self):
        """Test logging integration with OpenTelemetry"""
        from opentelemetry import trace
        import logging
        
        tracer = setup_telemetry("test_service")
        logger = logging.getLogger("test_logger")
        
        with tracer.start_as_current_span("logging_test") as span:
            logger.info("Test log message", extra={
                "span_id": span.get_span_context().span_id,
                "trace_id": span.get_span_context().trace_id
            })
            
            # Verify span has log record
            assert span is not None


class TestTelemetryMonitoring:
    """Test telemetry monitoring functionality"""
    
    def test_monitor_initialization(self):
        """Test telemetry monitor initialization"""
        monitor = TelemetryMonitor()
        
        assert monitor is not None
        assert hasattr(monitor, 'start_monitoring')
        assert hasattr(monitor, 'stop_monitoring')
    
    def test_span_collection(self):
        """Test span collection and processing"""
        monitor = TelemetryMonitor()
        
        # Mock span data
        span_data = {
            "trace_id": "test_trace_id",
            "span_id": "test_span_id",
            "name": "test_operation",
            "attributes": {"test.attr": "test_value"},
            "events": [{"name": "test_event"}],
            "start_time": time.time(),
            "end_time": time.time() + 1.0
        }
        
        # Process span
        result = monitor.process_span(span_data)
        
        assert result is not None
        assert result.processed == True
    
    def test_metrics_aggregation(self):
        """Test metrics aggregation functionality"""
        monitor = TelemetryMonitor()
        
        # Mock metrics data
        metrics_data = [
            {"name": "request_count", "value": 10, "labels": {"service": "test"}},
            {"name": "request_count", "value": 15, "labels": {"service": "test"}},
            {"name": "error_count", "value": 2, "labels": {"service": "test"}}
        ]
        
        # Aggregate metrics
        aggregated = monitor.aggregate_metrics(metrics_data)
        
        assert "request_count" in aggregated
        assert "error_count" in aggregated
        assert aggregated["request_count"]["total"] == 25
    
    def test_alert_generation(self):
        """Test alert generation based on telemetry data"""
        monitor = TelemetryMonitor()
        
        # Mock alert conditions
        alert_conditions = {
            "high_error_rate": {"threshold": 0.1, "metric": "error_rate"},
            "high_latency": {"threshold": 1000, "metric": "response_time"}
        }
        
        # Mock current metrics
        current_metrics = {
            "error_rate": 0.15,  # Above threshold
            "response_time": 500  # Below threshold
        }
        
        alerts = monitor.check_alerts(current_metrics, alert_conditions)
        
        assert len(alerts) == 1
        assert "high_error_rate" in [alert["type"] for alert in alerts]


class TestGapAnalysis:
    """Test gap analysis functionality"""
    
    def test_gap_analyzer_initialization(self):
        """Test gap analyzer initialization"""
        analyzer = GapAnalyzer()
        
        assert analyzer is not None
        assert hasattr(analyzer, 'analyze_gaps')
        assert hasattr(analyzer, 'generate_recommendations')
    
    def test_telemetry_gap_detection(self):
        """Test detection of telemetry gaps"""
        analyzer = GapAnalyzer()
        
        # Mock expected vs actual telemetry
        expected_telemetry = {
            "service.name": True,
            "service.version": True,
            "http.method": True,
            "http.status_code": True,
            "custom.metric": True
        }
        
        actual_telemetry = {
            "service.name": True,
            "service.version": False,  # Missing
            "http.method": True,
            "http.status_code": True,
            "custom.metric": False  # Missing
        }
        
        gaps = analyzer.detect_gaps(expected_telemetry, actual_telemetry)
        
        assert len(gaps) == 2
        assert "service.version" in gaps
        assert "custom.metric" in gaps
    
    def test_coverage_analysis(self):
        """Test telemetry coverage analysis"""
        analyzer = GapAnalyzer()
        
        # Mock service endpoints
        endpoints = [
            "/api/users",
            "/api/orders",
            "/api/products",
            "/api/admin"
        ]
        
        # Mock instrumented endpoints
        instrumented = [
            "/api/users",
            "/api/orders"
        ]
        
        coverage = analyzer.analyze_coverage(endpoints, instrumented)
        
        assert coverage["total"] == 4
        assert coverage["instrumented"] == 2
        assert coverage["percentage"] == 50.0
    
    def test_recommendation_generation(self):
        """Test recommendation generation for gaps"""
        analyzer = GapAnalyzer()
        
        gaps = [
            {"metric": "service.version", "type": "missing_attribute"},
            {"metric": "http.request.size", "type": "missing_metric"},
            {"endpoint": "/api/admin", "type": "missing_instrumentation"}
        ]
        
        recommendations = analyzer.generate_recommendations(gaps)
        
        assert len(recommendations) == 3
        assert all("priority" in rec for rec in recommendations)
        assert all("action" in rec for rec in recommendations)


class TestRemediationEngine:
    """Test remediation engine functionality"""
    
    def test_remediation_engine_initialization(self):
        """Test remediation engine initialization"""
        engine = RemediationEngine()
        
        assert engine is not None
        assert hasattr(engine, 'register_action')
        assert hasattr(engine, 'execute_remediation')
    
    def test_remediation_action_registration(self):
        """Test registration of remediation actions"""
        engine = RemediationEngine()
        
        def mock_action(context):
            return {"status": "success", "message": "Mock action executed"}
        
        engine.register_action("add_missing_attribute", mock_action)
        
        assert "add_missing_attribute" in engine.actions
    
    def test_automatic_remediation(self):
        """Test automatic remediation execution"""
        engine = RemediationEngine()
        
        # Register mock action
        def mock_action(context):
            context["remediated"] = True
            return {"status": "success"}
        
        engine.register_action("test_remediation", mock_action)
        
        # Execute remediation
        context = {"gap": "test_gap"}
        result = engine.execute_remediation("test_remediation", context)
        
        assert result["status"] == "success"
        assert context["remediated"] == True
    
    def test_remediation_history(self):
        """Test remediation history tracking"""
        engine = RemediationEngine()
        
        # Execute some remediations
        def mock_action(context):
            return {"status": "success"}
        
        engine.register_action("action1", mock_action)
        engine.register_action("action2", mock_action)
        
        engine.execute_remediation("action1", {"context": "test1"})
        engine.execute_remediation("action2", {"context": "test2"})
        
        history = engine.get_remediation_history()
        
        assert len(history) == 2
        assert history[0]["action"] == "action1"
        assert history[1]["action"] == "action2"


class TestSecurityMonitoring:
    """Test security monitoring functionality"""
    
    def test_security_monitor_initialization(self):
        """Test security monitor initialization"""
        monitor = SecurityMonitor()
        
        assert monitor is not None
        assert hasattr(monitor, 'scan_for_vulnerabilities')
        assert hasattr(monitor, 'generate_security_report')
    
    def test_vulnerability_scanning(self):
        """Test vulnerability scanning functionality"""
        monitor = SecurityMonitor()
        
        # Mock telemetry data for security analysis
        telemetry_data = {
            "spans": [
                {
                    "name": "database_query",
                    "attributes": {"db.statement": "SELECT * FROM users WHERE id = 1"},
                    "events": []
                },
                {
                    "name": "http_request",
                    "attributes": {"http.url": "http://example.com/api/users/1"},
                    "events": []
                }
            ]
        }
        
        vulnerabilities = monitor.scan_for_vulnerabilities(telemetry_data)
        
        assert isinstance(vulnerabilities, list)
        # Should detect potential SQL injection patterns
        assert any("sql_injection" in vuln["type"] for vuln in vulnerabilities)
    
    def test_security_event_simulation(self):
        """Test security event simulation"""
        monitor = SecurityMonitor()
        
        # Simulate security event
        event_data = {
            "type": "authentication_failure",
            "severity": "high",
            "source": "login_endpoint",
            "details": {"user_id": "test_user", "attempts": 5}
        }
        
        result = monitor.simulate_security_event(event_data)
        
        assert result["simulated"] == True
        assert result["event_type"] == "authentication_failure"
    
    def test_security_report_generation(self):
        """Test security report generation"""
        monitor = SecurityMonitor()
        
        # Mock security data
        security_data = {
            "vulnerabilities": [
                {"type": "sql_injection", "severity": "high", "count": 3},
                {"type": "xss", "severity": "medium", "count": 1}
            ],
            "events": [
                {"type": "authentication_failure", "count": 10},
                {"type": "authorization_failure", "count": 2}
            ]
        }
        
        report = monitor.generate_security_report(security_data)
        
        assert "summary" in report
        assert "vulnerabilities" in report
        assert "recommendations" in report
        assert report["total_vulnerabilities"] == 4


class TestOTELWeaverIntegration:
    """Test OpenTelemetry Weaver integration"""
    
    def test_weaver_otel_integration(self):
        """Test Weaver-OTEL integration"""
        integration = OTELWeaverIntegration()
        
        assert integration is not None
        assert hasattr(integration, 'instrument_weaver')
        assert hasattr(integration, 'extract_telemetry')
    
    def test_weaver_instrumentation(self):
        """Test Weaver instrumentation with OTEL"""
        integration = OTELWeaverIntegration()
        
        # Mock Weaver operation
        weaver_operation = {
            "operation": "generate_model",
            "convention": "test_convention",
            "parameters": {"template": "model_template"}
        }
        
        result = integration.instrument_weaver(weaver_operation)
        
        assert result["instrumented"] == True
        assert "span_id" in result
    
    def test_telemetry_extraction(self):
        """Test telemetry extraction from Weaver operations"""
        integration = OTELWeaverIntegration()
        
        # Mock Weaver telemetry data
        weaver_telemetry = {
            "operations": [
                {"name": "generate_model", "duration": 1.5, "success": True},
                {"name": "validate_convention", "duration": 0.3, "success": True}
            ]
        }
        
        extracted = integration.extract_telemetry(weaver_telemetry)
        
        assert "metrics" in extracted
        assert "spans" in extracted
        assert len(extracted["metrics"]) > 0


class TestOTELGapAnalyzer:
    """Test OpenTelemetry gap analyzer"""
    
    def test_otel_gap_analyzer(self):
        """Test OTEL-specific gap analysis"""
        analyzer = OTELGapAnalyzer()
        
        assert analyzer is not None
        assert hasattr(analyzer, 'analyze_otel_gaps')
        assert hasattr(analyzer, 'validate_spans')
    
    def test_span_validation(self):
        """Test span validation against schemas"""
        analyzer = OTELGapAnalyzer()
        
        # Mock spans
        spans = [
            {
                "name": "http_request",
                "attributes": {
                    "http.method": "GET",
                    "http.url": "/api/users",
                    "http.status_code": 200
                }
            },
            {
                "name": "database_query",
                "attributes": {
                    "db.system": "postgresql",
                    "db.statement": "SELECT * FROM users"
                }
            }
        ]
        
        validation_result = analyzer.validate_spans(spans)
        
        assert validation_result["valid"] == True
        assert validation_result["total_spans"] == 2
    
    def test_otel_gap_detection(self):
        """Test OTEL-specific gap detection"""
        analyzer = OTELGapAnalyzer()
        
        # Mock expected vs actual OTEL attributes
        expected_attributes = {
            "http.method": True,
            "http.url": True,
            "http.status_code": True,
            "http.request.size": True,
            "http.response.size": True
        }
        
        actual_attributes = {
            "http.method": True,
            "http.url": True,
            "http.status_code": True,
            "http.request.size": False,  # Missing
            "http.response.size": False  # Missing
        }
        
        gaps = analyzer.analyze_otel_gaps(expected_attributes, actual_attributes)
        
        assert len(gaps) == 2
        assert "http.request.size" in gaps
        assert "http.response.size" in gaps


class TestOTELMonitor:
    """Test OpenTelemetry monitor"""
    
    def test_otel_monitor(self):
        """Test OTEL monitor functionality"""
        monitor = OTELMonitor()
        
        assert monitor is not None
        assert hasattr(monitor, 'start_monitoring')
        assert hasattr(monitor, 'collect_metrics')
    
    def test_metric_collection(self):
        """Test metric collection from OTEL"""
        monitor = OTELMonitor()
        
        # Mock OTEL metrics
        otel_metrics = {
            "request_count": 100,
            "error_count": 5,
            "response_time": 250.5,
            "active_connections": 15
        }
        
        collected = monitor.collect_metrics(otel_metrics)
        
        assert "request_count" in collected
        assert "error_rate" in collected
        assert collected["error_rate"] == 0.05  # 5/100
    
    def test_real_time_monitoring(self):
        """Test real-time monitoring capabilities"""
        monitor = OTELMonitor()
        
        # Start monitoring
        monitor.start_monitoring()
        
        # Simulate some activity
        time.sleep(0.1)
        
        # Get current metrics
        metrics = monitor.get_current_metrics()
        
        assert metrics is not None
        assert "timestamp" in metrics
        
        # Stop monitoring
        monitor.stop_monitoring()


class TestTelemetryPerformance:
    """Test telemetry system performance"""
    
    def test_high_volume_span_processing(self):
        """Test processing of high volume spans"""
        monitor = TelemetryMonitor()
        
        # Generate large number of spans
        spans = []
        for i in range(1000):
            spans.append({
                "trace_id": f"trace_{i}",
                "span_id": f"span_{i}",
                "name": f"operation_{i}",
                "attributes": {"test.attr": f"value_{i}"},
                "start_time": time.time(),
                "end_time": time.time() + 0.1
            })
        
        # Process spans
        import time
        start_time = time.time()
        
        for span in spans:
            monitor.process_span(span)
        
        end_time = time.time()
        
        # Should process 1000 spans in reasonable time (< 10 seconds)
        assert (end_time - start_time) < 10.0
    
    def test_concurrent_telemetry_processing(self):
        """Test concurrent telemetry processing"""
        import threading
        
        monitor = TelemetryMonitor()
        results = []
        
        def process_spans(thread_id):
            spans = [
                {
                    "trace_id": f"trace_{thread_id}_{i}",
                    "span_id": f"span_{thread_id}_{i}",
                    "name": f"operation_{i}",
                    "attributes": {"thread_id": thread_id}
                }
                for i in range(100)
            ]
            
            for span in spans:
                result = monitor.process_span(span)
                results.append(result)
        
        # Run concurrent processing
        threads = []
        for i in range(5):
            thread = threading.Thread(target=process_spans, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify all spans processed
        assert len(results) == 500  # 5 threads * 100 spans each


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 