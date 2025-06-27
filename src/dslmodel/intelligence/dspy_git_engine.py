"""
DSPy-Powered Git Intelligence Engine
AI-driven decision making for Git operations in DevOps workflows
"""

import subprocess
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from opentelemetry import trace

import dspy
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()
tracer = trace.get_tracer(__name__)

@dataclass
class RepoState:
    """Current repository state for AI analysis"""
    branch: str
    ahead_commits: int
    behind_commits: int
    modified_files: int
    staged_files: int
    conflicts: int
    last_commit_age_hours: int
    contributors_active: int
    test_coverage: float
    build_status: str
    
@dataclass
class TeamStatus:
    """Team coordination status"""
    team_name: str
    sprint_progress: float
    blockers: int
    dependencies: List[str]
    velocity: float
    quality_score: float
    collaboration_score: float

@dataclass
class GitRecommendation:
    """AI recommendation for Git operation"""
    operation: str
    confidence: float
    reasoning: str
    risk_level: str
    expected_outcome: str
    fallback_strategy: str

class GitIntelligence(dspy.Module):
    """DSPy module for intelligent Git operation selection"""
    
    def __init__(self):
        super().__init__()
        self.analyze_repo = dspy.ChainOfThought(
            "repo_state, team_status -> optimal_git_operation, confidence, reasoning"
        )
        self.predict_conflicts = dspy.ChainOfThought(
            "branch_diff, team_activity -> conflict_probability, affected_files, resolution_strategy"
        )
        self.suggest_merge_strategy = dspy.ChainOfThought(
            "branch_complexity, team_coordination -> merge_strategy, sequence, timing"
        )
        self.assess_release_readiness = dspy.ChainOfThought(
            "quality_metrics, deployment_history -> readiness_score, blockers, recommendations"
        )
    
    def forward(self, repo_state: str, team_status: str, operation_context: str):
        """Generate intelligent Git operation recommendation"""
        
        # Analyze repository and recommend operation
        operation_result = self.analyze_repo(
            repo_state=repo_state,
            team_status=team_status
        )
        
        # Predict potential conflicts
        conflict_result = self.predict_conflicts(
            branch_diff=repo_state,
            team_activity=team_status
        )
        
        # Suggest integration strategy
        strategy_result = self.suggest_merge_strategy(
            branch_complexity=repo_state,
            team_coordination=team_status
        )
        
        return dspy.Prediction(
            operation=operation_result.optimal_git_operation,
            confidence=operation_result.confidence,
            reasoning=operation_result.reasoning,
            conflicts=conflict_result.conflict_probability,
            strategy=strategy_result.merge_strategy
        )

class CodeReviewAI(dspy.Module):
    """AI-powered code review and quality assessment"""
    
    def __init__(self):
        super().__init__()
        self.review_code = dspy.ChainOfThought(
            "code_diff, coding_standards -> review_feedback, issues, suggestions"
        )
        self.generate_tests = dspy.ChainOfThought(
            "code_changes, test_patterns -> test_cases, coverage_improvement, edge_cases"
        )
        self.assess_security = dspy.ChainOfThought(
            "code_diff, security_patterns -> vulnerabilities, risk_level, mitigations"
        )
    
    def forward(self, code_diff: str, context: str):
        """Perform AI-powered code review"""
        
        review = self.review_code(
            code_diff=code_diff,
            coding_standards=context
        )
        
        tests = self.generate_tests(
            code_changes=code_diff,
            test_patterns=context
        )
        
        security = self.assess_security(
            code_diff=code_diff,
            security_patterns=context
        )
        
        return dspy.Prediction(
            review=review.review_feedback,
            issues=review.issues,
            suggestions=review.suggestions,
            test_cases=tests.test_cases,
            security_risks=security.vulnerabilities
        )

class DeploymentAI(dspy.Module):
    """AI deployment decision engine"""
    
    def __init__(self):
        super().__init__()
        self.assess_readiness = dspy.ChainOfThought(
            "quality_metrics, system_health -> deployment_readiness, risk_factors, go_no_go"
        )
        self.recommend_strategy = dspy.ChainOfThought(
            "change_scope, system_capacity -> deployment_strategy, rollout_plan, monitoring_focus"
        )
        self.predict_impact = dspy.ChainOfThought(
            "change_analysis, user_patterns -> business_impact, user_experience_effect, rollback_criteria"
        )
    
    def forward(self, metrics: str, system_state: str, change_scope: str):
        """Make AI-powered deployment decisions"""
        
        readiness = self.assess_readiness(
            quality_metrics=metrics,
            system_health=system_state
        )
        
        strategy = self.recommend_strategy(
            change_scope=change_scope,
            system_capacity=system_state
        )
        
        impact = self.predict_impact(
            change_analysis=change_scope,
            user_patterns=system_state
        )
        
        return dspy.Prediction(
            ready=readiness.deployment_readiness,
            risk_factors=readiness.risk_factors,
            strategy=strategy.deployment_strategy,
            impact=impact.business_impact
        )

class DSPyGitEngine:
    """Main DSPy-powered Git intelligence engine"""
    
    def __init__(self):
        # Initialize DSPy with appropriate LM
        dspy.settings.configure(lm=dspy.OpenAI(model="gpt-4", max_tokens=2000))
        
        # Initialize AI modules
        self.git_intelligence = GitIntelligence()
        self.code_review_ai = CodeReviewAI()
        self.deployment_ai = DeploymentAI()
        
        console.print("🧠 DSPy Git Intelligence Engine initialized")
    
    def analyze_repository_state(self) -> RepoState:
        """Analyze current repository state for AI processing"""
        try:
            # Get current branch
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True, text=True, check=True
            )
            current_branch = branch_result.stdout.strip()
            
            # Get commit status
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True, check=True
            )
            modified_files = len([line for line in status_result.stdout.split('\n') 
                                if line.strip() and line[0] in 'MAD'])
            staged_files = len([line for line in status_result.stdout.split('\n') 
                              if line.strip() and line[1] in 'MAD'])
            
            # Check for conflicts
            conflict_result = subprocess.run(
                ["git", "diff", "--name-only", "--diff-filter=U"],
                capture_output=True, text=True
            )
            conflicts = len(conflict_result.stdout.split('\n')) if conflict_result.stdout.strip() else 0
            
            # Get commit age
            commit_age_result = subprocess.run([
                "git", "log", "-1", "--format=%ct"
            ], capture_output=True, text=True)
            
            if commit_age_result.returncode == 0:
                import time
                commit_timestamp = int(commit_age_result.stdout.strip())
                last_commit_age_hours = int((time.time() - commit_timestamp) / 3600)
            else:
                last_commit_age_hours = 0
            
            # Get contributor count (last 30 days)
            contributors_result = subprocess.run([
                "git", "shortlog", "-sn", "--since='30 days ago'"
            ], capture_output=True, text=True)
            contributors_active = len(contributors_result.stdout.split('\n')) if contributors_result.stdout.strip() else 1
            
            return RepoState(
                branch=current_branch,
                ahead_commits=0,  # Simplified for demo
                behind_commits=0,
                modified_files=modified_files,
                staged_files=staged_files,
                conflicts=conflicts,
                last_commit_age_hours=last_commit_age_hours,
                contributors_active=contributors_active,
                test_coverage=85.0,  # Mock data
                build_status="passing"
            )
            
        except subprocess.CalledProcessError as e:
            console.print(f"⚠️ Error analyzing repository: {e}")
            # Return default state
            return RepoState(
                branch="main", ahead_commits=0, behind_commits=0,
                modified_files=0, staged_files=0, conflicts=0,
                last_commit_age_hours=1, contributors_active=1,
                test_coverage=80.0, build_status="unknown"
            )
    
    def get_team_status(self, team_name: str = "default") -> TeamStatus:
        """Get current team status (mock implementation)"""
        # In production, this would integrate with Jira, Azure DevOps, etc.
        return TeamStatus(
            team_name=team_name,
            sprint_progress=0.65,
            blockers=2,
            dependencies=["auth-service", "payment-api"],
            velocity=23.5,
            quality_score=0.87,
            collaboration_score=0.92
        )
    
    def recommend_git_operation(self, context: str = "development") -> GitRecommendation:
        """Get AI recommendation for next Git operation"""
        with tracer.start_as_current_span("dspy.git.recommendation") as span:
            
            # Analyze current state
            repo_state = self.analyze_repository_state()
            team_status = self.get_team_status()
            
            # Format for DSPy
            repo_description = f"""
            Repository State:
            - Branch: {repo_state.branch}
            - Modified files: {repo_state.modified_files}
            - Staged files: {repo_state.staged_files}
            - Conflicts: {repo_state.conflicts}
            - Test coverage: {repo_state.test_coverage}%
            - Build status: {repo_state.build_status}
            - Contributors active: {repo_state.contributors_active}
            """
            
            team_description = f"""
            Team Status:
            - Sprint progress: {team_status.sprint_progress * 100:.1f}%
            - Active blockers: {team_status.blockers}
            - Dependencies: {', '.join(team_status.dependencies)}
            - Velocity: {team_status.velocity}
            - Quality score: {team_status.quality_score}
            """
            
            # Get AI recommendation
            prediction = self.git_intelligence(
                repo_state=repo_description,
                team_status=team_description,
                operation_context=context
            )
            
            # Parse confidence score
            try:
                confidence = float(prediction.confidence)
            except:
                confidence = 0.75  # Default confidence
            
            # Determine risk level based on repository state
            risk_level = "low"
            if repo_state.conflicts > 0:
                risk_level = "high"
            elif repo_state.modified_files > 10:
                risk_level = "medium"
            
            recommendation = GitRecommendation(
                operation=prediction.operation,
                confidence=confidence,
                reasoning=prediction.reasoning,
                risk_level=risk_level,
                expected_outcome=f"Improved {context} workflow efficiency",
                fallback_strategy="Manual review and approval process"
            )
            
            # Add telemetry
            span.set_attribute("dspy.recommendation.operation", recommendation.operation)
            span.set_attribute("dspy.recommendation.confidence", recommendation.confidence)
            span.set_attribute("dspy.recommendation.risk_level", recommendation.risk_level)
            
            return recommendation
    
    def review_code_changes(self) -> Dict[str, Any]:
        """AI-powered code review of current changes"""
        with tracer.start_as_current_span("dspy.code.review") as span:
            
            # Get current diff
            try:
                diff_result = subprocess.run([
                    "git", "diff", "--cached"
                ], capture_output=True, text=True, check=True)
                
                if not diff_result.stdout.strip():
                    # No staged changes, check working directory
                    diff_result = subprocess.run([
                        "git", "diff"
                    ], capture_output=True, text=True, check=True)
                
                code_diff = diff_result.stdout
                
            except subprocess.CalledProcessError:
                code_diff = "No changes detected"
            
            if not code_diff.strip() or code_diff == "No changes detected":
                return {
                    "review": "No code changes to review",
                    "issues": [],
                    "suggestions": [],
                    "test_cases": [],
                    "security_risks": []
                }
            
            # Perform AI review
            context = "Python project with DSPy, Git automation, and OTEL integration"
            
            prediction = self.code_review_ai(
                code_diff=code_diff[:2000],  # Limit size for LLM
                context=context
            )
            
            review_result = {
                "review": prediction.review,
                "issues": prediction.issues if hasattr(prediction, 'issues') else [],
                "suggestions": prediction.suggestions if hasattr(prediction, 'suggestions') else [],
                "test_cases": prediction.test_cases if hasattr(prediction, 'test_cases') else [],
                "security_risks": prediction.security_risks if hasattr(prediction, 'security_risks') else []
            }
            
            # Add telemetry
            span.set_attribute("dspy.review.changes_size", len(code_diff))
            span.set_attribute("dspy.review.has_issues", len(review_result["issues"]) > 0)
            
            return review_result
    
    def assess_deployment_readiness(self) -> Dict[str, Any]:
        """AI assessment of deployment readiness"""
        with tracer.start_as_current_span("dspy.deployment.assessment") as span:
            
            repo_state = self.analyze_repository_state()
            
            # Mock quality metrics (in production, integrate with actual metrics)
            metrics = f"""
            Quality Metrics:
            - Test coverage: {repo_state.test_coverage}%
            - Build status: {repo_state.build_status}
            - Code quality score: 8.5/10
            - Security scan: PASSED
            - Performance tests: PASSED
            """
            
            system_state = f"""
            System Health:
            - CPU utilization: 45%
            - Memory usage: 62%
            - Error rate: 0.02%
            - Response time: 125ms avg
            - Uptime: 99.98%
            """
            
            change_scope = f"""
            Change Analysis:
            - Modified files: {repo_state.modified_files}
            - Risk level: {repo_state.conflicts > 0 and 'HIGH' or 'LOW'}
            - Breaking changes: None detected
            - Database migrations: None
            """
            
            # Get AI assessment
            prediction = self.deployment_ai(
                metrics=metrics,
                system_state=system_state,
                change_scope=change_scope
            )
            
            assessment = {
                "ready": prediction.ready,
                "risk_factors": prediction.risk_factors if hasattr(prediction, 'risk_factors') else [],
                "strategy": prediction.strategy,
                "impact": prediction.impact,
                "confidence": 0.85  # Mock confidence score
            }
            
            # Add telemetry
            span.set_attribute("dspy.deployment.ready", assessment["ready"])
            span.set_attribute("dspy.deployment.confidence", assessment["confidence"])
            
            return assessment
    
    def display_recommendation(self, recommendation: GitRecommendation):
        """Display AI recommendation in rich format"""
        
        # Color code by confidence
        confidence_color = "green" if recommendation.confidence > 0.8 else "yellow" if recommendation.confidence > 0.6 else "red"
        
        # Risk level emoji
        risk_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}
        
        panel_content = f"""
🧠 **AI Git Recommendation**

**Operation**: `{recommendation.operation}`
**Confidence**: {recommendation.confidence:.1%} 
**Risk Level**: {risk_emoji.get(recommendation.risk_level, '⚪')} {recommendation.risk_level.upper()}

**Reasoning**: {recommendation.reasoning}

**Expected Outcome**: {recommendation.expected_outcome}
**Fallback Strategy**: {recommendation.fallback_strategy}
        """
        
        console.print(Panel.fit(
            panel_content,
            title="DSPy Git Intelligence",
            style=confidence_color
        ))
    
    def display_code_review(self, review: Dict[str, Any]):
        """Display code review results"""
        
        table = Table(title="AI Code Review Results")
        table.add_column("Category", style="cyan")
        table.add_column("Findings", style="white")
        
        table.add_row("Overall Review", str(review.get("review", "No review available")))
        table.add_row("Issues Found", str(len(review.get("issues", []))))
        table.add_row("Suggestions", str(len(review.get("suggestions", []))))
        table.add_row("Test Cases", str(len(review.get("test_cases", []))))
        table.add_row("Security Risks", str(len(review.get("security_risks", []))))
        
        console.print(table)
        
        # Show details if available
        if review.get("issues"):
            console.print("\n🔍 **Issues Found**:")
            for i, issue in enumerate(review["issues"][:3], 1):  # Show first 3
                console.print(f"  {i}. {issue}")
        
        if review.get("suggestions"):
            console.print("\n💡 **Suggestions**:")
            for i, suggestion in enumerate(review["suggestions"][:3], 1):
                console.print(f"  {i}. {suggestion}")

    def run_intelligent_git_workflow(self, context: str = "development") -> bool:
        """Run complete AI-powered Git workflow"""
        console.print("🚀 Starting Intelligent Git Workflow")
        
        try:
            # Step 1: Get AI recommendation
            console.print("\n1️⃣ Getting AI recommendation...")
            recommendation = self.recommend_git_operation(context)
            self.display_recommendation(recommendation)
            
            # Step 2: Code review if there are changes
            console.print("\n2️⃣ Performing AI code review...")
            review = self.review_code_changes()
            self.display_code_review(review)
            
            # Step 3: Deployment readiness if in release context
            if context in ["release", "production", "deployment"]:
                console.print("\n3️⃣ Assessing deployment readiness...")
                assessment = self.assess_deployment_readiness()
                
                readiness_panel = f"""
🚀 **Deployment Assessment**

**Ready for Deployment**: {assessment['ready']}
**Confidence**: {assessment['confidence']:.1%}
**Strategy**: {assessment['strategy']}
**Business Impact**: {assessment['impact']}
                """
                
                console.print(Panel.fit(readiness_panel, title="Deployment AI", style="blue"))
            
            console.print("\n✅ Intelligent Git workflow completed successfully")
            return True
            
        except Exception as e:
            console.print(f"\n❌ Intelligent workflow failed: {e}")
            return False


# CLI interface for testing
if __name__ == "__main__":
    import typer
    
    app = typer.Typer(name="dspy-git", help="DSPy-powered Git intelligence")
    
    @app.command()
    def recommend(context: str = "development"):
        """Get AI recommendation for Git operation"""
        engine = DSPyGitEngine()
        recommendation = engine.recommend_git_operation(context)
        engine.display_recommendation(recommendation)
    
    @app.command()
    def review():
        """AI-powered code review of current changes"""
        engine = DSPyGitEngine()
        review = engine.review_code_changes()
        engine.display_code_review(review)
    
    @app.command()
    def deploy_check():
        """Assess deployment readiness with AI"""
        engine = DSPyGitEngine()
        assessment = engine.assess_deployment_readiness()
        console.print(assessment)
    
    @app.command()
    def workflow(context: str = "development"):
        """Run complete intelligent Git workflow"""
        engine = DSPyGitEngine()
        engine.run_intelligent_git_workflow(context)
    
    app()