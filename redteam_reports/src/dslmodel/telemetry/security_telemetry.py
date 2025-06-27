"""
Security-focused Telemetry and Compliance Monitoring
Provides security-specific spans and real-time threat detection.
"""

import time
import hashlib
import ipaddress
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import re
from pathlib import Path
from loguru import logger

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode


class SecurityEventType(Enum):
    """Types of security events."""
    AUTHENTICATION_FAILURE = "auth_failure"
    AUTHORIZATION_VIOLATION = "authz_violation"
    SUSPICIOUS_ACCESS = "suspicious_access"
    DATA_EXFILTRATION = "data_exfiltration"
    INJECTION_ATTEMPT = "injection_attempt"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"
    COMPLIANCE_VIOLATION = "compliance_violation"
    CRYPTO_MISUSE = "crypto_misuse"
    INSIDER_THREAT = "insider_threat"


class ThreatLevel(Enum):
    """Threat severity levels."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityEvent:
    """Represents a security-related event."""
    event_type: SecurityEventType
    threat_level: ThreatLevel
    source_ip: Optional[str] = None
    user_id: Optional[str] = None
    resource: Optional[str] = None
    description: str = ""
    indicators: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    trace_id: str = ""
    
    def to_otel_attributes(self) -> Dict[str, Any]:
        """Convert to OpenTelemetry span attributes."""
        return {
            "security.event.type": self.event_type.value,
            "security.threat.level": self.threat_level.value,
            "security.source.ip": self.source_ip or "unknown",
            "security.user.id": self.user_id or "anonymous",
            "security.resource": self.resource or "unknown",
            "security.description": self.description,
            "security.indicators.count": len(self.indicators),
            "security.timestamp": self.timestamp.isoformat()
        }


class SecurityTelemetryCollector:
    """Collects and analyzes security telemetry."""
    
    def __init__(self):
        """Initialize the security telemetry collector."""
        self.tracer = trace.get_tracer(__name__, "1.0.0")
        self.security_events: List[SecurityEvent] = []
        self.threat_patterns = self._load_threat_patterns()
        self.compliance_rules = self._load_compliance_rules()
        self.ip_whitelist: Set[str] = set()
        self.suspicious_ips: Set[str] = set()
        self.failed_auth_attempts: Dict[str, List[datetime]] = {}
        
        logger.info("Security telemetry collector initialized")
    
    def _load_threat_patterns(self) -> Dict[str, Any]:
        """Load threat detection patterns."""
        return {
            "sql_injection": [
                r"union\s+select",
                r"drop\s+table",
                r"insert\s+into",
                r"delete\s+from",
                r"exec\s*\(",
                r"script\s*>",
                r"<\s*script",
                r"javascript:",
                r"eval\s*\(",
                r"expression\s*\("
            ],
            "xss_patterns": [
                r"<script",
                r"javascript:",
                r"onload\s*=",
                r"onerror\s*=",
                r"onclick\s*=",
                r"eval\s*\(",
                r"document\s*\.\s*cookie",
                r"window\s*\.\s*location"
            ],
            "command_injection": [
                r";\s*(rm|del|format)",
                r"\|\s*(nc|netcat)",
                r"&&\s*(wget|curl)",
                r"`.*`",
                r"\$\(.*\)",
                r">\s*/dev/"
            ],
            "path_traversal": [
                r"\.\./",
                r"\.\.\\",
                r"%2e%2e%2f",
                r"%2e%2e\\",
                r"..%252f",
                r"..%255c"
            ]
        }
    
    def _load_compliance_rules(self) -> Dict[str, Any]:
        """Load compliance monitoring rules."""
        return {
            "gdpr": {
                "data_retention_days": 365,
                "encryption_required": True,
                "consent_tracking": True,
                "data_minimization": True
            },
            "pci_dss": {
                "card_data_encryption": True,
                "access_logging": True,
                "network_segmentation": True,
                "regular_testing": True
            },
            "sox": {
                "audit_trail_required": True,
                "segregation_of_duties": True,
                "change_management": True,
                "data_integrity": True
            },
            "hipaa": {
                "phi_encryption": True,
                "access_controls": True,
                "audit_logs": True,
                "breach_notification": True
            }
        }
    
    def emit_security_event(self, event: SecurityEvent):
        """Emit a security event with OpenTelemetry span."""
        with self.tracer.start_as_current_span("swarmsh.security.event") as span:
            # Set span attributes
            attributes = event.to_otel_attributes()
            for key, value in attributes.items():
                span.set_attribute(key, str(value))
            
            # Set span status based on threat level
            if event.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
                span.set_status(Status(StatusCode.ERROR, f"Security threat: {event.event_type.value}"))
            else:
                span.set_status(Status(StatusCode.OK))
            
            # Store event
            self.security_events.append(event)
            
            # Log security event
            log_level = {
                ThreatLevel.INFO: logger.info,
                ThreatLevel.LOW: logger.info,
                ThreatLevel.MEDIUM: logger.warning,
                ThreatLevel.HIGH: logger.error,
                ThreatLevel.CRITICAL: logger.critical
            }.get(event.threat_level, logger.info)
            
            log_level(f"Security Event: {event.event_type.value} - {event.description}")
    
    def analyze_request(self, request_data: Dict[str, Any]) -> Optional[SecurityEvent]:
        """Analyze a request for security threats."""
        url = request_data.get("url", "")
        params = request_data.get("params", {})
        headers = request_data.get("headers", {})
        body = request_data.get("body", "")
        source_ip = request_data.get("source_ip", "")
        user_id = request_data.get("user_id", "")
        
        # Check for injection attempts
        all_inputs = " ".join([url, str(params), str(headers), body])
        
        for pattern_type, patterns in self.threat_patterns.items():
            for pattern in patterns:
                if re.search(pattern, all_inputs, re.IGNORECASE):
                    return SecurityEvent(
                        event_type=SecurityEventType.INJECTION_ATTEMPT,
                        threat_level=ThreatLevel.HIGH,
                        source_ip=source_ip,
                        user_id=user_id,
                        resource=url,
                        description=f"Detected {pattern_type} attempt",
                        indicators={"pattern": pattern, "input": all_inputs[:200]},
                        trace_id=request_data.get("trace_id", "")
                    )
        
        # Check for suspicious IP behavior
        if source_ip and self._is_suspicious_ip(source_ip):
            return SecurityEvent(
                event_type=SecurityEventType.SUSPICIOUS_ACCESS,
                threat_level=ThreatLevel.MEDIUM,
                source_ip=source_ip,
                user_id=user_id,
                resource=url,
                description="Access from suspicious IP address",
                indicators={"ip_reputation": "suspicious"},
                trace_id=request_data.get("trace_id", "")
            )
        
        return None
    
    def track_authentication_attempt(self, user_id: str, success: bool, source_ip: str, trace_id: str = ""):
        """Track authentication attempts and detect brute force."""
        with self.tracer.start_as_current_span("swarmsh.security.authentication") as span:
            span.set_attribute("security.auth.user_id", user_id)
            span.set_attribute("security.auth.success", success)
            span.set_attribute("security.auth.source_ip", source_ip)
            
            if not success:
                # Track failed attempts
                key = f"{user_id}:{source_ip}"
                if key not in self.failed_auth_attempts:
                    self.failed_auth_attempts[key] = []
                
                self.failed_auth_attempts[key].append(datetime.now())
                
                # Clean old attempts (last 15 minutes)
                cutoff = datetime.now() - timedelta(minutes=15)
                self.failed_auth_attempts[key] = [
                    ts for ts in self.failed_auth_attempts[key] if ts > cutoff
                ]
                
                # Check for brute force
                if len(self.failed_auth_attempts[key]) >= 5:
                    event = SecurityEvent(
                        event_type=SecurityEventType.AUTHENTICATION_FAILURE,
                        threat_level=ThreatLevel.HIGH,
                        source_ip=source_ip,
                        user_id=user_id,
                        description=f"Brute force attack detected: {len(self.failed_auth_attempts[key])} failed attempts",
                        indicators={"attempts": len(self.failed_auth_attempts[key])},
                        trace_id=trace_id
                    )
                    self.emit_security_event(event)
                    
                    # Add to suspicious IPs
                    self.suspicious_ips.add(source_ip)
                    
                    span.set_status(Status(StatusCode.ERROR, "Brute force detected"))
                else:
                    span.set_status(Status(StatusCode.ERROR, "Authentication failed"))
            else:
                span.set_status(Status(StatusCode.OK, "Authentication successful"))
    
    def monitor_data_access(self, user_id: str, resource: str, operation: str, data_sensitivity: str, trace_id: str = ""):
        """Monitor data access for compliance and anomalies."""
        with self.tracer.start_as_current_span("swarmsh.security.data_access") as span:
            span.set_attribute("security.data.user_id", user_id)
            span.set_attribute("security.data.resource", resource)
            span.set_attribute("security.data.operation", operation)
            span.set_attribute("security.data.sensitivity", data_sensitivity)
            
            # Check for sensitive data access
            if data_sensitivity in ["high", "critical"] and operation in ["read", "export"]:
                event = SecurityEvent(
                    event_type=SecurityEventType.DATA_EXFILTRATION,
                    threat_level=ThreatLevel.MEDIUM,
                    user_id=user_id,
                    resource=resource,
                    description=f"Sensitive data access: {operation} on {data_sensitivity} data",
                    indicators={"sensitivity": data_sensitivity, "operation": operation},
                    trace_id=trace_id
                )
                self.emit_security_event(event)
            
            # Check compliance requirements
            self._check_compliance_violations(user_id, resource, operation, data_sensitivity, trace_id)
    
    def detect_anomalous_behavior(self, user_id: str, activity_metrics: Dict[str, Any], trace_id: str = ""):
        """Detect anomalous user behavior patterns."""
        with self.tracer.start_as_current_span("swarmsh.security.anomaly_detection") as span:
            span.set_attribute("security.anomaly.user_id", user_id)
            
            # Simple anomaly detection based on activity volume
            requests_per_minute = activity_metrics.get("requests_per_minute", 0)
            data_volume_mb = activity_metrics.get("data_volume_mb", 0)
            unique_resources = activity_metrics.get("unique_resources", 0)
            
            span.set_attribute("security.anomaly.requests_per_minute", requests_per_minute)
            span.set_attribute("security.anomaly.data_volume_mb", data_volume_mb)
            span.set_attribute("security.anomaly.unique_resources", unique_resources)
            
            # Thresholds for anomaly detection
            anomaly_detected = False
            indicators = {}
            
            if requests_per_minute > 100:
                anomaly_detected = True
                indicators["high_request_rate"] = requests_per_minute
            
            if data_volume_mb > 500:
                anomaly_detected = True
                indicators["high_data_volume"] = data_volume_mb
            
            if unique_resources > 50:
                anomaly_detected = True
                indicators["resource_scanning"] = unique_resources
            
            if anomaly_detected:
                event = SecurityEvent(
                    event_type=SecurityEventType.ANOMALOUS_BEHAVIOR,
                    threat_level=ThreatLevel.MEDIUM,
                    user_id=user_id,
                    description="Anomalous user behavior detected",
                    indicators=indicators,
                    trace_id=trace_id
                )
                self.emit_security_event(event)
                span.set_status(Status(StatusCode.ERROR, "Anomalous behavior"))
            else:
                span.set_status(Status(StatusCode.OK))
    
    def _is_suspicious_ip(self, ip: str) -> bool:
        """Check if an IP address is suspicious."""
        if ip in self.suspicious_ips:
            return True
        
        try:
            ip_obj = ipaddress.ip_address(ip)
            # Check for private/internal IPs (generally trusted)
            if ip_obj.is_private or ip_obj.is_loopback:
                return False
        except ValueError:
            return True  # Invalid IP is suspicious
        
        # Additional checks could include:
        # - IP reputation databases
        # - Geolocation anomalies
        # - Known bad IP lists
        
        return False
    
    def _check_compliance_violations(self, user_id: str, resource: str, operation: str, sensitivity: str, trace_id: str):
        """Check for compliance violations."""
        violations = []
        
        # GDPR checks
        if "gdpr" in self.compliance_rules:
            if sensitivity == "pii" and operation == "export" and not self._has_consent(user_id):
                violations.append("GDPR: PII export without consent")
        
        # PCI DSS checks
        if "pci_dss" in self.compliance_rules:
            if "card" in resource.lower() and not self._is_encrypted_access(resource):
                violations.append("PCI DSS: Unencrypted card data access")
        
        # HIPAA checks
        if "hipaa" in self.compliance_rules:
            if "phi" in resource.lower() or "health" in resource.lower():
                if not self._has_proper_authorization(user_id, resource):
                    violations.append("HIPAA: Unauthorized PHI access")
        
        # Emit compliance violation events
        for violation in violations:
            event = SecurityEvent(
                event_type=SecurityEventType.COMPLIANCE_VIOLATION,
                threat_level=ThreatLevel.HIGH,
                user_id=user_id,
                resource=resource,
                description=violation,
                indicators={"compliance_type": violation.split(":")[0]},
                trace_id=trace_id
            )
            self.emit_security_event(event)
    
    def _has_consent(self, user_id: str) -> bool:
        """Check if user has given consent for data processing."""
        # Simplified check - in real implementation, check consent database
        return True  # Assume consent for demo
    
    def _is_encrypted_access(self, resource: str) -> bool:
        """Check if access to resource is encrypted."""
        # Simplified check - in real implementation, check encryption status
        return True  # Assume encrypted for demo
    
    def _has_proper_authorization(self, user_id: str, resource: str) -> bool:
        """Check if user has proper authorization for resource."""
        # Simplified check - in real implementation, check authorization database
        return True  # Assume authorized for demo
    
    def get_security_metrics(self) -> Dict[str, Any]:
        """Get aggregated security metrics."""
        total_events = len(self.security_events)
        if total_events == 0:
            return {"total_events": 0, "threat_distribution": {}, "recent_threats": []}
        
        # Count events by threat level
        threat_distribution = {}
        for event in self.security_events:
            level = event.threat_level.value
            threat_distribution[level] = threat_distribution.get(level, 0) + 1
        
        # Get recent high-severity events
        recent_threats = [
            {
                "type": event.event_type.value,
                "level": event.threat_level.value,
                "description": event.description,
                "timestamp": event.timestamp.isoformat()
            }
            for event in self.security_events[-10:]
            if event.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]
        ]
        
        return {
            "total_events": total_events,
            "threat_distribution": threat_distribution,
            "recent_threats": recent_threats,
            "suspicious_ips": len(self.suspicious_ips),
            "failed_auth_patterns": len(self.failed_auth_attempts)
        }
    
    def generate_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report."""
        return {
            "report_timestamp": datetime.now().isoformat(),
            "metrics": self.get_security_metrics(),
            "threat_summary": self._get_threat_summary(),
            "compliance_status": self._get_compliance_status(),
            "recommendations": self._get_security_recommendations()
        }
    
    def _get_threat_summary(self) -> Dict[str, Any]:
        """Get threat summary for the report."""
        last_24h = datetime.now() - timedelta(hours=24)
        recent_events = [e for e in self.security_events if e.timestamp > last_24h]
        
        return {
            "events_last_24h": len(recent_events),
            "critical_threats": len([e for e in recent_events if e.threat_level == ThreatLevel.CRITICAL]),
            "high_threats": len([e for e in recent_events if e.threat_level == ThreatLevel.HIGH]),
            "top_threat_types": self._get_top_threat_types(recent_events)
        }
    
    def _get_top_threat_types(self, events: List[SecurityEvent]) -> List[Dict[str, Any]]:
        """Get top threat types from events."""
        type_counts = {}
        for event in events:
            type_name = event.event_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        return [
            {"type": threat_type, "count": count}
            for threat_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
    
    def _get_compliance_status(self) -> Dict[str, Any]:
        """Get compliance status summary."""
        return {
            "monitored_frameworks": list(self.compliance_rules.keys()),
            "violations_detected": len([e for e in self.security_events if e.event_type == SecurityEventType.COMPLIANCE_VIOLATION]),
            "last_audit": datetime.now().isoformat()  # Simplified
        }
    
    def _get_security_recommendations(self) -> List[str]:
        """Get security recommendations based on detected patterns."""
        recommendations = []
        
        if len(self.suspicious_ips) > 5:
            recommendations.append("Consider implementing IP-based rate limiting")
        
        failed_auth_count = sum(len(attempts) for attempts in self.failed_auth_attempts.values())
        if failed_auth_count > 10:
            recommendations.append("Review authentication mechanisms and consider MFA")
        
        injection_attempts = len([e for e in self.security_events if e.event_type == SecurityEventType.INJECTION_ATTEMPT])
        if injection_attempts > 0:
            recommendations.append("Implement input validation and parameterized queries")
        
        return recommendations


# Global security telemetry collector
_global_security_collector: Optional[SecurityTelemetryCollector] = None


def get_security_collector() -> SecurityTelemetryCollector:
    """Get the global security telemetry collector."""
    global _global_security_collector
    if _global_security_collector is None:
        _global_security_collector = SecurityTelemetryCollector()
    return _global_security_collector