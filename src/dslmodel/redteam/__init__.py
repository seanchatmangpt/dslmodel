"""
DSLModel Automated Red Team Framework
Comprehensive security testing and vulnerability assessment
"""

from .core import (
    RedTeamScanner,
    VulnerabilityReport,
    SecurityTest,
    AttackVector,
    RedTeamEngine
)

from .scanners import (
    CodeVulnerabilityScanner,
    DependencyScanner,
    PQCCryptoScanner,
    OTELSecurityScanner,
    SwarmCoordinationScanner
)

from .attacks import (
    AdversarialTestGenerator,
    PenetrationTester,
    CryptoAttacker,
    TelemetryProber
)

from .reports import (
    SecurityReportGenerator,
    RemediationEngine,
    RiskAssessment
)

__all__ = [
    # Core framework
    "RedTeamScanner",
    "VulnerabilityReport", 
    "SecurityTest",
    "AttackVector",
    "RedTeamEngine",
    
    # Specialized scanners
    "CodeVulnerabilityScanner",
    "DependencyScanner", 
    "PQCCryptoScanner",
    "OTELSecurityScanner",
    "SwarmCoordinationScanner",
    
    # Attack modules
    "AdversarialTestGenerator",
    "PenetrationTester",
    "CryptoAttacker",
    "TelemetryProber",
    
    # Reporting
    "SecurityReportGenerator",
    "RemediationEngine",
    "RiskAssessment"
]