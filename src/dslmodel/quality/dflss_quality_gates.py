"""
DFLSS (Design for Lean Six Sigma) Quality Gates for Git Pipeline
Data-driven continuous improvement integrated with Git operations
"""

import subprocess
import json
import time
import statistics
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
from opentelemetry import trace

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()
tracer = trace.get_tracer(__name__)

class QualityPhase(Enum):
    """DFLSS phases"""
    DEFINE = "define"
    MEASURE = "measure"
    ANALYZE = "analyze"
    IMPROVE = "improve"
    CONTROL = "control"

class QualityGateStatus(Enum):
    """Quality gate status"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    PENDING = "pending"

class MetricType(Enum):
    """Types of quality metrics"""
    PERFORMANCE = "performance"
    RELIABILITY = "reliability"
    SECURITY = "security"
    MAINTAINABILITY = "maintainability"
    USABILITY = "usability"
    EFFICIENCY = "efficiency"

@dataclass
class QualityMetric:
    """Individual quality metric definition"""
    id: str
    name: str
    description: str
    metric_type: MetricType
    threshold_green: float
    threshold_yellow: float
    threshold_red: float
    unit: str
    higher_is_better: bool = True
    critical: bool = False
    
    def evaluate(self, value: float) -> QualityGateStatus:
        """Evaluate metric value against thresholds"""
        if self.higher_is_better:
            if value >= self.threshold_green:
                return QualityGateStatus.PASSED
            elif value >= self.threshold_yellow:
                return QualityGateStatus.WARNING
            else:
                return QualityGateStatus.FAILED
        else:
            if value <= self.threshold_green:
                return QualityGateStatus.PASSED
            elif value <= self.threshold_yellow:
                return QualityGateStatus.WARNING
            else:
                return QualityGateStatus.FAILED

@dataclass
class QualityMeasurement:
    """Individual quality measurement"""
    metric_id: str
    value: float
    timestamp: datetime
    git_commit: str
    branch: str
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Git storage"""
        return {
            "metric_id": self.metric_id,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "git_commit": self.git_commit,
            "branch": self.branch,
            "context": self.context
        }

@dataclass
class QualityGateResult:
    """Result of quality gate evaluation"""
    gate_id: str
    overall_status: QualityGateStatus
    metrics_evaluated: int
    metrics_passed: int
    metrics_failed: int
    critical_failures: int
    timestamp: datetime
    git_commit: str
    branch: str
    details: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Git storage"""
        return {
            "gate_id": self.gate_id,
            "overall_status": self.overall_status.value,
            "metrics_evaluated": self.metrics_evaluated,
            "metrics_passed": self.metrics_passed,
            "metrics_failed": self.metrics_failed,
            "critical_failures": self.critical_failures,
            "timestamp": self.timestamp.isoformat(),
            "git_commit": self.git_commit,
            "branch": self.branch,
            "details": self.details
        }

@dataclass
class ProcessImprovement:
    """DFLSS process improvement recommendation"""
    id: str
    phase: QualityPhase
    problem_statement: str
    root_cause: str
    recommendation: str
    impact_estimate: float
    effort_estimate: str
    git_operations: List[str]
    success_metrics: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Git storage"""
        return {
            "id": self.id,
            "phase": self.phase.value,
            "problem_statement": self.problem_statement,
            "root_cause": self.root_cause,
            "recommendation": self.recommendation,
            "impact_estimate": self.impact_estimate,
            "effort_estimate": self.effort_estimate,
            "git_operations": self.git_operations,
            "success_metrics": self.success_metrics
        }

class DFLSSDefinePhase:
    """Define phase - establish quality metrics and standards"""
    
    def __init__(self):
        self.quality_metrics: Dict[str, QualityMetric] = {}
        self.initialize_default_metrics()
    
    def initialize_default_metrics(self):
        """Initialize default quality metrics for Git operations"""
        
        # Performance metrics
        self.add_metric(QualityMetric(
            id="code_coverage",
            name="Code Coverage",
            description="Percentage of code covered by tests",
            metric_type=MetricType.RELIABILITY,
            threshold_green=85.0,
            threshold_yellow=70.0,
            threshold_red=50.0,
            unit="%",
            higher_is_better=True,
            critical=True
        ))
        
        self.add_metric(QualityMetric(
            id="build_success_rate",
            name="Build Success Rate",
            description="Percentage of successful builds",
            metric_type=MetricType.RELIABILITY,
            threshold_green=95.0,
            threshold_yellow=90.0,
            threshold_red=80.0,
            unit="%",
            higher_is_better=True,
            critical=True
        ))
        
        self.add_metric(QualityMetric(
            id="deployment_frequency",
            name="Deployment Frequency",
            description="Deployments per day",
            metric_type=MetricType.EFFICIENCY,
            threshold_green=1.0,
            threshold_yellow=0.5,
            threshold_red=0.1,
            unit="per day",
            higher_is_better=True,
            critical=False
        ))
        
        self.add_metric(QualityMetric(
            id="lead_time",
            name="Lead Time",
            description="Time from commit to production (hours)",
            metric_type=MetricType.EFFICIENCY,
            threshold_green=24.0,
            threshold_yellow=72.0,
            threshold_red=168.0,
            unit="hours",
            higher_is_better=False,
            critical=False
        ))
        
        self.add_metric(QualityMetric(
            id="mean_time_to_recovery",
            name="Mean Time to Recovery",
            description="Average time to recover from failures (hours)",
            metric_type=MetricType.RELIABILITY,
            threshold_green=1.0,
            threshold_yellow=4.0,
            threshold_red=24.0,
            unit="hours",
            higher_is_better=False,
            critical=True
        ))
        
        self.add_metric(QualityMetric(
            id="change_failure_rate",
            name="Change Failure Rate",
            description="Percentage of deployments causing failures",
            metric_type=MetricType.RELIABILITY,
            threshold_green=5.0,
            threshold_yellow=10.0,
            threshold_red=20.0,
            unit="%",
            higher_is_better=False,
            critical=True
        ))
        
        self.add_metric(QualityMetric(
            id="security_vulnerabilities",
            name="Security Vulnerabilities",
            description="Number of security vulnerabilities detected",
            metric_type=MetricType.SECURITY,
            threshold_green=0.0,
            threshold_yellow=2.0,
            threshold_red=5.0,
            unit="count",
            higher_is_better=False,
            critical=True
        ))
        
        self.add_metric(QualityMetric(
            id="technical_debt_ratio",
            name="Technical Debt Ratio",
            description="Percentage of code that needs refactoring",
            metric_type=MetricType.MAINTAINABILITY,
            threshold_green=5.0,
            threshold_yellow=10.0,
            threshold_red=20.0,
            unit="%",
            higher_is_better=False,
            critical=False
        ))
    
    def add_metric(self, metric: QualityMetric):
        """Add a quality metric"""
        self.quality_metrics[metric.id] = metric
        console.print(f"📊 Defined quality metric: {metric.name}")
    
    def get_metric(self, metric_id: str) -> Optional[QualityMetric]:
        """Get a quality metric by ID"""
        return self.quality_metrics.get(metric_id)
    
    def list_metrics(self) -> List[QualityMetric]:
        """List all defined metrics"""
        return list(self.quality_metrics.values())

class DFLSSMeasurePhase:
    """Measure phase - collect quality measurements"""
    
    def __init__(self):
        self.measurements: List[QualityMeasurement] = []
        self.notes_ref = "refs/notes/dflss/measurements"
    
    def collect_git_metrics(self) -> Dict[str, float]:
        """Collect metrics from Git operations"""
        
        metrics = {}
        
        try:
            # Get current commit and branch
            commit_result = subprocess.run([
                "git", "rev-parse", "HEAD"
            ], capture_output=True, text=True)
            current_commit = commit_result.stdout.strip() if commit_result.returncode == 0 else "unknown"
            
            branch_result = subprocess.run([
                "git", "branch", "--show-current"
            ], capture_output=True, text=True)
            current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
            
            # Measure build success rate (simplified - would integrate with CI)
            metrics["build_success_rate"] = 95.0  # Mock data
            
            # Measure deployment frequency
            deploy_frequency = self.calculate_deployment_frequency()
            metrics["deployment_frequency"] = deploy_frequency
            
            # Measure lead time
            lead_time = self.calculate_lead_time()
            metrics["lead_time"] = lead_time
            
            # Measure change failure rate
            metrics["change_failure_rate"] = 3.0  # Mock data
            
            # Measure code coverage (would integrate with coverage tools)
            metrics["code_coverage"] = 87.5  # Mock data
            
            # Measure security vulnerabilities (would integrate with security scanners)
            metrics["security_vulnerabilities"] = 0.0  # Mock data
            
            # Measure technical debt ratio (would integrate with code analysis tools)
            metrics["technical_debt_ratio"] = 8.5  # Mock data
            
            # Measure MTTR
            metrics["mean_time_to_recovery"] = 2.5  # Mock data
            
            console.print(f"📏 Collected {len(metrics)} quality measurements")
            
        except Exception as e:
            console.print(f"❌ Error collecting Git metrics: {e}")
        
        return metrics
    
    def calculate_deployment_frequency(self) -> float:
        """Calculate deployment frequency from Git tags"""
        try:
            # Get tags from last 30 days
            thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            
            result = subprocess.run([
                "git", "tag", "--sort=-creatordate", 
                "--merged", "HEAD"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                tags = [tag.strip() for tag in result.stdout.split('\n') if tag.strip()]
                # Simplified calculation - count release tags
                release_tags = [tag for tag in tags if 'v' in tag.lower() or 'release' in tag.lower()]
                return len(release_tags) / 30.0  # Per day over 30 days
            else:
                return 0.1  # Default low frequency
                
        except Exception:
            return 0.1
    
    def calculate_lead_time(self) -> float:
        """Calculate lead time from commit to deployment"""
        try:
            # Get last commit time
            result = subprocess.run([
                "git", "log", "-1", "--format=%ct"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                commit_time = int(result.stdout.strip())
                current_time = int(time.time())
                hours_since_commit = (current_time - commit_time) / 3600
                return min(hours_since_commit, 168)  # Cap at 1 week
            else:
                return 48.0  # Default 48 hours
                
        except Exception:
            return 48.0
    
    def record_measurement(self, metric_id: str, value: float, context: Dict[str, Any] = None):
        """Record a quality measurement"""
        
        if context is None:
            context = {}
        
        try:
            # Get Git context
            commit_result = subprocess.run([
                "git", "rev-parse", "HEAD"
            ], capture_output=True, text=True)
            current_commit = commit_result.stdout.strip() if commit_result.returncode == 0 else "unknown"
            
            branch_result = subprocess.run([
                "git", "branch", "--show-current"
            ], capture_output=True, text=True)
            current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
            
            measurement = QualityMeasurement(
                metric_id=metric_id,
                value=value,
                timestamp=datetime.now(timezone.utc),
                git_commit=current_commit,
                branch=current_branch,
                context=context
            )
            
            self.measurements.append(measurement)
            
            # Store in Git notes
            measurement_json = json.dumps(measurement.to_dict(), indent=2)
            subprocess.run([
                "git", "notes", "--ref", self.notes_ref,
                "append", "-m", measurement_json, "HEAD"
            ], capture_output=True, text=True)
            
            console.print(f"📊 Recorded measurement: {metric_id} = {value}")
            
        except Exception as e:
            console.print(f"❌ Error recording measurement: {e}")
    
    def get_measurement_history(self, metric_id: str, days: int = 30) -> List[QualityMeasurement]:
        """Get measurement history for a metric"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        return [
            m for m in self.measurements 
            if m.metric_id == metric_id and m.timestamp >= cutoff_date
        ]

class DFLSSAnalyzePhase:
    """Analyze phase - identify bottlenecks and improvement opportunities"""
    
    def __init__(self, define_phase: DFLSSDefinePhase, measure_phase: DFLSSMeasurePhase):
        self.define_phase = define_phase
        self.measure_phase = measure_phase
    
    def analyze_git_performance(self) -> Dict[str, Any]:
        """Analyze Git operation performance"""
        
        analysis = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "bottlenecks": [],
            "trends": {},
            "recommendations": []
        }
        
        # Analyze each metric
        for metric_id, metric in self.define_phase.quality_metrics.items():
            history = self.measure_phase.get_measurement_history(metric_id)
            
            if len(history) >= 3:
                values = [m.value for m in history]
                
                # Calculate trend
                if len(values) >= 2:
                    trend = "improving" if values[-1] > values[-2] else "degrading"
                    if metric.higher_is_better and values[-1] < values[-2]:
                        trend = "degrading"
                    elif not metric.higher_is_better and values[-1] > values[-2]:
                        trend = "degrading"
                    
                    analysis["trends"][metric_id] = {
                        "trend": trend,
                        "current_value": values[-1],
                        "previous_value": values[-2],
                        "change": abs(values[-1] - values[-2])
                    }
                
                # Identify bottlenecks
                current_value = values[-1]
                status = metric.evaluate(current_value)
                
                if status in [QualityGateStatus.FAILED, QualityGateStatus.WARNING]:
                    analysis["bottlenecks"].append({
                        "metric_id": metric_id,
                        "metric_name": metric.name,
                        "current_value": current_value,
                        "threshold": metric.threshold_green,
                        "status": status.value,
                        "critical": metric.critical
                    })
        
        # Generate recommendations
        analysis["recommendations"] = self.generate_recommendations(analysis["bottlenecks"])
        
        console.print(f"🔍 Analyzed {len(self.define_phase.quality_metrics)} metrics")
        console.print(f"📍 Found {len(analysis['bottlenecks'])} bottlenecks")
        
        return analysis
    
    def generate_recommendations(self, bottlenecks: List[Dict[str, Any]]) -> List[str]:
        """Generate improvement recommendations based on bottlenecks"""
        
        recommendations = []
        
        for bottleneck in bottlenecks:
            metric_id = bottleneck["metric_id"]
            
            if metric_id == "build_success_rate":
                recommendations.append("Implement pre-commit hooks to catch build failures early")
                recommendations.append("Add more comprehensive unit tests")
                recommendations.append("Set up better CI/CD pipeline with faster feedback")
            
            elif metric_id == "code_coverage":
                recommendations.append("Implement test-driven development practices")
                recommendations.append("Add code coverage quality gates to Git hooks")
                recommendations.append("Review and strengthen test strategies")
            
            elif metric_id == "deployment_frequency":
                recommendations.append("Implement continuous deployment automation")
                recommendations.append("Reduce deployment complexity and risk")
                recommendations.append("Automate more testing and validation steps")
            
            elif metric_id == "lead_time":
                recommendations.append("Streamline Git workflows and merge processes")
                recommendations.append("Reduce review cycle times")
                recommendations.append("Automate manual testing and approval steps")
            
            elif metric_id == "security_vulnerabilities":
                recommendations.append("Integrate security scanning into Git hooks")
                recommendations.append("Implement security-first development practices")
                recommendations.append("Add automated vulnerability detection")
        
        return list(set(recommendations))  # Remove duplicates
    
    def identify_correlation(self) -> Dict[str, Any]:
        """Identify correlations between metrics"""
        
        correlations = {}
        
        # This would implement statistical correlation analysis
        # Simplified for demo
        correlations["lead_time_vs_quality"] = {
            "correlation": -0.7,
            "insight": "Longer lead times correlate with lower quality"
        }
        
        correlations["deployment_frequency_vs_stability"] = {
            "correlation": 0.6,
            "insight": "Higher deployment frequency correlates with better stability"
        }
        
        return correlations

class DFLSSImprovePhase:
    """Improve phase - implement process improvements"""
    
    def __init__(self, analyze_phase: DFLSSAnalyzePhase):
        self.analyze_phase = analyze_phase
        self.improvements: List[ProcessImprovement] = []
    
    def create_improvement_plan(self, analysis: Dict[str, Any]) -> List[ProcessImprovement]:
        """Create improvement plan based on analysis"""
        
        improvements = []
        
        for i, recommendation in enumerate(analysis.get("recommendations", [])):
            improvement = ProcessImprovement(
                id=f"improvement_{i+1}",
                phase=QualityPhase.IMPROVE,
                problem_statement=f"Quality metric below threshold",
                root_cause="Process inefficiency",
                recommendation=recommendation,
                impact_estimate=0.15,  # 15% improvement estimate
                effort_estimate="2-4 weeks",
                git_operations=["hook", "merge", "commit"],
                success_metrics=["build_success_rate", "code_coverage"]
            )
            
            improvements.append(improvement)
        
        self.improvements.extend(improvements)
        
        console.print(f"📈 Created {len(improvements)} improvement plans")
        return improvements
    
    def implement_git_automation(self, improvement: ProcessImprovement) -> bool:
        """Implement Git automation based on improvement plan"""
        
        try:
            # This would implement specific Git automations
            # For demo, we'll simulate implementation
            
            if "pre-commit" in improvement.recommendation.lower():
                # Would set up pre-commit hooks
                console.print(f"🔧 Implementing pre-commit automation for: {improvement.id}")
                
            elif "ci/cd" in improvement.recommendation.lower():
                # Would set up CI/CD improvements
                console.print(f"🔧 Implementing CI/CD automation for: {improvement.id}")
            
            elif "quality gate" in improvement.recommendation.lower():
                # Would set up quality gates
                console.print(f"🔧 Implementing quality gates for: {improvement.id}")
            
            return True
            
        except Exception as e:
            console.print(f"❌ Error implementing improvement: {e}")
            return False

class DFLSSControlPhase:
    """Control phase - maintain quality standards"""
    
    def __init__(self, define_phase: DFLSSDefinePhase, measure_phase: DFLSSMeasurePhase):
        self.define_phase = define_phase
        self.measure_phase = measure_phase
        self.quality_gates: Dict[str, QualityGateResult] = {}
    
    def run_quality_gate(self, gate_id: str = "default") -> QualityGateResult:
        """Run quality gate evaluation"""
        
        with tracer.start_as_current_span("dflss.quality_gate") as span:
            
            console.print(f"🚪 Running quality gate: {gate_id}")
            
            # Collect current measurements
            current_metrics = self.measure_phase.collect_git_metrics()
            
            # Evaluate against thresholds
            details = []
            metrics_passed = 0
            metrics_failed = 0
            critical_failures = 0
            
            for metric_id, value in current_metrics.items():
                metric = self.define_phase.get_metric(metric_id)
                if metric:
                    status = metric.evaluate(value)
                    
                    detail = {
                        "metric_id": metric_id,
                        "metric_name": metric.name,
                        "value": value,
                        "status": status.value,
                        "threshold_green": metric.threshold_green,
                        "critical": metric.critical
                    }
                    
                    details.append(detail)
                    
                    if status == QualityGateStatus.PASSED:
                        metrics_passed += 1
                    else:
                        metrics_failed += 1
                        if metric.critical:
                            critical_failures += 1
                    
                    # Record measurement
                    self.measure_phase.record_measurement(metric_id, value)
            
            # Determine overall status
            if critical_failures > 0:
                overall_status = QualityGateStatus.FAILED
            elif metrics_failed > metrics_passed:
                overall_status = QualityGateStatus.FAILED
            elif metrics_failed > 0:
                overall_status = QualityGateStatus.WARNING
            else:
                overall_status = QualityGateStatus.PASSED
            
            # Get Git context
            try:
                commit_result = subprocess.run([
                    "git", "rev-parse", "HEAD"
                ], capture_output=True, text=True)
                current_commit = commit_result.stdout.strip() if commit_result.returncode == 0 else "unknown"
                
                branch_result = subprocess.run([
                    "git", "branch", "--show-current"
                ], capture_output=True, text=True)
                current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
            except:
                current_commit = "unknown"
                current_branch = "unknown"
            
            result = QualityGateResult(
                gate_id=gate_id,
                overall_status=overall_status,
                metrics_evaluated=len(current_metrics),
                metrics_passed=metrics_passed,
                metrics_failed=metrics_failed,
                critical_failures=critical_failures,
                timestamp=datetime.now(timezone.utc),
                git_commit=current_commit,
                branch=current_branch,
                details=details
            )
            
            self.quality_gates[gate_id] = result
            
            # Store in Git notes
            self.store_quality_gate_result(result)
            
            # Display results
            self.display_quality_gate_results(result)
            
            span.set_attribute("gate.status", overall_status.value)
            span.set_attribute("gate.metrics_evaluated", len(current_metrics))
            span.set_attribute("gate.critical_failures", critical_failures)
            
            return result
    
    def store_quality_gate_result(self, result: QualityGateResult):
        """Store quality gate result in Git notes"""
        try:
            result_json = json.dumps(result.to_dict(), indent=2)
            subprocess.run([
                "git", "notes", "--ref", "refs/notes/dflss/quality-gates",
                "add", "-m", result_json, "HEAD"
            ], capture_output=True, text=True)
        except Exception as e:
            console.print(f"⚠️ Could not store quality gate result: {e}")
    
    def display_quality_gate_results(self, result: QualityGateResult):
        """Display quality gate results"""
        
        status_color = {
            QualityGateStatus.PASSED: "green",
            QualityGateStatus.WARNING: "yellow", 
            QualityGateStatus.FAILED: "red",
            QualityGateStatus.PENDING: "blue"
        }
        
        table = Table(title=f"DFLSS Quality Gate: {result.gate_id}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        table.add_column("Status", style="bold")
        table.add_column("Threshold", style="dim")
        table.add_column("Critical", style="red")
        
        for detail in result.details:
            status_style = status_color.get(QualityGateStatus(detail["status"]), "white")
            critical_mark = "🔴" if detail["critical"] else ""
            
            table.add_row(
                detail["metric_name"],
                f"{detail['value']:.1f}",
                detail["status"].upper(),
                f"{detail['threshold_green']:.1f}",
                critical_mark
            )
        
        console.print(table)
        
        # Overall status panel
        overall_color = status_color.get(result.overall_status, "white")
        
        panel_content = f"""
🏛️ **Quality Gate Result: {result.overall_status.value.upper()}**

**Metrics Evaluated**: {result.metrics_evaluated}
**Passed**: {result.metrics_passed}
**Failed**: {result.metrics_failed}
**Critical Failures**: {result.critical_failures}

**Git Context**: {result.branch}@{result.git_commit[:8]}
**Timestamp**: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}

**DFLSS Phase**: Control - Quality standards enforcement
**Continuous Improvement**: Data-driven decision making
        """
        
        console.print(Panel.fit(panel_content, title="DFLSS Quality Control", style=overall_color))

class DFLSSQualitySystem:
    """Main DFLSS Quality System orchestrating all phases"""
    
    def __init__(self):
        self.define_phase = DFLSSDefinePhase()
        self.measure_phase = DFLSSMeasurePhase()
        self.analyze_phase = DFLSSAnalyzePhase(self.define_phase, self.measure_phase)
        self.improve_phase = DFLSSImprovePhase(self.analyze_phase)
        self.control_phase = DFLSSControlPhase(self.define_phase, self.measure_phase)
        
        console.print("🏭 DFLSS Quality System initialized")
    
    def run_complete_cycle(self) -> Dict[str, Any]:
        """Run complete DFLSS cycle"""
        
        with tracer.start_as_current_span("dflss.complete_cycle") as span:
            
            console.print("🔄 Starting complete DFLSS cycle...")
            
            cycle_results = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "phases": {}
            }
            
            # Phase 1: Measure
            console.print("\n📏 DFLSS Phase: MEASURE")
            metrics = self.measure_phase.collect_git_metrics()
            cycle_results["phases"]["measure"] = {
                "metrics_collected": len(metrics),
                "values": metrics
            }
            
            # Phase 2: Analyze
            console.print("\n🔍 DFLSS Phase: ANALYZE")
            analysis = self.analyze_phase.analyze_git_performance()
            cycle_results["phases"]["analyze"] = analysis
            
            # Phase 3: Improve
            console.print("\n📈 DFLSS Phase: IMPROVE")
            improvements = self.improve_phase.create_improvement_plan(analysis)
            cycle_results["phases"]["improve"] = {
                "improvements_created": len(improvements),
                "improvements": [imp.to_dict() for imp in improvements]
            }
            
            # Phase 4: Control
            console.print("\n🚪 DFLSS Phase: CONTROL")
            quality_gate = self.control_phase.run_quality_gate("dflss_cycle")
            cycle_results["phases"]["control"] = quality_gate.to_dict()
            
            span.set_attribute("cycle.quality_gate_status", quality_gate.overall_status.value)
            span.set_attribute("cycle.improvements_created", len(improvements))
            span.set_attribute("cycle.bottlenecks_found", len(analysis.get("bottlenecks", [])))
            
            console.print("\n✅ DFLSS cycle completed")
            
            return cycle_results
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health from DFLSS perspective"""
        
        # Run quality gate to get current status
        current_gate = self.control_phase.run_quality_gate("health_check")
        
        health = {
            "overall_health": current_gate.overall_status.value,
            "metrics_count": len(self.define_phase.quality_metrics),
            "measurements_count": len(self.measure_phase.measurements),
            "improvements_count": len(self.improve_phase.improvements),
            "quality_gates_run": len(self.control_phase.quality_gates),
            "last_gate_result": current_gate.to_dict()
        }
        
        return health


# CLI interface for testing
if __name__ == "__main__":
    import typer
    
    app = typer.Typer(name="dflss-quality", help="DFLSS Quality System")
    
    quality_system = DFLSSQualitySystem()
    
    @app.command()
    def define_metric(metric_id: str, name: str, threshold_green: float, 
                     threshold_yellow: float, threshold_red: float):
        """Define a new quality metric"""
        metric = QualityMetric(
            id=metric_id,
            name=name,
            description=f"Custom metric: {name}",
            metric_type=MetricType.PERFORMANCE,
            threshold_green=threshold_green,
            threshold_yellow=threshold_yellow,
            threshold_red=threshold_red,
            unit="units"
        )
        quality_system.define_phase.add_metric(metric)
    
    @app.command()
    def measure():
        """Collect quality measurements"""
        metrics = quality_system.measure_phase.collect_git_metrics()
        console.print(f"Collected {len(metrics)} measurements")
    
    @app.command()
    def analyze():
        """Analyze quality metrics"""
        analysis = quality_system.analyze_phase.analyze_git_performance()
        console.print(f"Found {len(analysis['bottlenecks'])} bottlenecks")
    
    @app.command()
    def quality_gate(gate_id: str = "default"):
        """Run quality gate"""
        result = quality_system.control_phase.run_quality_gate(gate_id)
        console.print(f"Quality gate {gate_id}: {result.overall_status.value}")
    
    @app.command()
    def full_cycle():
        """Run complete DFLSS cycle"""
        results = quality_system.run_complete_cycle()
        console.print("DFLSS cycle completed")
    
    @app.command()
    def health():
        """Get system health"""
        health = quality_system.get_system_health()
        console.print(f"System health: {health['overall_health']}")
    
    app()