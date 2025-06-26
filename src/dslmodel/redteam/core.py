"""
Core Red Team Framework Components
Base classes for security testing and vulnerability assessment
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Any, Optional, Union, Set
from datetime import datetime, timedelta
from pathlib import Path
import asyncio
import hashlib
import json

from dslmodel import DSLModel
from pydantic import Field, validator

class SeverityLevel(str, Enum):
    """Security vulnerability severity levels"""
    CRITICAL = "critical"
    HIGH = "high" 
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class AttackType(str, Enum):
    """Types of security attacks"""
    CODE_INJECTION = "code_injection"
    CRYPTOGRAPHIC = "cryptographic"
    TELEMETRY_LEAK = "telemetry_leak"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_EXFILTRATION = "data_exfiltration"
    DENIAL_OF_SERVICE = "denial_of_service"
    AUTHENTICATION_BYPASS = "authentication_bypass"
    AUTHORIZATION_BYPASS = "authorization_bypass"
    SUPPLY_CHAIN = "supply_chain"
    CONFIGURATION = "configuration"

class VulnerabilityCategory(str, Enum):
    """OWASP-based vulnerability categories"""
    A01_BROKEN_ACCESS_CONTROL = "a01_broken_access_control"
    A02_CRYPTOGRAPHIC_FAILURES = "a02_cryptographic_failures"
    A03_INJECTION = "a03_injection"
    A04_INSECURE_DESIGN = "a04_insecure_design"
    A05_SECURITY_MISCONFIGURATION = "a05_security_misconfiguration"
    A06_VULNERABLE_COMPONENTS = "a06_vulnerable_components"
    A07_IDENTIFICATION_FAILURES = "a07_identification_failures"
    A08_SOFTWARE_INTEGRITY_FAILURES = "a08_software_integrity_failures"
    A09_LOGGING_MONITORING_FAILURES = "a09_logging_monitoring_failures"
    A10_SERVER_SIDE_REQUEST_FORGERY = "a10_server_side_request_forgery"

class SecurityTest(DSLModel):
    """Individual security test case"""
    test_id: str = Field(..., description="Unique test identifier")
    name: str = Field(..., description="Test name")
    description: str = Field(..., description="Test description")
    attack_type: AttackType = Field(..., description="Type of attack being tested")
    category: VulnerabilityCategory = Field(..., description="OWASP category")
    severity: SeverityLevel = Field(..., description="Expected severity if vulnerable")
    target_component: str = Field(..., description="Component being tested")
    test_payload: Optional[str] = Field(None, description="Test payload/input")
    expected_outcome: str = Field(..., description="Expected secure behavior")
    remediation_hint: str = Field(..., description="How to fix if vulnerable")
    
class AttackVector(DSLModel):
    """Represents a potential attack vector"""
    vector_id: str = Field(..., description="Unique vector identifier")
    name: str = Field(..., description="Attack vector name")
    attack_type: AttackType = Field(..., description="Type of attack")
    entry_points: List[str] = Field(..., description="Potential entry points")
    prerequisites: List[str] = Field(default_factory=list, description="Prerequisites for attack")
    impact: str = Field(..., description="Potential impact if exploited")
    likelihood: float = Field(..., ge=0.0, le=1.0, description="Likelihood of successful exploit")
    detection_difficulty: float = Field(..., ge=0.0, le=1.0, description="Difficulty of detecting attack")

class VulnerabilityReport(DSLModel):
    """Security vulnerability report"""
    vulnerability_id: str = Field(..., description="Unique vulnerability ID")
    title: str = Field(..., description="Vulnerability title")
    description: str = Field(..., description="Detailed description")
    severity: SeverityLevel = Field(..., description="Severity level")
    category: VulnerabilityCategory = Field(..., description="OWASP category")
    attack_type: AttackType = Field(..., description="Attack type")
    affected_components: List[str] = Field(..., description="Affected components")
    file_path: Optional[str] = Field(None, description="File path if applicable")
    line_number: Optional[int] = Field(None, description="Line number if applicable")
    cvss_score: Optional[float] = Field(None, ge=0.0, le=10.0, description="CVSS v3.1 score")
    exploit_code: Optional[str] = Field(None, description="Proof of concept exploit")
    remediation: str = Field(..., description="How to fix the vulnerability")
    references: List[str] = Field(default_factory=list, description="External references")
    discovered_at: datetime = Field(default_factory=datetime.utcnow)
    validated: bool = Field(False, description="Whether vulnerability was validated")

class RedTeamScanner(ABC):
    """Abstract base class for security scanners"""
    
    def __init__(self, name: str, target_path: Path):
        self.name = name
        self.target_path = target_path
        self.vulnerabilities: List[VulnerabilityReport] = []
        self.attack_vectors: List[AttackVector] = []
        
    @abstractmethod
    async def scan(self) -> List[VulnerabilityReport]:
        """Perform security scan and return vulnerabilities"""
        pass
    
    @abstractmethod
    def get_attack_vectors(self) -> List[AttackVector]:
        """Get potential attack vectors for this scanner"""
        pass
    
    def calculate_risk_score(self) -> float:
        """Calculate overall risk score based on vulnerabilities"""
        if not self.vulnerabilities:
            return 0.0
            
        severity_weights = {
            SeverityLevel.CRITICAL: 10.0,
            SeverityLevel.HIGH: 7.5,
            SeverityLevel.MEDIUM: 5.0,
            SeverityLevel.LOW: 2.5,
            SeverityLevel.INFO: 1.0
        }
        
        total_score = sum(severity_weights.get(vuln.severity, 1.0) for vuln in self.vulnerabilities)
        return min(total_score / 10.0, 10.0)  # Normalize to 0-10 scale

class RedTeamEngine(DSLModel):
    """Main red team engine coordinating all security testing"""
    session_id: str = Field(..., description="Red team session ID")
    target_path: Path = Field(..., description="Target path to scan")
    scanners: List[str] = Field(default_factory=list, description="Active scanner names")
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = Field(None, description="Scan completion time")
    total_vulnerabilities: int = Field(0, description="Total vulnerabilities found")
    critical_vulnerabilities: int = Field(0, description="Critical vulnerabilities")
    high_vulnerabilities: int = Field(0, description="High severity vulnerabilities")
    overall_risk_score: float = Field(0.0, description="Overall risk score 0-10")
    scan_coverage: Dict[str, float] = Field(default_factory=dict, description="Coverage per component")
    
    def __init__(self, **data):
        super().__init__(**data)
        self.active_scanners: Dict[str, RedTeamScanner] = {}
        self.all_vulnerabilities: List[VulnerabilityReport] = []
        self.all_attack_vectors: List[AttackVector] = []
        
    def register_scanner(self, scanner: RedTeamScanner):
        """Register a security scanner"""
        self.active_scanners[scanner.name] = scanner
        if scanner.name not in self.scanners:
            self.scanners.append(scanner.name)
    
    async def run_comprehensive_scan(self) -> Dict[str, Any]:
        """Run all registered scanners and compile results"""
        self.start_time = datetime.utcnow()
        
        # Run all scanners concurrently
        scan_tasks = []
        for scanner in self.active_scanners.values():
            scan_tasks.append(self._run_scanner(scanner))
        
        scan_results = await asyncio.gather(*scan_tasks, return_exceptions=True)
        
        # Compile results
        self._compile_results()
        self.end_time = datetime.utcnow()
        
        return self._generate_summary()
    
    async def _run_scanner(self, scanner: RedTeamScanner) -> Dict[str, Any]:
        """Run individual scanner"""
        try:
            vulnerabilities = await scanner.scan()
            attack_vectors = scanner.get_attack_vectors()
            
            return {
                "scanner": scanner.name,
                "vulnerabilities": vulnerabilities,
                "attack_vectors": attack_vectors,
                "risk_score": scanner.calculate_risk_score(),
                "success": True
            }
        except Exception as e:
            return {
                "scanner": scanner.name,
                "error": str(e),
                "success": False
            }
    
    def _compile_results(self):
        """Compile results from all scanners"""
        self.all_vulnerabilities = []
        self.all_attack_vectors = []
        
        for scanner in self.active_scanners.values():
            self.all_vulnerabilities.extend(scanner.vulnerabilities)
            self.all_attack_vectors.extend(scanner.attack_vectors)
        
        # Update counters
        self.total_vulnerabilities = len(self.all_vulnerabilities)
        self.critical_vulnerabilities = sum(1 for v in self.all_vulnerabilities if v.severity == SeverityLevel.CRITICAL)
        self.high_vulnerabilities = sum(1 for v in self.all_vulnerabilities if v.severity == SeverityLevel.HIGH)
        
        # Calculate overall risk score
        if self.active_scanners:
            self.overall_risk_score = sum(s.calculate_risk_score() for s in self.active_scanners.values()) / len(self.active_scanners)
        
        # Calculate coverage
        self.scan_coverage = {name: 1.0 for name in self.scanners}  # Simplified coverage
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate comprehensive scan summary"""
        duration = (self.end_time - self.start_time).total_seconds() if self.end_time else 0
        
        # Group vulnerabilities by severity
        vuln_by_severity = {}
        for severity in SeverityLevel:
            vuln_by_severity[severity.value] = [
                v for v in self.all_vulnerabilities if v.severity == severity
            ]
        
        # Group by category
        vuln_by_category = {}
        for category in VulnerabilityCategory:
            vuln_by_category[category.value] = [
                v for v in self.all_vulnerabilities if v.category == category
            ]
        
        # Group by attack type
        vuln_by_attack_type = {}
        for attack_type in AttackType:
            vuln_by_attack_type[attack_type.value] = [
                v for v in self.all_vulnerabilities if v.attack_type == attack_type
            ]
        
        return {
            "session_id": self.session_id,
            "scan_summary": {
                "duration_seconds": duration,
                "total_vulnerabilities": self.total_vulnerabilities,
                "critical_vulnerabilities": self.critical_vulnerabilities,
                "high_vulnerabilities": self.high_vulnerabilities,
                "overall_risk_score": self.overall_risk_score,
                "scanners_used": len(self.active_scanners),
                "attack_vectors_identified": len(self.all_attack_vectors)
            },
            "vulnerabilities_by_severity": {
                k: len(v) for k, v in vuln_by_severity.items()
            },
            "vulnerabilities_by_category": {
                k: len(v) for k, v in vuln_by_category.items() 
            },
            "vulnerabilities_by_attack_type": {
                k: len(v) for k, v in vuln_by_attack_type.items()
            },
            "scanner_results": {
                name: {
                    "vulnerabilities": len(scanner.vulnerabilities),
                    "attack_vectors": len(scanner.attack_vectors),
                    "risk_score": scanner.calculate_risk_score()
                }
                for name, scanner in self.active_scanners.items()
            },
            "coverage": self.scan_coverage,
            "detailed_vulnerabilities": [v.dict() for v in self.all_vulnerabilities],
            "attack_vectors": [av.dict() for av in self.all_attack_vectors]
        }
    
    def get_critical_findings(self) -> List[VulnerabilityReport]:
        """Get only critical and high severity vulnerabilities"""
        return [
            v for v in self.all_vulnerabilities 
            if v.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]
        ]
    
    def get_remediation_priority(self) -> List[VulnerabilityReport]:
        """Get vulnerabilities ordered by remediation priority"""
        severity_order = {
            SeverityLevel.CRITICAL: 5,
            SeverityLevel.HIGH: 4,
            SeverityLevel.MEDIUM: 3,
            SeverityLevel.LOW: 2,
            SeverityLevel.INFO: 1
        }
        
        return sorted(
            self.all_vulnerabilities,
            key=lambda v: (severity_order.get(v.severity, 0), v.cvss_score or 0),
            reverse=True
        )