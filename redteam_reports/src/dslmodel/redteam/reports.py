"""
Security Report Generation and Remediation Engine
"""

import json
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass
import hashlib

from dslmodel import DSLModel
from pydantic import Field

from .core import (
    VulnerabilityReport, SecurityTest, AttackVector, RedTeamEngine,
    SeverityLevel, AttackType, VulnerabilityCategory
)

class RiskAssessment(DSLModel):
    """Risk assessment for security findings"""
    overall_risk_score: float = Field(..., ge=0.0, le=10.0, description="Overall risk score 0-10")
    critical_count: int = Field(0, description="Number of critical vulnerabilities")
    high_count: int = Field(0, description="Number of high severity vulnerabilities")
    medium_count: int = Field(0, description="Number of medium severity vulnerabilities")
    low_count: int = Field(0, description="Number of low severity vulnerabilities")
    info_count: int = Field(0, description="Number of informational findings")
    
    top_risks: List[str] = Field(default_factory=list, description="Top risk categories")
    remediation_priority: List[str] = Field(default_factory=list, description="Priority order for remediation")
    estimated_fix_time: str = Field("", description="Estimated time to fix critical issues")
    compliance_impact: List[str] = Field(default_factory=list, description="Compliance frameworks affected")
    
    def calculate_risk_level(self) -> str:
        """Calculate overall risk level"""
        if self.overall_risk_score >= 8.0:
            return "CRITICAL"
        elif self.overall_risk_score >= 6.0:
            return "HIGH" 
        elif self.overall_risk_score >= 4.0:
            return "MEDIUM"
        elif self.overall_risk_score >= 2.0:
            return "LOW"
        else:
            return "MINIMAL"

class RemediationStep(DSLModel):
    """Individual remediation step"""
    step_id: str = Field(..., description="Unique step identifier")
    title: str = Field(..., description="Step title")
    description: str = Field(..., description="Detailed description")
    priority: SeverityLevel = Field(..., description="Priority level")
    estimated_effort: str = Field(..., description="Estimated effort (hours/days)")
    prerequisites: List[str] = Field(default_factory=list, description="Prerequisites for this step")
    code_changes: Optional[str] = Field(None, description="Specific code changes needed")
    verification_steps: List[str] = Field(default_factory=list, description="How to verify fix")
    resources: List[str] = Field(default_factory=list, description="Helpful resources/links")

class RemediationPlan(DSLModel):
    """Comprehensive remediation plan"""
    plan_id: str = Field(..., description="Unique plan identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    target_completion: datetime = Field(..., description="Target completion date")
    
    immediate_actions: List[RemediationStep] = Field(default_factory=list, description="Immediate critical fixes")
    short_term_actions: List[RemediationStep] = Field(default_factory=list, description="Short-term fixes (1-2 weeks)")
    long_term_actions: List[RemediationStep] = Field(default_factory=list, description="Long-term improvements (1+ months)")
    
    total_estimated_effort: str = Field("", description="Total estimated effort")
    resource_requirements: List[str] = Field(default_factory=list, description="Required resources/skills")

class SecurityReportGenerator:
    """Generates comprehensive security reports"""
    
    def __init__(self):
        self.report_templates = {
            "executive": self._generate_executive_summary,
            "technical": self._generate_technical_report,
            "remediation": self._generate_remediation_report,
            "compliance": self._generate_compliance_report
        }
    
    def generate_comprehensive_report(
        self, 
        engine: RedTeamEngine,
        report_types: List[str] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        
        if report_types is None:
            report_types = ["executive", "technical", "remediation"]
        
        # Calculate risk assessment
        risk_assessment = self._calculate_risk_assessment(engine)
        
        # Generate base report data
        base_report = {
            "report_metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "session_id": engine.session_id,
                "target_path": str(engine.target_path),
                "scan_duration": (engine.end_time - engine.start_time).total_seconds() if engine.end_time else 0,
                "report_version": "1.0"
            },
            "risk_assessment": risk_assessment.dict(),
            "vulnerability_summary": self._generate_vulnerability_summary(engine),
            "attack_vector_analysis": self._generate_attack_vector_analysis(engine)
        }
        
        # Generate requested report sections
        for report_type in report_types:
            if report_type in self.report_templates:
                base_report[f"{report_type}_report"] = self.report_templates[report_type](engine, risk_assessment)
        
        return base_report
    
    def _calculate_risk_assessment(self, engine: RedTeamEngine) -> RiskAssessment:
        """Calculate comprehensive risk assessment"""
        
        # Count vulnerabilities by severity
        severity_counts = {
            SeverityLevel.CRITICAL: 0,
            SeverityLevel.HIGH: 0,
            SeverityLevel.MEDIUM: 0,
            SeverityLevel.LOW: 0,
            SeverityLevel.INFO: 0
        }
        
        for vuln in engine.all_vulnerabilities:
            severity_counts[vuln.severity] += 1
        
        # Calculate weighted risk score
        severity_weights = {
            SeverityLevel.CRITICAL: 10.0,
            SeverityLevel.HIGH: 7.5,
            SeverityLevel.MEDIUM: 5.0,
            SeverityLevel.LOW: 2.5,
            SeverityLevel.INFO: 1.0
        }
        
        total_score = sum(
            count * severity_weights[severity] 
            for severity, count in severity_counts.items()
        )
        
        # Normalize to 0-10 scale
        max_possible = len(engine.all_vulnerabilities) * 10.0 if engine.all_vulnerabilities else 1.0
        overall_risk = min(total_score / max_possible * 10.0, 10.0)
        
        # Identify top risk categories
        category_counts = {}
        for vuln in engine.all_vulnerabilities:
            category_counts[vuln.category.value] = category_counts.get(vuln.category.value, 0) + 1
        
        top_risks = sorted(category_counts.keys(), key=lambda k: category_counts[k], reverse=True)[:5]
        
        # Estimate fix time
        critical_high_count = severity_counts[SeverityLevel.CRITICAL] + severity_counts[SeverityLevel.HIGH]
        if critical_high_count > 10:
            fix_time = "2-4 weeks"
        elif critical_high_count > 5:
            fix_time = "1-2 weeks"
        elif critical_high_count > 0:
            fix_time = "3-7 days"
        else:
            fix_time = "1-3 days"
        
        return RiskAssessment(
            overall_risk_score=overall_risk,
            critical_count=severity_counts[SeverityLevel.CRITICAL],
            high_count=severity_counts[SeverityLevel.HIGH],
            medium_count=severity_counts[SeverityLevel.MEDIUM],
            low_count=severity_counts[SeverityLevel.LOW],
            info_count=severity_counts[SeverityLevel.INFO],
            top_risks=top_risks,
            remediation_priority=self._get_remediation_priority(engine),
            estimated_fix_time=fix_time,
            compliance_impact=self._get_compliance_impact(engine)
        )
    
    def _get_remediation_priority(self, engine: RedTeamEngine) -> List[str]:
        """Get prioritized list of remediation areas"""
        priority_map = {
            AttackType.CODE_INJECTION: 1,
            AttackType.CRYPTOGRAPHIC: 2,
            AttackType.AUTHORIZATION_BYPASS: 3,
            AttackType.AUTHENTICATION_BYPASS: 4,
            AttackType.DATA_EXFILTRATION: 5,
            AttackType.TELEMETRY_LEAK: 6,
            AttackType.SUPPLY_CHAIN: 7,
            AttackType.CONFIGURATION: 8,
            AttackType.DENIAL_OF_SERVICE: 9,
            AttackType.PRIVILEGE_ESCALATION: 10
        }
        
        attack_types = {vuln.attack_type for vuln in engine.all_vulnerabilities}
        return sorted(attack_types, key=lambda at: priority_map.get(at, 99))
    
    def _get_compliance_impact(self, engine: RedTeamEngine) -> List[str]:
        """Identify compliance frameworks that may be impacted"""
        compliance_frameworks = []
        
        # Check for specific vulnerability types that impact compliance
        for vuln in engine.all_vulnerabilities:
            if vuln.category == VulnerabilityCategory.A02_CRYPTOGRAPHIC_FAILURES:
                compliance_frameworks.extend(["SOC 2", "ISO 27001", "NIST"])
            elif vuln.category == VulnerabilityCategory.A01_BROKEN_ACCESS_CONTROL:
                compliance_frameworks.extend(["SOX", "GDPR", "HIPAA"])
            elif vuln.category == VulnerabilityCategory.A09_LOGGING_MONITORING_FAILURES:
                compliance_frameworks.extend(["PCI DSS", "SOC 2"])
        
        return list(set(compliance_frameworks))
    
    def _generate_vulnerability_summary(self, engine: RedTeamEngine) -> Dict[str, Any]:
        """Generate vulnerability summary statistics"""
        
        # Group by various categories
        by_severity = {}
        by_category = {}
        by_attack_type = {}
        by_component = {}
        
        for vuln in engine.all_vulnerabilities:
            # By severity
            by_severity[vuln.severity.value] = by_severity.get(vuln.severity.value, 0) + 1
            
            # By OWASP category
            by_category[vuln.category.value] = by_category.get(vuln.category.value, 0) + 1
            
            # By attack type
            by_attack_type[vuln.attack_type.value] = by_attack_type.get(vuln.attack_type.value, 0) + 1
            
            # By component
            for component in vuln.affected_components:
                by_component[component] = by_component.get(component, 0) + 1
        
        return {
            "total_vulnerabilities": len(engine.all_vulnerabilities),
            "by_severity": by_severity,
            "by_owasp_category": by_category,
            "by_attack_type": by_attack_type,
            "most_affected_components": dict(sorted(by_component.items(), key=lambda x: x[1], reverse=True)[:10])
        }
    
    def _generate_attack_vector_analysis(self, engine: RedTeamEngine) -> Dict[str, Any]:
        """Analyze attack vectors"""
        
        if not engine.all_attack_vectors:
            return {"total_vectors": 0, "analysis": "No attack vectors identified"}
        
        # Calculate average likelihood and detection difficulty
        avg_likelihood = sum(av.likelihood for av in engine.all_attack_vectors) / len(engine.all_attack_vectors)
        avg_detection_difficulty = sum(av.detection_difficulty for av in engine.all_attack_vectors) / len(engine.all_attack_vectors)
        
        # Group by attack type
        by_attack_type = {}
        for av in engine.all_attack_vectors:
            if av.attack_type.value not in by_attack_type:
                by_attack_type[av.attack_type.value] = []
            by_attack_type[av.attack_type.value].append({
                "name": av.name,
                "likelihood": av.likelihood,
                "detection_difficulty": av.detection_difficulty,
                "impact": av.impact
            })
        
        # Find highest risk vectors
        high_risk_vectors = [
            av for av in engine.all_attack_vectors 
            if av.likelihood > 0.7 and av.detection_difficulty > 0.7
        ]
        
        return {
            "total_vectors": len(engine.all_attack_vectors),
            "average_likelihood": avg_likelihood,
            "average_detection_difficulty": avg_detection_difficulty,
            "by_attack_type": by_attack_type,
            "high_risk_vectors": [
                {
                    "name": av.name,
                    "risk_score": av.likelihood * av.detection_difficulty,
                    "impact": av.impact
                }
                for av in high_risk_vectors
            ]
        }
    
    def _generate_executive_summary(self, engine: RedTeamEngine, risk_assessment: RiskAssessment) -> Dict[str, Any]:
        """Generate executive summary report"""
        
        # Key findings
        key_findings = []
        if risk_assessment.critical_count > 0:
            key_findings.append(f"{risk_assessment.critical_count} critical vulnerabilities require immediate attention")
        if risk_assessment.high_count > 0:
            key_findings.append(f"{risk_assessment.high_count} high-severity issues need priority remediation")
        
        # Business impact
        business_impact = []
        if risk_assessment.overall_risk_score >= 7.0:
            business_impact.append("High risk of security breach and data compromise")
            business_impact.append("Potential regulatory compliance violations")
            business_impact.append("Reputational damage risk")
        elif risk_assessment.overall_risk_score >= 4.0:
            business_impact.append("Moderate security risk requiring attention")
            business_impact.append("Some compliance gaps identified")
        
        # Recommendations
        recommendations = []
        if risk_assessment.critical_count > 0:
            recommendations.append("Immediately address all critical vulnerabilities")
        if "injection" in risk_assessment.top_risks:
            recommendations.append("Implement input validation and sanitization")
        if "cryptographic" in risk_assessment.top_risks:
            recommendations.append("Review and strengthen cryptographic implementations")
        
        return {
            "executive_summary": {
                "overall_risk_level": risk_assessment.calculate_risk_level(),
                "risk_score": risk_assessment.overall_risk_score,
                "key_findings": key_findings,
                "business_impact": business_impact,
                "immediate_recommendations": recommendations,
                "estimated_remediation_time": risk_assessment.estimated_fix_time,
                "compliance_impact": risk_assessment.compliance_impact
            }
        }
    
    def _generate_technical_report(self, engine: RedTeamEngine, risk_assessment: RiskAssessment) -> Dict[str, Any]:
        """Generate detailed technical report"""
        
        # Most critical vulnerabilities
        critical_vulns = [
            {
                "id": vuln.vulnerability_id,
                "title": vuln.title,
                "severity": vuln.severity.value,
                "category": vuln.category.value,
                "file": vuln.file_path,
                "line": vuln.line_number,
                "description": vuln.description,
                "remediation": vuln.remediation
            }
            for vuln in sorted(engine.all_vulnerabilities, 
                             key=lambda v: (v.severity == SeverityLevel.CRITICAL, v.cvss_score or 0),
                             reverse=True)[:10]
        ]
        
        # Scanner results
        scanner_results = {}
        for name, scanner in engine.active_scanners.items():
            scanner_results[name] = {
                "vulnerabilities_found": len(scanner.vulnerabilities),
                "risk_score": scanner.calculate_risk_score(),
                "top_findings": [
                    {
                        "title": vuln.title,
                        "severity": vuln.severity.value,
                        "file": vuln.file_path
                    }
                    for vuln in sorted(scanner.vulnerabilities, 
                                     key=lambda v: v.severity.value, reverse=True)[:5]
                ]
            }
        
        return {
            "technical_details": {
                "scan_coverage": engine.scan_coverage,
                "scanner_results": scanner_results,
                "critical_vulnerabilities": critical_vulns,
                "attack_vector_details": [av.dict() for av in engine.all_attack_vectors],
                "vulnerability_distribution": self._generate_vulnerability_summary(engine)
            }
        }
    
    def _generate_remediation_report(self, engine: RedTeamEngine, risk_assessment: RiskAssessment) -> Dict[str, Any]:
        """Generate detailed remediation report"""
        remediation_engine = RemediationEngine()
        plan = remediation_engine.generate_remediation_plan(engine.all_vulnerabilities)
        
        return {
            "remediation_plan": plan.dict(),
            "prioritized_actions": [
                {
                    "vulnerability_id": vuln.vulnerability_id,
                    "title": vuln.title,
                    "priority": vuln.severity.value,
                    "effort_estimate": self._estimate_fix_effort(vuln),
                    "remediation_steps": vuln.remediation
                }
                for vuln in engine.get_remediation_priority()[:20]
            ]
        }
    
    def _generate_compliance_report(self, engine: RedTeamEngine, risk_assessment: RiskAssessment) -> Dict[str, Any]:
        """Generate compliance-focused report"""
        
        # Map vulnerabilities to compliance frameworks
        compliance_mapping = {
            "SOC 2": [],
            "ISO 27001": [], 
            "NIST": [],
            "OWASP": [],
            "PCI DSS": []
        }
        
        for vuln in engine.all_vulnerabilities:
            # Map based on vulnerability category
            if vuln.category == VulnerabilityCategory.A02_CRYPTOGRAPHIC_FAILURES:
                compliance_mapping["SOC 2"].append(vuln.vulnerability_id)
                compliance_mapping["ISO 27001"].append(vuln.vulnerability_id)
                compliance_mapping["NIST"].append(vuln.vulnerability_id)
            elif vuln.category == VulnerabilityCategory.A01_BROKEN_ACCESS_CONTROL:
                compliance_mapping["SOC 2"].append(vuln.vulnerability_id)
                compliance_mapping["ISO 27001"].append(vuln.vulnerability_id)
            # Add more mappings as needed
        
        return {
            "compliance_assessment": {
                "frameworks_impacted": risk_assessment.compliance_impact,
                "vulnerability_mapping": compliance_mapping,
                "compliance_gaps": [
                    f"{len(vulns)} vulnerabilities impact {framework}"
                    for framework, vulns in compliance_mapping.items() if vulns
                ],
                "remediation_priority_by_compliance": [
                    {
                        "framework": framework,
                        "critical_gaps": len([v for v in vulns if any(
                            av.vulnerability_id == v and av.severity == SeverityLevel.CRITICAL 
                            for av in engine.all_vulnerabilities
                        )])
                    }
                    for framework, vulns in compliance_mapping.items() if vulns
                ]
            }
        }
    
    def _estimate_fix_effort(self, vuln: VulnerabilityReport) -> str:
        """Estimate effort required to fix vulnerability"""
        effort_map = {
            SeverityLevel.CRITICAL: "1-3 days",
            SeverityLevel.HIGH: "4-8 hours", 
            SeverityLevel.MEDIUM: "2-4 hours",
            SeverityLevel.LOW: "1-2 hours",
            SeverityLevel.INFO: "30 minutes"
        }
        return effort_map.get(vuln.severity, "2-4 hours")
    
    def save_report(self, report: Dict[str, Any], output_path: Path, format: str = "json"):
        """Save report to file"""
        if format == "json":
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
        elif format == "markdown":
            self._save_markdown_report(report, output_path)
    
    def _save_markdown_report(self, report: Dict[str, Any], output_path: Path):
        """Save report as markdown"""
        md_content = []
        
        # Executive Summary
        if "executive_report" in report:
            exec_report = report["executive_report"]["executive_summary"]
            md_content.append("# Security Assessment Executive Summary\n")
            md_content.append(f"**Overall Risk Level:** {exec_report['overall_risk_level']}\n")
            md_content.append(f"**Risk Score:** {exec_report['risk_score']}/10\n\n")
            
            md_content.append("## Key Findings\n")
            for finding in exec_report["key_findings"]:
                md_content.append(f"- {finding}\n")
            md_content.append("\n")
            
            md_content.append("## Immediate Recommendations\n")
            for rec in exec_report["immediate_recommendations"]:
                md_content.append(f"- {rec}\n")
            md_content.append("\n")
        
        # Risk Assessment
        if "risk_assessment" in report:
            risk = report["risk_assessment"]
            md_content.append("## Risk Assessment\n")
            md_content.append(f"- **Critical:** {risk['critical_count']}\n")
            md_content.append(f"- **High:** {risk['high_count']}\n")
            md_content.append(f"- **Medium:** {risk['medium_count']}\n")
            md_content.append(f"- **Low:** {risk['low_count']}\n\n")
        
        with open(output_path, 'w') as f:
            f.write(''.join(md_content))

class RemediationEngine:
    """Generates detailed remediation plans"""
    
    def generate_remediation_plan(self, vulnerabilities: List[VulnerabilityReport]) -> RemediationPlan:
        """Generate comprehensive remediation plan"""
        
        plan_id = hashlib.md5(f"remediation_{datetime.utcnow()}".encode()).hexdigest()[:16]
        
        # Categorize by urgency
        immediate = [v for v in vulnerabilities if v.severity == SeverityLevel.CRITICAL]
        short_term = [v for v in vulnerabilities if v.severity == SeverityLevel.HIGH]
        long_term = [v for v in vulnerabilities if v.severity in [SeverityLevel.MEDIUM, SeverityLevel.LOW]]
        
        # Generate remediation steps
        immediate_steps = [self._create_remediation_step(v, "immediate") for v in immediate]
        short_term_steps = [self._create_remediation_step(v, "short_term") for v in short_term]
        long_term_steps = [self._create_remediation_step(v, "long_term") for v in long_term]
        
        # Calculate timeline
        immediate_days = len(immediate) * 1  # 1 day per critical
        short_term_days = len(short_term) * 0.5  # 0.5 day per high
        long_term_days = len(long_term) * 0.25  # 0.25 day per medium/low
        
        total_days = immediate_days + short_term_days + long_term_days
        target_completion = datetime.utcnow() + timedelta(days=int(total_days))
        
        return RemediationPlan(
            plan_id=plan_id,
            target_completion=target_completion,
            immediate_actions=immediate_steps,
            short_term_actions=short_term_steps,
            long_term_actions=long_term_steps,
            total_estimated_effort=f"{total_days:.1f} days",
            resource_requirements=self._determine_resource_requirements(vulnerabilities)
        )
    
    def _create_remediation_step(self, vuln: VulnerabilityReport, timeframe: str) -> RemediationStep:
        """Create remediation step for vulnerability"""
        
        step_id = f"step_{vuln.vulnerability_id}"
        
        # Effort estimation
        effort_map = {
            "immediate": {"critical": "4-8 hours", "high": "2-4 hours"},
            "short_term": {"high": "1-2 days", "medium": "4-8 hours"},
            "long_term": {"medium": "1-2 days", "low": "2-4 hours"}
        }
        
        effort = effort_map.get(timeframe, {}).get(vuln.severity.value, "2-4 hours")
        
        # Verification steps
        verification = [
            "Re-run security scanner to confirm fix",
            "Conduct manual testing of affected functionality",
            "Update security documentation"
        ]
        
        if vuln.attack_type == AttackType.CODE_INJECTION:
            verification.append("Test with injection payloads")
        elif vuln.attack_type == AttackType.CRYPTOGRAPHIC:
            verification.append("Validate cryptographic strength")
        
        return RemediationStep(
            step_id=step_id,
            title=f"Fix {vuln.title}",
            description=vuln.description,
            priority=vuln.severity,
            estimated_effort=effort,
            prerequisites=self._get_prerequisites(vuln),
            code_changes=self._get_code_changes(vuln),
            verification_steps=verification,
            resources=self._get_resources(vuln)
        )
    
    def _get_prerequisites(self, vuln: VulnerabilityReport) -> List[str]:
        """Get prerequisites for fixing vulnerability"""
        prerequisites = []
        
        if vuln.attack_type == AttackType.CRYPTOGRAPHIC:
            prerequisites.append("Review cryptographic requirements")
            prerequisites.append("Ensure cryptographic libraries are up to date")
        elif vuln.attack_type == AttackType.CODE_INJECTION:
            prerequisites.append("Identify all user input points")
            prerequisites.append("Review input validation framework")
        
        return prerequisites
    
    def _get_code_changes(self, vuln: VulnerabilityReport) -> Optional[str]:
        """Get specific code changes needed"""
        if vuln.file_path and vuln.line_number:
            return f"Update {vuln.file_path} line {vuln.line_number}: {vuln.remediation}"
        return vuln.remediation
    
    def _get_resources(self, vuln: VulnerabilityReport) -> List[str]:
        """Get helpful resources for remediation"""
        resources = ["https://owasp.org/www-project-top-ten/"]
        
        if vuln.category == VulnerabilityCategory.A02_CRYPTOGRAPHIC_FAILURES:
            resources.append("https://cryptography.io/en/latest/")
        elif vuln.category == VulnerabilityCategory.A03_INJECTION:
            resources.append("https://owasp.org/www-community/Injection_Flaws")
        
        return resources
    
    def _determine_resource_requirements(self, vulnerabilities: List[VulnerabilityReport]) -> List[str]:
        """Determine resource requirements for remediation"""
        requirements = set()
        
        attack_types = {v.attack_type for v in vulnerabilities}
        
        if AttackType.CRYPTOGRAPHIC in attack_types:
            requirements.add("Cryptographic expertise")
        if AttackType.CODE_INJECTION in attack_types:
            requirements.add("Secure coding knowledge")
        if AttackType.TELEMETRY_LEAK in attack_types:
            requirements.add("OTEL/telemetry expertise")
        
        requirements.add("Security testing tools")
        requirements.add("Development environment access")
        
        return list(requirements)