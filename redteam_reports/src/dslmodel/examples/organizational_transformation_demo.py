#!/usr/bin/env python3
"""
Organizational Transformation Demo - 80/20 Implementation
=========================================================

Demonstrates integration of:
1. Roberts Rules of Order (Governance)
2. Scrum at Scale (Agile Development) 
3. Design for Lean Six Sigma (Process Improvement)

Through DSLModel framework with telemetry-driven coordination.

80/20 Focus: 20% effort demonstrating 80% of organizational transformation value
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

from pydantic import BaseModel, Field
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

# DSLModel imports
from dslmodel.mixins import FSMMixin, trigger
from dslmodel.template.functional import render

# Configure OTEL for demo
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(ConsoleSpanExporter())
)

# =====================================================
# 1. ROBERTS RULES GOVERNANCE AGENT (Parliamentary Procedure)
# =====================================================

class Motion(BaseModel):
    """Parliamentary motion following Roberts Rules"""
    id: str = Field(..., description="Motion identifier")
    title: str = Field(..., description="Motion title")
    description: str = Field(..., description="Detailed motion description")
    moved_by: str = Field(..., description="Member who moved the motion")
    seconded_by: Optional[str] = Field(None, description="Member who seconded")
    status: str = Field(default="pending", description="pending|seconded|voted|passed|failed")
    votes_for: int = Field(default=0, description="Votes in favor")
    votes_against: int = Field(default=0, description="Votes against")
    abstentions: int = Field(default=0, description="Abstentions")
    impact_scope: str = Field(..., description="development|process|governance")

class RobertsRulesAgent(FSMMixin):
    """
    Agent implementing Roberts Rules of Order for organizational governance
    
    States: idle → motion_pending → motion_seconded → voting → decision_made
    """
    
    states = ['idle', 'motion_pending', 'motion_seconded', 'voting', 'decision_made']
    
    def __init__(self):
        super().__init__()
        self.current_motion: Optional[Motion] = None
        self.meeting_minutes: List[Dict] = []
        # Initialize FSM
        self.setup_fsm(self.states, initial='idle')
        
    @trigger(source='idle', dest='motion_pending')
    def receive_motion(self, motion_data: Dict) -> Motion:
        """Receive and validate a parliamentary motion"""
        with tracer.start_as_current_span("roberts.motion.received") as span:
            motion = Motion(**motion_data)
            self.current_motion = motion
            
            span.set_attribute("roberts.motion.id", motion.id)
            span.set_attribute("roberts.motion.title", motion.title)
            span.set_attribute("roberts.motion.moved_by", motion.moved_by)
            span.set_attribute("roberts.motion.impact_scope", motion.impact_scope)
            
            self.meeting_minutes.append({
                "timestamp": datetime.now().isoformat(),
                "action": "motion_received",
                "motion_id": motion.id,
                "title": motion.title,
                "moved_by": motion.moved_by
            })
            
            return motion
    
    @trigger(source='motion_pending', dest='motion_seconded')
    def second_motion(self, seconded_by: str) -> bool:
        """Second the current motion"""
        with tracer.start_as_current_span("roberts.motion.seconded") as span:
            if self.current_motion:
                self.current_motion.seconded_by = seconded_by
                self.current_motion.status = "seconded"
                
                span.set_attribute("roberts.motion.id", self.current_motion.id)
                span.set_attribute("roberts.motion.seconded_by", seconded_by)
                
                self.meeting_minutes.append({
                    "timestamp": datetime.now().isoformat(),
                    "action": "motion_seconded",
                    "motion_id": self.current_motion.id,
                    "seconded_by": seconded_by
                })
                
                return True
            return False
    
    @trigger(source='motion_seconded', dest='voting')
    def open_voting(self) -> bool:
        """Open voting on the seconded motion"""
        with tracer.start_as_current_span("roberts.voting.opened") as span:
            if self.current_motion:
                span.set_attribute("roberts.motion.id", self.current_motion.id)
                span.set_attribute("roberts.voting.status", "open")
                
                self.meeting_minutes.append({
                    "timestamp": datetime.now().isoformat(),
                    "action": "voting_opened",
                    "motion_id": self.current_motion.id
                })
                
                return True
            return False
    
    @trigger(source='voting', dest='decision_made')
    def close_voting(self, votes_for: int, votes_against: int, abstentions: int = 0) -> Dict:
        """Close voting and determine motion outcome"""
        with tracer.start_as_current_span("roberts.voting.closed") as span:
            if self.current_motion:
                self.current_motion.votes_for = votes_for
                self.current_motion.votes_against = votes_against
                self.current_motion.abstentions = abstentions
                
                # Determine outcome (simple majority)
                passed = votes_for > votes_against
                self.current_motion.status = "passed" if passed else "failed"
                
                span.set_attribute("roberts.motion.id", self.current_motion.id)
                span.set_attribute("roberts.voting.votes_for", votes_for)
                span.set_attribute("roberts.voting.votes_against", votes_against)
                span.set_attribute("roberts.voting.abstentions", abstentions)
                span.set_attribute("roberts.motion.outcome", self.current_motion.status)
                
                decision = {
                    "motion_id": self.current_motion.id,
                    "outcome": self.current_motion.status,
                    "votes": {
                        "for": votes_for,
                        "against": votes_against,
                        "abstentions": abstentions
                    },
                    "trigger_next": self.current_motion.impact_scope if passed else None
                }
                
                self.meeting_minutes.append({
                    "timestamp": datetime.now().isoformat(),
                    "action": "voting_closed",
                    "motion_id": self.current_motion.id,
                    "outcome": self.current_motion.status,
                    "votes": decision["votes"]
                })
                
                return decision
            return {}

# =====================================================
# 2. SCRUM AT SCALE AGENT (Agile Development)
# =====================================================

class Epic(BaseModel):
    """Scrum at Scale Epic for large organizational initiatives"""
    id: str = Field(..., description="Epic identifier")
    title: str = Field(..., description="Epic title")
    description: str = Field(..., description="Epic description")
    business_value: int = Field(..., description="Business value (1-100)")
    effort_estimate: int = Field(..., description="Story points estimate")
    teams_involved: List[str] = Field(..., description="Scrum teams involved")
    pi_objective: str = Field(..., description="Program Increment objective")
    status: str = Field(default="backlog", description="backlog|planned|active|done")

class ScrumAtScaleAgent(FSMMixin):
    """
    Agent implementing Scrum at Scale for large agile organizations
    
    States: idle → pi_planning → sprint_planning → execution → retrospective → improvement
    """
    
    states = ['idle', 'pi_planning', 'sprint_planning', 'execution', 'retrospective', 'improvement']
    
    def __init__(self):
        super().__init__()
        self.program_increment: Optional[Dict] = None
        self.epics: List[Epic] = []
        self.team_capacity: Dict[str, int] = {}
        self.velocity_data: Dict[str, List[int]] = {}
        # Initialize FSM
        self.setup_fsm(self.states, initial='idle')
        
    @trigger(source='idle', dest='pi_planning')
    def initiate_pi_planning(self, governance_decision: Dict) -> Dict:
        """Initiate Program Increment planning based on governance decision"""
        with tracer.start_as_current_span("scrum.pi_planning.initiated") as span:
            pi_number = f"PI-{datetime.now().strftime('%Y%m')}"
            
            self.program_increment = {
                "pi_number": pi_number,
                "start_date": datetime.now().isoformat(),
                "end_date": (datetime.now() + timedelta(days=84)).isoformat(),  # 12 weeks
                "governance_trigger": governance_decision,
                "objectives": [],
                "teams": ["Alpha", "Beta", "Gamma", "Delta"],  # Example teams
                "capacity_per_team": 80  # Story points per sprint per team
            }
            
            span.set_attribute("scrum.pi.number", pi_number)
            span.set_attribute("scrum.pi.governance_motion", governance_decision.get("motion_id", ""))
            span.set_attribute("scrum.pi.teams_count", len(self.program_increment["teams"]))
            
            return self.program_increment
    
    @trigger(source='pi_planning', dest='sprint_planning')
    def create_epics_from_governance(self, governance_decision: Dict) -> List[Epic]:
        """Create epics based on governance decision"""
        with tracer.start_as_current_span("scrum.epics.created") as span:
            # Generate epics based on governance decision scope
            scope = governance_decision.get("trigger_next", "development")
            
            if scope == "development":
                epic_data = [
                    {
                        "id": f"EPIC-{datetime.now().strftime('%Y%m')}-001",
                        "title": "Platform Architecture Enhancement",
                        "description": "Implement scalable architecture based on governance decision",
                        "business_value": 85,
                        "effort_estimate": 120,
                        "teams_involved": ["Alpha", "Beta"],
                        "pi_objective": "Deliver scalable platform foundation"
                    },
                    {
                        "id": f"EPIC-{datetime.now().strftime('%Y%m')}-002", 
                        "title": "User Experience Optimization",
                        "description": "Enhance user interface based on feedback",
                        "business_value": 70,
                        "effort_estimate": 80,
                        "teams_involved": ["Gamma"],
                        "pi_objective": "Improve user satisfaction metrics"
                    }
                ]
            elif scope == "process":
                epic_data = [
                    {
                        "id": f"EPIC-{datetime.now().strftime('%Y%m')}-003",
                        "title": "Process Automation Initiative", 
                        "description": "Automate manual processes identified in governance",
                        "business_value": 90,
                        "effort_estimate": 100,
                        "teams_involved": ["Delta", "Alpha"],
                        "pi_objective": "Reduce manual overhead by 60%"
                    }
                ]
            else:
                epic_data = []
            
            epics = [Epic(**data) for data in epic_data]
            self.epics.extend(epics)
            
            span.set_attribute("scrum.epics.count", len(epics))
            span.set_attribute("scrum.epics.total_effort", sum(e.effort_estimate for e in epics))
            span.set_attribute("scrum.epics.total_value", sum(e.business_value for e in epics))
            
            return epics
    
    @trigger(source='sprint_planning', dest='execution')
    def plan_sprints(self) -> Dict:
        """Plan sprints for the Program Increment"""
        with tracer.start_as_current_span("scrum.sprints.planned") as span:
            total_capacity = len(self.program_increment["teams"]) * 6 * 80  # 6 sprints, 80 points each
            total_effort = sum(epic.effort_estimate for epic in self.epics)
            
            sprint_plan = {
                "pi_number": self.program_increment["pi_number"],
                "total_capacity": total_capacity,
                "total_planned_effort": total_effort,
                "utilization_percentage": min(100, (total_effort / total_capacity) * 100),
                "sprints": []
            }
            
            # Distribute epics across sprints
            for sprint in range(1, 7):  # 6 sprints per PI
                sprint_plan["sprints"].append({
                    "sprint_number": sprint,
                    "start_date": (datetime.now() + timedelta(weeks=2*(sprint-1))).isoformat(),
                    "capacity_per_team": 80,
                    "planned_epics": [epic.id for epic in self.epics[:2]]  # Simplified distribution
                })
            
            span.set_attribute("scrum.sprint_plan.total_capacity", total_capacity)
            span.set_attribute("scrum.sprint_plan.planned_effort", total_effort)
            span.set_attribute("scrum.sprint_plan.utilization", int(sprint_plan["utilization_percentage"]))
            
            return sprint_plan
    
    @trigger(source='execution', dest='retrospective')
    def execute_sprint(self, sprint_data: Dict) -> Dict:
        """Execute sprint and gather metrics"""
        with tracer.start_as_current_span("scrum.sprint.executed") as span:
            # Simulate sprint execution metrics
            teams = self.program_increment["teams"]
            sprint_results = {
                "sprint_number": sprint_data.get("sprint_number", 1),
                "planned_points": sprint_data.get("capacity_per_team", 80) * len(teams),
                "completed_points": 0,
                "team_velocities": {},
                "defects_found": 0,
                "blockers_encountered": 0
            }
            
            # Generate realistic velocity data
            for team in teams:
                base_velocity = 75  # Base capacity
                velocity_variance = 15  # ±15 point variance
                actual_velocity = max(0, base_velocity + (hash(team + str(time.time())) % (velocity_variance * 2)) - velocity_variance)
                sprint_results["team_velocities"][team] = actual_velocity
                sprint_results["completed_points"] += actual_velocity
                
                # Track defects (trigger for Lean Six Sigma)
                defects = max(0, (hash(team + "defects") % 5))  # 0-4 defects per team
                sprint_results["defects_found"] += defects
            
            # Calculate key metrics
            sprint_results["velocity_percentage"] = (sprint_results["completed_points"] / sprint_results["planned_points"]) * 100
            sprint_results["defect_rate"] = sprint_results["defects_found"] / sprint_results["completed_points"] if sprint_results["completed_points"] > 0 else 0
            
            span.set_attribute("scrum.sprint.number", sprint_results["sprint_number"])
            span.set_attribute("scrum.sprint.velocity_percentage", int(sprint_results["velocity_percentage"]))
            span.set_attribute("scrum.sprint.defects_found", sprint_results["defects_found"])
            span.set_attribute("scrum.sprint.defect_rate", sprint_results["defect_rate"])
            
            return sprint_results
    
    @trigger(source='retrospective', dest='improvement')
    def conduct_retrospective(self, sprint_results: Dict) -> Dict:
        """Conduct sprint retrospective and identify improvements"""
        with tracer.start_as_current_span("scrum.retrospective.conducted") as span:
            retrospective = {
                "sprint_number": sprint_results["sprint_number"],
                "velocity_trend": "stable",  # Simplified
                "key_insights": [],
                "improvement_actions": [],
                "trigger_lean_six_sigma": False
            }
            
            # Analyze sprint results
            velocity_pct = sprint_results["velocity_percentage"]
            defect_rate = sprint_results["defect_rate"]
            
            if velocity_pct < 75:
                retrospective["key_insights"].append("Velocity below target - investigate blockers")
                retrospective["improvement_actions"].append("Process impediment analysis")
                
            if defect_rate > 0.05:  # 5% defect rate threshold
                retrospective["key_insights"].append(f"Defect rate {defect_rate:.2%} exceeds threshold")
                retrospective["improvement_actions"].append("Quality process improvement needed")
                retrospective["trigger_lean_six_sigma"] = True
                
            if sprint_results["blockers_encountered"] > 3:
                retrospective["key_insights"].append("High blocker count indicates process issues")
                retrospective["improvement_actions"].append("Workflow optimization required")
                retrospective["trigger_lean_six_sigma"] = True
            
            span.set_attribute("scrum.retrospective.velocity_percentage", int(velocity_pct))
            span.set_attribute("scrum.retrospective.defect_rate", defect_rate)
            span.set_attribute("scrum.retrospective.trigger_lean", retrospective["trigger_lean_six_sigma"])
            span.set_attribute("scrum.retrospective.improvement_actions_count", len(retrospective["improvement_actions"]))
            
            return retrospective

# =====================================================
# 3. LEAN SIX SIGMA AGENT (Process Improvement)
# =====================================================

class DefectAnalysis(BaseModel):
    """Lean Six Sigma defect analysis"""
    defect_type: str = Field(..., description="Type of defect identified")
    frequency: int = Field(..., description="Number of occurrences")
    impact_severity: str = Field(..., description="low|medium|high|critical")
    root_cause: str = Field(..., description="Identified root cause")
    process_area: str = Field(..., description="Process area affected")

class LeanSixSigmaAgent(FSMMixin):
    """
    Agent implementing Design for Lean Six Sigma methodology
    
    States: idle → define → measure → analyze → improve → control
    """
    
    states = ['idle', 'define', 'measure', 'analyze', 'improve', 'control']
    
    def __init__(self):
        super().__init__()
        self.current_project: Optional[Dict] = None
        self.metrics_baseline: Dict = {}
        self.improvement_recommendations: List[Dict] = []
        # Initialize FSM
        self.setup_fsm(self.states, initial='idle')
        
    @trigger(source='idle', dest='define')
    def initiate_improvement_project(self, scrum_retrospective: Dict) -> Dict:
        """Initiate Lean Six Sigma improvement project based on Scrum retrospective"""
        with tracer.start_as_current_span("lean.project.defined") as span:
            project_id = f"LSS-{datetime.now().strftime('%Y%m%d%H%M')}"
            
            self.current_project = {
                "project_id": project_id,
                "charter": {
                    "problem_statement": f"Address quality and velocity issues from Sprint {scrum_retrospective['sprint_number']}",
                    "goal": "Reduce defect rate and improve velocity consistency",
                    "scope": "Development and testing processes",
                    "success_criteria": [
                        "Reduce defect rate to <3%",
                        "Achieve velocity variance <10%",
                        "Eliminate process blockers"
                    ]
                },
                "scrum_trigger": scrum_retrospective,
                "start_date": datetime.now().isoformat(),
                "phase": "define"
            }
            
            span.set_attribute("lean.project.id", project_id)
            span.set_attribute("lean.project.trigger_sprint", scrum_retrospective["sprint_number"])
            span.set_attribute("lean.project.defect_rate", scrum_retrospective.get("defect_rate", 0))
            
            return self.current_project
    
    @trigger(source='define', dest='measure')
    def establish_baseline_metrics(self) -> Dict:
        """Establish baseline measurements for current state"""
        with tracer.start_as_current_span("lean.baseline.measured") as span:
            # Simulate baseline metrics collection
            self.metrics_baseline = {
                "defect_rate": 0.08,  # 8% current defect rate
                "cycle_time_avg": 5.2,  # days
                "lead_time_avg": 12.5,  # days
                "rework_percentage": 15.3,  # percentage of work requiring rework
                "process_efficiency": 72.1,  # percentage
                "customer_satisfaction": 7.2,  # out of 10
                "team_velocity_variance": 18.5  # percentage variance
            }
            
            span.set_attribute("lean.baseline.defect_rate", self.metrics_baseline["defect_rate"])
            span.set_attribute("lean.baseline.cycle_time", self.metrics_baseline["cycle_time_avg"])
            span.set_attribute("lean.baseline.efficiency", self.metrics_baseline["process_efficiency"])
            
            return self.metrics_baseline
    
    @trigger(source='measure', dest='analyze')
    def analyze_root_causes(self) -> List[DefectAnalysis]:
        """Analyze root causes using Lean Six Sigma tools"""
        with tracer.start_as_current_span("lean.analysis.completed") as span:
            # Perform root cause analysis (simplified)
            defect_analyses = [
                DefectAnalysis(
                    defect_type="Integration Failures",
                    frequency=12,
                    impact_severity="high",
                    root_cause="Insufficient automated testing in CI/CD pipeline",
                    process_area="Development"
                ),
                DefectAnalysis(
                    defect_type="Requirements Misalignment",
                    frequency=8,
                    impact_severity="medium", 
                    root_cause="Unclear acceptance criteria and stakeholder communication gaps",
                    process_area="Planning"
                ),
                DefectAnalysis(
                    defect_type="Code Quality Issues",
                    frequency=15,
                    impact_severity="medium",
                    root_cause="Inconsistent code review standards and time pressure",
                    process_area="Development"
                ),
                DefectAnalysis(
                    defect_type="Environment Configuration",
                    frequency=5,
                    impact_severity="high",
                    root_cause="Manual deployment processes prone to human error",
                    process_area="Operations"
                )
            ]
            
            total_defects = sum(analysis.frequency for analysis in defect_analyses)
            high_impact_defects = sum(1 for analysis in defect_analyses if analysis.impact_severity in ["high", "critical"])
            
            span.set_attribute("lean.analysis.total_defects", total_defects)
            span.set_attribute("lean.analysis.high_impact_count", high_impact_defects)
            span.set_attribute("lean.analysis.process_areas", len(set(a.process_area for a in defect_analyses)))
            
            return defect_analyses
    
    @trigger(source='analyze', dest='improve')
    def design_improvements(self, defect_analyses: List[DefectAnalysis]) -> List[Dict]:
        """Design improvement solutions using Lean principles"""
        with tracer.start_as_current_span("lean.improvements.designed") as span:
            improvements = []
            
            # Group defects by process area and design improvements
            process_areas = set(analysis.process_area for analysis in defect_analyses)
            
            for area in process_areas:
                area_defects = [d for d in defect_analyses if d.process_area == area]
                total_frequency = sum(d.frequency for d in area_defects)
                
                if area == "Development":
                    improvements.append({
                        "area": area,
                        "improvement_type": "Automation",
                        "description": "Implement comprehensive automated testing and code quality gates",
                        "expected_impact": "70% reduction in integration and code quality defects",
                        "implementation_effort": "6 weeks",
                        "defects_addressed": total_frequency,
                        "lean_principle": "Eliminate waste (rework)"
                    })
                elif area == "Planning":
                    improvements.append({
                        "area": area,
                        "improvement_type": "Process Standardization",
                        "description": "Standardize acceptance criteria templates and stakeholder review process",
                        "expected_impact": "50% reduction in requirements-related defects",
                        "implementation_effort": "3 weeks",
                        "defects_addressed": total_frequency,
                        "lean_principle": "Standardize work"
                    })
                elif area == "Operations":
                    improvements.append({
                        "area": area,
                        "improvement_type": "Error Proofing",
                        "description": "Implement infrastructure as code and automated deployment validation",
                        "expected_impact": "85% reduction in configuration defects",
                        "implementation_effort": "8 weeks",
                        "defects_addressed": total_frequency,
                        "lean_principle": "Error proofing (poka-yoke)"
                    })
            
            self.improvement_recommendations = improvements
            
            span.set_attribute("lean.improvements.count", len(improvements))
            span.set_attribute("lean.improvements.total_defects_addressed", sum(i["defects_addressed"] for i in improvements))
            span.set_attribute("lean.improvements.total_effort_weeks", sum(int(i["implementation_effort"].split()[0]) for i in improvements))
            
            return improvements
    
    @trigger(source='improve', dest='control')
    def implement_control_plan(self) -> Dict:
        """Implement control plan to sustain improvements"""
        with tracer.start_as_current_span("lean.control.implemented") as span:
            control_plan = {
                "project_id": self.current_project["project_id"],
                "control_metrics": [
                    {
                        "metric": "Defect Rate",
                        "target": "< 3%",
                        "measurement_frequency": "Daily",
                        "responsible_party": "Quality Team",
                        "escalation_threshold": "5%"
                    },
                    {
                        "metric": "Cycle Time",
                        "target": "< 4 days",
                        "measurement_frequency": "Weekly",
                        "responsible_party": "Scrum Masters",
                        "escalation_threshold": "> 6 days"
                    },
                    {
                        "metric": "Velocity Variance",
                        "target": "< 10%",
                        "measurement_frequency": "Per Sprint",
                        "responsible_party": "Agile Coaches",
                        "escalation_threshold": "> 15%"
                    }
                ],
                "governance_integration": {
                    "quarterly_review": "Present results to governance board",
                    "escalation_process": "Automatic motion for process changes if thresholds exceeded",
                    "continuous_improvement": "Monthly retrospectives with Scrum teams"
                },
                "expected_benefits": {
                    "defect_reduction": "65%",
                    "cycle_time_improvement": "23%",
                    "velocity_stabilization": "85%",
                    "customer_satisfaction_increase": "15%"
                }
            }
            
            span.set_attribute("lean.control.metrics_count", len(control_plan["control_metrics"]))
            span.set_attribute("lean.control.expected_defect_reduction", 65)
            span.set_attribute("lean.control.expected_cycle_improvement", 23)
            
            return control_plan

# =====================================================
# 4. ORCHESTRATION ENGINE (Integration Demo)
# =====================================================

class OrganizationalTransformationOrchestrator:
    """
    Orchestrates the integration of Roberts Rules → Scrum at Scale → Lean Six Sigma
    
    Demonstrates end-to-end organizational transformation with telemetry validation
    """
    
    def __init__(self):
        self.roberts_agent = RobertsRulesAgent()
        self.scrum_agent = ScrumAtScaleAgent()
        self.lean_agent = LeanSixSigmaAgent()
        self.execution_log: List[Dict] = []
        
    async def run_full_transformation_demo(self) -> Dict:
        """Execute complete organizational transformation demo"""
        with tracer.start_as_current_span("transformation.demo.full") as span:
            print("🏛️  ORGANIZATIONAL TRANSFORMATION DEMO")
            print("=====================================")
            print("Integrating Roberts Rules → Scrum at Scale → Lean Six Sigma")
            print()
            
            results = {
                "demo_start": datetime.now().isoformat(),
                "phases": {},
                "integration_points": [],
                "final_outcomes": {}
            }
            
            # === PHASE 1: GOVERNANCE DECISION (Roberts Rules) ===
            print("📋 PHASE 1: GOVERNANCE DECISION (Roberts Rules)")
            print("-" * 50)
            
            # 1.1 Propose motion for platform improvement
            motion_data = {
                "id": "MOTION-2024-001",
                "title": "Platform Scalability Initiative",
                "description": "Approve investment in platform architecture improvements to support 300% user growth",
                "moved_by": "CTO Sarah Chen",
                "impact_scope": "development"
            }
            
            motion = self.roberts_agent.receive_motion(motion_data)
            print(f"   🗣️  Motion received: {motion.title}")
            print(f"   📝 Moved by: {motion.moved_by}")
            
            # 1.2 Second the motion
            self.roberts_agent.second_motion("VP Engineering Mike Rodriguez")
            print(f"   ✋ Motion seconded by: VP Engineering Mike Rodriguez")
            
            # 1.3 Open and close voting
            self.roberts_agent.open_voting()
            print(f"   🗳️  Voting opened...")
            
            # Simulate board voting
            decision = self.roberts_agent.close_voting(votes_for=7, votes_against=1, abstentions=1)
            print(f"   ✅ Motion PASSED: {decision['votes']['for']} for, {decision['votes']['against']} against")
            
            results["phases"]["governance"] = {
                "motion": motion_data,
                "outcome": decision,
                "trigger_next": decision.get("trigger_next")
            }
            
            # === PHASE 2: AGILE PLANNING (Scrum at Scale) ===
            print("\n🏃 PHASE 2: AGILE PLANNING (Scrum at Scale)")
            print("-" * 50)
            
            # 2.1 Initiate PI Planning based on governance decision
            pi_data = self.scrum_agent.initiate_pi_planning(decision)
            print(f"   📅 Program Increment {pi_data['pi_number']} initiated")
            print(f"   👥 Teams involved: {', '.join(pi_data['teams'])}")
            
            # 2.2 Create epics from governance decision
            epics = self.scrum_agent.create_epics_from_governance(decision)
            print(f"   📊 Created {len(epics)} epics:")
            for epic in epics:
                print(f"      • {epic.title} (Value: {epic.business_value}, Effort: {epic.effort_estimate})")
            
            # 2.3 Plan sprints
            sprint_plan = self.scrum_agent.plan_sprints()
            print(f"   ⚡ Sprint plan created: {sprint_plan['utilization_percentage']:.1f}% capacity utilization")
            
            # 2.4 Execute first sprint
            sprint_results = self.scrum_agent.execute_sprint(sprint_plan["sprints"][0])
            print(f"   🏃 Sprint 1 executed: {sprint_results['velocity_percentage']:.1f}% velocity achieved")
            print(f"   🐛 Defects found: {sprint_results['defects_found']} (Rate: {sprint_results['defect_rate']:.1%})")
            
            # 2.5 Conduct retrospective
            retrospective = self.scrum_agent.conduct_retrospective(sprint_results)
            print(f"   🔄 Retrospective completed: {len(retrospective['improvement_actions'])} improvement actions")
            if retrospective["trigger_lean_six_sigma"]:
                print(f"   🚨 Quality issues detected - triggering Lean Six Sigma improvement")
            
            results["phases"]["agile"] = {
                "pi_planning": pi_data,
                "epics": [epic.dict() for epic in epics],
                "sprint_results": sprint_results,
                "retrospective": retrospective
            }
            
            # === PHASE 3: PROCESS IMPROVEMENT (Lean Six Sigma) ===
            if retrospective["trigger_lean_six_sigma"]:
                print("\n🔧 PHASE 3: PROCESS IMPROVEMENT (Lean Six Sigma)")
                print("-" * 50)
                
                # 3.1 Define improvement project
                project = self.lean_agent.initiate_improvement_project(retrospective)
                print(f"   📋 Project {project['project_id']} initiated")
                print(f"   🎯 Goal: {project['charter']['goal']}")
                
                # 3.2 Measure baseline
                baseline = self.lean_agent.establish_baseline_metrics()
                print(f"   📊 Baseline metrics established:")
                print(f"      • Defect rate: {baseline['defect_rate']:.1%}")
                print(f"      • Cycle time: {baseline['cycle_time_avg']:.1f} days")
                print(f"      • Process efficiency: {baseline['process_efficiency']:.1f}%")
                
                # 3.3 Analyze root causes
                defect_analyses = self.lean_agent.analyze_root_causes()
                print(f"   🔍 Root cause analysis completed: {len(defect_analyses)} defect types identified")
                for analysis in defect_analyses:
                    print(f"      • {analysis.defect_type}: {analysis.frequency} occurrences ({analysis.impact_severity} impact)")
                
                # 3.4 Design improvements
                improvements = self.lean_agent.design_improvements(defect_analyses)
                print(f"   💡 Improvement solutions designed: {len(improvements)} interventions")
                for improvement in improvements:
                    print(f"      • {improvement['area']}: {improvement['expected_impact']}")
                
                # 3.5 Implement control plan
                control_plan = self.lean_agent.implement_control_plan()
                print(f"   📈 Control plan implemented with {len(control_plan['control_metrics'])} metrics")
                print(f"   🎯 Expected benefits: {control_plan['expected_benefits']['defect_reduction']} defect reduction")
                
                results["phases"]["lean_six_sigma"] = {
                    "project": project,
                    "baseline": baseline,
                    "improvements": improvements,
                    "control_plan": control_plan
                }
            
            # === INTEGRATION POINTS ===
            integration_points = [
                {
                    "from": "Roberts Rules",
                    "to": "Scrum at Scale",
                    "trigger": f"Motion {motion.id} approved → PI Planning initiated",
                    "data_flow": "Governance decision scope drives epic creation"
                },
                {
                    "from": "Scrum at Scale", 
                    "to": "Lean Six Sigma",
                    "trigger": f"Defect rate {sprint_results['defect_rate']:.1%} > 5% threshold → Improvement project",
                    "data_flow": "Sprint metrics drive process improvement initiatives"
                },
                {
                    "from": "Lean Six Sigma",
                    "to": "Roberts Rules",
                    "trigger": "Control plan governance integration → Quarterly board review",
                    "data_flow": "Improvement results inform future governance decisions"
                }
            ]
            
            print("\n🔄 INTEGRATION POINTS")
            print("-" * 50)
            for point in integration_points:
                print(f"   {point['from']} → {point['to']}")
                print(f"      Trigger: {point['trigger']}")
                print(f"      Data: {point['data_flow']}")
            
            results["integration_points"] = integration_points
            
            # === FINAL OUTCOMES ===
            final_outcomes = {
                "governance_effectiveness": "Structured decision-making with clear audit trail",
                "agile_delivery": f"{sprint_results['velocity_percentage']:.1f}% velocity with {len(epics)} epics planned",
                "process_improvement": f"Expected {control_plan['expected_benefits']['defect_reduction'] if 'lean_six_sigma' in results['phases'] else '0'}% defect reduction",
                "organizational_maturity": "Integrated governance, agile delivery, and continuous improvement",
                "telemetry_validation": "All phases instrumented with OpenTelemetry spans",
                "demo_duration": f"{(datetime.now() - datetime.fromisoformat(results['demo_start'])).total_seconds():.1f} seconds"
            }
            
            results["final_outcomes"] = final_outcomes
            results["demo_end"] = datetime.now().isoformat()
            
            print("\n🎯 FINAL OUTCOMES")
            print("-" * 50)
            for key, value in final_outcomes.items():
                print(f"   {key.replace('_', ' ').title()}: {value}")
            
            span.set_attribute("demo.phases_completed", len(results["phases"]))
            span.set_attribute("demo.integration_points", len(integration_points))
            span.set_attribute("demo.duration_seconds", (datetime.now() - datetime.fromisoformat(results['demo_start'])).total_seconds())
            
            return results
    
    def generate_demo_artifacts(self, results: Dict) -> Dict:
        """Generate template-driven artifacts from demo results"""
        with tracer.start_as_current_span("demo.artifacts.generated") as span:
            artifacts = {}
            
            # Generate meeting minutes template
            if "governance" in results["phases"]:
                governance_data = results["phases"]["governance"]
                
                meeting_minutes_template = """
# Board Meeting Minutes
## Date: {{ demo_date }}
## Motion: {{ motion.title }}

### Motion Details
- **Moved by:** {{ motion.moved_by }}
- **Seconded by:** {{ motion.seconded_by }}
- **Description:** {{ motion.description }}

### Voting Results
- **For:** {{ outcome.votes.for }}
- **Against:** {{ outcome.votes.against }}
- **Abstentions:** {{ outcome.votes.abstentions }}
- **Result:** {{ outcome.outcome | upper }}

### Next Steps
- Impact Scope: {{ outcome.trigger_next }}
- Program Increment Planning initiated
- Expected delivery in 12 weeks

---
*Generated by DSLModel Organizational Transformation Demo*
"""
                
                artifacts["meeting_minutes"] = render(
                    meeting_minutes_template,
                    {
                        "demo_date": datetime.now().strftime("%Y-%m-%d"),
                        "motion": governance_data["motion"],
                        "outcome": governance_data["outcome"]
                    }
                )
            
            # Generate sprint plan template
            if "agile" in results["phases"]:
                agile_data = results["phases"]["agile"]
                
                sprint_plan_template = """
# Program Increment Sprint Plan
## PI: {{ pi_planning.pi_number }}
## Duration: {{ pi_planning.start_date }} to {{ pi_planning.end_date }}

### Epics
{% for epic in epics %}
- **{{ epic.title }}**
  - Business Value: {{ epic.business_value }}
  - Effort: {{ epic.effort_estimate }} story points
  - Teams: {{ epic.teams_involved | join(', ') }}
{% endfor %}

### Sprint 1 Results
- Planned Points: {{ sprint_results.planned_points }}
- Completed Points: {{ sprint_results.completed_points }}
- Velocity: {{ "%.1f" | format(sprint_results.velocity_percentage) }}%
- Defects Found: {{ sprint_results.defects_found }}

### Retrospective Actions
{% for action in retrospective.improvement_actions %}
- {{ action }}
{% endfor %}

---
*Generated by DSLModel Scrum at Scale Integration*
"""
                
                artifacts["sprint_plan"] = render(
                    sprint_plan_template,
                    agile_data
                )
            
            # Generate improvement report template
            if "lean_six_sigma" in results["phases"]:
                lean_data = results["phases"]["lean_six_sigma"]
                
                improvement_report_template = """
# Lean Six Sigma Improvement Report
## Project: {{ project.project_id }}
## Charter: {{ project.charter.problem_statement }}

### Baseline Metrics
- Defect Rate: {{ "%.1f" | format(baseline.defect_rate * 100) }}%
- Cycle Time: {{ baseline.cycle_time_avg }} days
- Process Efficiency: {{ baseline.process_efficiency }}%

### Improvement Solutions
{% for improvement in improvements %}
- **{{ improvement.area }}**: {{ improvement.description }}
  - Expected Impact: {{ improvement.expected_impact }}
  - Implementation: {{ improvement.implementation_effort }}
  - Lean Principle: {{ improvement.lean_principle }}
{% endfor %}

### Expected Benefits
- Defect Reduction: {{ control_plan.expected_benefits.defect_reduction }}
- Cycle Time Improvement: {{ control_plan.expected_benefits.cycle_time_improvement }}
- Velocity Stabilization: {{ control_plan.expected_benefits.velocity_stabilization }}

---
*Generated by DSLModel Lean Six Sigma Integration*
"""
                
                artifacts["improvement_report"] = render(
                    improvement_report_template,
                    lean_data
                )
            
            span.set_attribute("artifacts.generated_count", len(artifacts))
            
            return artifacts

# =====================================================
# 5. CLI DEMO INTERFACE
# =====================================================

async def run_8020_demo():
    """Run the 80/20 organizational transformation demo"""
    print("🚀 Starting 80/20 Organizational Transformation Demo")
    print("=" * 60)
    
    orchestrator = OrganizationalTransformationOrchestrator()
    
    # Run full demo
    results = await orchestrator.run_full_transformation_demo()
    
    # Generate artifacts
    print("\n📄 GENERATING DEMO ARTIFACTS")
    print("-" * 50)
    artifacts = orchestrator.generate_demo_artifacts(results)
    
    # Save results
    output_dir = Path("demo_output")
    output_dir.mkdir(exist_ok=True)
    
    # Save JSON results
    with open(output_dir / "transformation_demo_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    # Save artifacts
    for name, content in artifacts.items():
        with open(output_dir / f"{name}.md", "w") as f:
            f.write(content)
    
    print(f"   📁 Results saved to: {output_dir}")
    print(f"   📊 JSON results: transformation_demo_results.json")
    for name in artifacts.keys():
        print(f"   📝 {name.replace('_', ' ').title()}: {name}.md")
    
    print("\n✅ DEMO COMPLETED SUCCESSFULLY")
    print(f"   Duration: {results['final_outcomes']['demo_duration']} seconds")
    print(f"   Phases: {len(results['phases'])}")
    print(f"   Integration Points: {len(results['integration_points'])}")
    
    return results

if __name__ == "__main__":
    asyncio.run(run_8020_demo())