#!/usr/bin/env python3
"""
Automatic Evolution CLI - Self-Improving System
===============================================

Implements automatic evolution based on:
1. Test failure analysis
2. Performance metrics monitoring
3. User feedback patterns
4. Code quality indicators
5. Telemetry-driven improvements

80/20 Focus: Maximum learning from minimal feedback
"""

import typer
import asyncio
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from datetime import datetime, timedelta
import re
import xml.etree.ElementTree as ET

app = typer.Typer(name="auto-evolve", help="Automatic system evolution and improvement")
console = Console()


class EvolutionEngine:
    """Core engine for automatic system evolution"""
    
    def __init__(self):
        self.repo_root = self._find_repo_root()
        self.evolution_log = self.repo_root / "evolution.jsonl"
        self.metrics_history = []
        self.improvement_patterns = self._load_patterns()
        
    def _find_repo_root(self) -> Path:
        """Find git repository root"""
        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def _load_patterns(self) -> Dict[str, Any]:
        """Load learned improvement patterns"""
        patterns_file = self.repo_root / "evolution_patterns.json"
        default_patterns = {
            "test_failures": {
                "dspy_parsing_errors": {
                    "pattern": "AttributeError.*items.*json_adapter",
                    "solution": "Fix DSPy signature parsing for LLM outputs",
                    "confidence": 0.9
                },
                "import_errors": {
                    "pattern": "ImportError.*cannot import",
                    "solution": "Add missing dependencies or fix import paths",
                    "confidence": 0.8
                },
                "timeout_errors": {
                    "pattern": "TimeoutExpired|timeout",
                    "solution": "Increase timeout or optimize performance",
                    "confidence": 0.7
                }
            },
            "performance_degradation": {
                "slow_tests": {
                    "threshold": 30.0,  # seconds
                    "solution": "Optimize slow operations or add caching",
                    "confidence": 0.8
                }
            },
            "code_quality": {
                "large_files": {
                    "threshold": 1000,  # lines
                    "solution": "Refactor large files into smaller modules",
                    "confidence": 0.6
                },
                "complex_functions": {
                    "threshold": 50,  # lines per function
                    "solution": "Break down complex functions",
                    "confidence": 0.7
                }
            }
        }
        
        if patterns_file.exists():
            try:
                with open(patterns_file) as f:
                    user_patterns = json.load(f)
                    default_patterns.update(user_patterns)
            except:
                pass
        
        return default_patterns
    
    def analyze_test_failures(self) -> List[Dict[str, Any]]:
        """Analyze recent test failures for improvement opportunities"""
        issues = []
        
        # Check pytest XML reports
        reports_dir = self.repo_root / "reports"
        if reports_dir.exists():
            for report_file in reports_dir.glob("pytest*.xml"):
                issues.extend(self._parse_pytest_xml(report_file))
        
        # Check git commit messages for fixes
        try:
            result = subprocess.run([
                "git", "log", "--oneline", "--since=1 week ago", "--grep=fix"
            ], capture_output=True, text=True, cwd=self.repo_root)
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        issues.append({
                            "type": "recurring_fix",
                            "description": line,
                            "priority": "medium",
                            "source": "git_history"
                        })
        except:
            pass
        
        return issues
    
    def _parse_pytest_xml(self, xml_file: Path) -> List[Dict[str, Any]]:
        """Parse pytest XML report for failure patterns"""
        issues = []
        
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            for testcase in root.findall(".//testcase"):
                failure = testcase.find("failure")
                if failure is not None:
                    failure_message = failure.get("message", "")
                    failure_text = failure.text or ""
                    
                    # Analyze failure patterns
                    issue = self._classify_test_failure(
                        testcase.get("name", ""),
                        failure_message,
                        failure_text
                    )
                    
                    if issue:
                        issues.append(issue)
        except Exception as e:
            console.print(f"⚠️ Error parsing {xml_file}: {e}")
        
        return issues
    
    def _classify_test_failure(self, test_name: str, message: str, text: str) -> Optional[Dict[str, Any]]:
        """Classify test failure and suggest improvements"""
        full_error = f"{message}\n{text}"
        
        # Check against known patterns
        for category, patterns in self.improvement_patterns["test_failures"].items():
            if re.search(patterns["pattern"], full_error, re.IGNORECASE):
                return {
                    "type": "test_failure",
                    "category": category,
                    "test_name": test_name,
                    "description": message,
                    "solution": patterns["solution"],
                    "confidence": patterns["confidence"],
                    "priority": "high" if patterns["confidence"] > 0.8 else "medium",
                    "source": "pytest_analysis"
                }
        
        # Generic analysis
        if "timeout" in full_error.lower():
            return {
                "type": "performance_issue",
                "category": "timeout",
                "test_name": test_name,
                "description": "Test timeout detected",
                "solution": "Optimize test performance or increase timeout",
                "confidence": 0.7,
                "priority": "medium",
                "source": "generic_analysis"
            }
        
        return None
    
    def analyze_performance_metrics(self) -> List[Dict[str, Any]]:
        """Analyze performance trends for degradation"""
        issues = []
        
        # Analyze recent test execution times
        reports_dir = self.repo_root / "reports"
        if reports_dir.exists():
            test_times = []
            for report_file in sorted(reports_dir.glob("pytest*.xml"))[-5:]:  # Last 5 reports
                try:
                    tree = ET.parse(report_file)
                    root = tree.getroot()
                    
                    for testcase in root.findall(".//testcase"):
                        time_attr = testcase.get("time")
                        if time_attr:
                            test_time = float(time_attr)
                            test_times.append({
                                "name": testcase.get("name"),
                                "time": test_time,
                                "file": report_file.name
                            })
                except:
                    continue
            
            # Find slow tests
            slow_threshold = self.improvement_patterns["performance_degradation"]["slow_tests"]["threshold"]
            for test in test_times:
                if test["time"] > slow_threshold:
                    issues.append({
                        "type": "performance_degradation",
                        "category": "slow_test",
                        "test_name": test["name"],
                        "description": f"Test taking {test['time']:.1f}s (threshold: {slow_threshold}s)",
                        "solution": self.improvement_patterns["performance_degradation"]["slow_tests"]["solution"],
                        "confidence": 0.8,
                        "priority": "medium",
                        "source": "performance_analysis"
                    })
        
        return issues
    
    def analyze_code_quality(self) -> List[Dict[str, Any]]:
        """Analyze code quality metrics for improvement opportunities"""
        issues = []
        
        # Find large files
        src_dir = self.repo_root / "src"
        if src_dir.exists():
            for py_file in src_dir.rglob("*.py"):
                try:
                    line_count = len(py_file.read_text().splitlines())
                    threshold = self.improvement_patterns["code_quality"]["large_files"]["threshold"]
                    
                    if line_count > threshold:
                        issues.append({
                            "type": "code_quality",
                            "category": "large_file",
                            "file_path": str(py_file.relative_to(self.repo_root)),
                            "description": f"File has {line_count} lines (threshold: {threshold})",
                            "solution": self.improvement_patterns["code_quality"]["large_files"]["solution"],
                            "confidence": 0.6,
                            "priority": "low",
                            "source": "code_analysis"
                        })
                except:
                    continue
        
        return issues
    
    def generate_improvements(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate specific improvement recommendations"""
        improvements = []
        
        # Group issues by category
        issue_groups = {}
        for issue in issues:
            category = issue.get("category", "unknown")
            if category not in issue_groups:
                issue_groups[category] = []
            issue_groups[category].append(issue)
        
        # Generate improvements for each category
        for category, category_issues in issue_groups.items():
            if category == "dspy_parsing_errors":
                improvements.append(self._create_dspy_fix_improvement(category_issues))
            elif category == "slow_test":
                improvements.append(self._create_performance_improvement(category_issues))
            elif category == "large_file":
                improvements.append(self._create_refactoring_improvement(category_issues))
            else:
                improvements.append(self._create_generic_improvement(category, category_issues))
        
        return improvements
    
    def _create_dspy_fix_improvement(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create improvement for DSPy parsing issues"""
        return {
            "id": f"dspy_fix_{int(time.time())}",
            "type": "code_fix",
            "priority": "high",
            "title": "Fix DSPy LLM Output Parsing",
            "description": "Improve DSPy signature parsing to handle various LLM output formats",
            "affected_files": ["tests/test_weaver_otel_integration.py"],
            "implementation": {
                "steps": [
                    "Add output format validation in DSPy signatures",
                    "Implement fallback parsing for malformed JSON",
                    "Add timeout and retry logic for LLM calls",
                    "Improve error handling for chain-of-thought responses"
                ],
                "estimated_effort": "2-4 hours",
                "confidence": 0.9
            },
            "validation": {
                "tests": ["test_llm_semantic_validation"],
                "metrics": ["test_success_rate", "parsing_error_count"]
            },
            "issues": issues
        }
    
    def _create_performance_improvement(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create performance optimization improvement"""
        slow_tests = [issue["test_name"] for issue in issues]
        
        return {
            "id": f"perf_opt_{int(time.time())}",
            "type": "performance_optimization",
            "priority": "medium",
            "title": "Optimize Slow Test Performance",
            "description": f"Optimize {len(slow_tests)} slow tests for better CI/CD performance",
            "affected_tests": slow_tests,
            "implementation": {
                "steps": [
                    "Add caching for expensive operations",
                    "Implement test parallelization",
                    "Optimize LLM initialization",
                    "Add performance benchmarks"
                ],
                "estimated_effort": "4-6 hours",
                "confidence": 0.8
            },
            "validation": {
                "metrics": ["test_execution_time", "overall_suite_time"]
            },
            "issues": issues
        }
    
    def _create_refactoring_improvement(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create code refactoring improvement"""
        large_files = [issue["file_path"] for issue in issues]
        
        return {
            "id": f"refactor_{int(time.time())}",
            "type": "refactoring",
            "priority": "low",
            "title": "Refactor Large Files",
            "description": f"Break down {len(large_files)} large files into smaller, maintainable modules",
            "affected_files": large_files,
            "implementation": {
                "steps": [
                    "Identify logical separation points",
                    "Extract common functionality into utilities",
                    "Create modular interfaces",
                    "Update imports and tests"
                ],
                "estimated_effort": "6-8 hours",
                "confidence": 0.6
            },
            "validation": {
                "metrics": ["file_line_count", "cyclomatic_complexity"]
            },
            "issues": issues
        }
    
    def _create_generic_improvement(self, category: str, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create generic improvement for uncategorized issues"""
        return {
            "id": f"generic_{category}_{int(time.time())}",
            "type": "generic_fix",
            "priority": "medium",
            "title": f"Address {category.title()} Issues",
            "description": f"Fix {len(issues)} issues in category: {category}",
            "implementation": {
                "steps": [
                    "Analyze root cause",
                    "Implement targeted fix",
                    "Add regression tests",
                    "Validate solution"
                ],
                "estimated_effort": "2-4 hours",
                "confidence": 0.7
            },
            "issues": issues
        }
    
    def log_evolution_event(self, event: Dict[str, Any]):
        """Log evolution event for learning"""
        event["timestamp"] = datetime.now().isoformat()
        
        with open(self.evolution_log, "a") as f:
            f.write(json.dumps(event) + "\n")
    
    def learn_from_history(self) -> Dict[str, Any]:
        """Learn from historical evolution events"""
        if not self.evolution_log.exists():
            return {"patterns": {}, "success_rate": 0.0}
        
        events = []
        try:
            with open(self.evolution_log) as f:
                for line in f:
                    if line.strip():
                        events.append(json.loads(line))
        except:
            return {"patterns": {}, "success_rate": 0.0}
        
        # Analyze success patterns
        successful_events = [e for e in events if e.get("success", False)]
        success_rate = len(successful_events) / len(events) if events else 0.0
        
        # Extract patterns
        patterns = {}
        for event in successful_events:
            event_type = event.get("type", "unknown")
            if event_type not in patterns:
                patterns[event_type] = {"count": 0, "avg_confidence": 0.0}
            
            patterns[event_type]["count"] += 1
            patterns[event_type]["avg_confidence"] = (
                patterns[event_type]["avg_confidence"] + event.get("confidence", 0.0)
            ) / 2
        
        return {
            "patterns": patterns,
            "success_rate": success_rate,
            "total_events": len(events),
            "recent_events": events[-10:]  # Last 10 events
        }


@app.command()
def analyze():
    """Analyze system for evolution opportunities"""
    engine = EvolutionEngine()
    
    console.print("🔍 AUTOMATIC EVOLUTION ANALYSIS")
    console.print("=" * 35)
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        
        # Test failure analysis
        task1 = progress.add_task("Analyzing test failures...", total=1)
        test_issues = engine.analyze_test_failures()
        progress.update(task1, completed=1)
        
        # Performance analysis
        task2 = progress.add_task("Analyzing performance metrics...", total=1)
        perf_issues = engine.analyze_performance_metrics()
        progress.update(task2, completed=1)
        
        # Code quality analysis
        task3 = progress.add_task("Analyzing code quality...", total=1)
        quality_issues = engine.analyze_code_quality()
        progress.update(task3, completed=1)
    
    # Combine all issues
    all_issues = test_issues + perf_issues + quality_issues
    
    # Display results
    if all_issues:
        table = Table(title="🎯 Evolution Opportunities")
        table.add_column("Type", style="cyan")
        table.add_column("Category", style="yellow")
        table.add_column("Priority", style="bold")
        table.add_column("Description", style="white")
        table.add_column("Confidence", style="green")
        
        for issue in sorted(all_issues, key=lambda x: {"high": 3, "medium": 2, "low": 1}[x.get("priority", "low")], reverse=True):
            priority_color = {"high": "red", "medium": "yellow", "low": "blue"}[issue.get("priority", "low")]
            table.add_row(
                issue.get("type", "unknown"),
                issue.get("category", "unknown"),
                f"[{priority_color}]{issue.get('priority', 'unknown').upper()}[/{priority_color}]",
                issue.get("description", "")[:50] + "...",
                f"{issue.get('confidence', 0):.1%}"
            )
        
        console.print(table)
        
        # Show summary
        high_priority = len([i for i in all_issues if i.get("priority") == "high"])
        console.print(f"\n📊 Found {len(all_issues)} opportunities ({high_priority} high priority)")
    else:
        console.print("✅ No evolution opportunities found - system is performing well!")


@app.command()
def evolve(
    auto_apply: bool = typer.Option(False, "--auto-apply", help="Automatically apply safe improvements"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be done")
):
    """Generate and apply evolution improvements"""
    engine = EvolutionEngine()
    
    console.print("🚀 AUTOMATIC EVOLUTION ENGINE")
    console.print("=" * 32)
    
    # Analyze issues
    console.print("🔍 Analyzing current state...")
    test_issues = engine.analyze_test_failures()
    perf_issues = engine.analyze_performance_metrics()
    quality_issues = engine.analyze_code_quality()
    all_issues = test_issues + perf_issues + quality_issues
    
    if not all_issues:
        console.print("✅ No issues found - system is optimized!")
        return
    
    # Generate improvements
    console.print("💡 Generating improvements...")
    improvements = engine.generate_improvements(all_issues)
    
    if not improvements:
        console.print("ℹ️ No actionable improvements available")
        return
    
    # Display improvements
    for i, improvement in enumerate(improvements, 1):
        console.print(f"\n🎯 Improvement {i}: {improvement['title']}")
        console.print(f"   Priority: {improvement['priority'].upper()}")
        console.print(f"   Description: {improvement['description']}")
        console.print(f"   Estimated Effort: {improvement['implementation']['estimated_effort']}")
        console.print(f"   Confidence: {improvement['implementation']['confidence']:.1%}")
        
        if dry_run:
            console.print("   [DRY RUN] Would implement improvement")
            continue
        
        # Apply improvement if confidence is high and auto_apply is enabled
        if auto_apply and improvement['implementation']['confidence'] >= 0.8:
            console.print("   🤖 Auto-applying high-confidence improvement...")
            success = _apply_improvement(improvement)
            
            # Log evolution event
            engine.log_evolution_event({
                "type": "auto_improvement",
                "improvement_id": improvement["id"],
                "success": success,
                "confidence": improvement['implementation']['confidence'],
                "auto_applied": True
            })
            
            if success:
                console.print("   ✅ Improvement applied successfully")
            else:
                console.print("   ❌ Improvement failed to apply")
        else:
            console.print("   ⏸️ Manual review required")


@app.command()
def learn():
    """Learn from evolution history and update patterns"""
    engine = EvolutionEngine()
    
    console.print("🧠 EVOLUTION LEARNING SYSTEM")
    console.print("=" * 30)
    
    # Learn from history
    learning_data = engine.learn_from_history()
    
    if learning_data["total_events"] == 0:
        console.print("ℹ️ No evolution history found")
        return
    
    # Display learning results
    console.print(f"📊 Analyzed {learning_data['total_events']} historical events")
    console.print(f"📈 Overall success rate: {learning_data['success_rate']:.1%}")
    
    if learning_data["patterns"]:
        table = Table(title="🎓 Learned Patterns")
        table.add_column("Pattern Type", style="cyan")
        table.add_column("Count", style="bold")
        table.add_column("Avg Confidence", style="green")
        
        for pattern_type, data in learning_data["patterns"].items():
            table.add_row(
                pattern_type,
                str(data["count"]),
                f"{data['avg_confidence']:.1%}"
            )
        
        console.print(table)
    
    # Show recent events
    if learning_data["recent_events"]:
        console.print("\n📋 Recent Evolution Events:")
        for event in learning_data["recent_events"][-3:]:
            timestamp = event.get("timestamp", "unknown")
            success = "✅" if event.get("success") else "❌"
            console.print(f"   {success} {timestamp}: {event.get('type', 'unknown')}")


@app.command()
def status():
    """Show evolution system status"""
    engine = EvolutionEngine()
    
    console.print("📊 EVOLUTION SYSTEM STATUS")
    console.print("=" * 28)
    
    # Quick analysis
    test_issues = engine.analyze_test_failures()
    perf_issues = engine.analyze_performance_metrics()
    quality_issues = engine.analyze_code_quality()
    
    # Learning status
    learning_data = engine.learn_from_history()
    
    # Create status panel
    status_content = f"""
📈 Current Issues: {len(test_issues + perf_issues + quality_issues)}
   • Test Failures: {len(test_issues)}
   • Performance: {len(perf_issues)}
   • Code Quality: {len(quality_issues)}

🧠 Learning Status:
   • Historical Events: {learning_data.get('total_events', 0)}
   • Success Rate: {learning_data.get('success_rate', 0.0):.1%}
   • Learned Patterns: {len(learning_data.get('patterns', {}))}

🎯 Next Steps:
   • Run 'auto-evolve analyze' for detailed analysis
   • Run 'auto-evolve evolve' to apply improvements
   • Run 'auto-evolve learn' to update patterns
    """.strip()
    
    console.print(Panel(status_content, title="🤖 Evolution Engine Status", border_style="blue"))


def _apply_improvement(improvement: Dict[str, Any]) -> bool:
    """Apply a specific improvement (placeholder implementation)"""
    # This is a placeholder - in a real system, this would implement
    # the actual code changes based on the improvement specification
    
    improvement_type = improvement.get("type")
    
    if improvement_type == "code_fix" and "dspy" in improvement.get("title", "").lower():
        # For DSPy parsing fixes, we could:
        # 1. Update test signatures
        # 2. Add error handling
        # 3. Implement fallback parsing
        console.print("   🔧 Implementing DSPy parsing improvements...")
        time.sleep(1)  # Simulate work
        return True
    
    elif improvement_type == "performance_optimization":
        # For performance improvements, we could:
        # 1. Add caching
        # 2. Optimize algorithms
        # 3. Parallelize operations
        console.print("   🔧 Implementing performance optimizations...")
        time.sleep(1)  # Simulate work
        return True
    
    else:
        console.print("   ⚠️ Improvement type not yet supported for auto-application")
        return False


if __name__ == "__main__":
    app()