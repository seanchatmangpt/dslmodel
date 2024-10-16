"""title: "Agile Protocol Specification (APS) for Scaled Agile Compliance"
tags: [#scrum, #agile, #scaled-agile, #aps, #scrumatscale]
date: 2024-10-11
status: Active

# Progressive Summary
This YAML representation of the Agile Protocol Specification (APS) highlights key elements of the Scrum@Scale implementation. It leverages the provided classes such as ScrumTeam, ScrumOfScrums, ExecutiveActionTeam, and others to model coordination, backlog management, cross-team dependencies, and organizational workflows.

# Scrum Teams and Scrum of Scrums
scrum_of_scrums:
  sos_id: "sos-001"
  teams:
    - team_id: "team-001"
      scrum_master: "SM_John_Doe"
      product_owner: "PO_Jane_Smith"
      developers: ["Dev_1", "Dev_2", "Dev_3"]
      backlog: ["Task_A", "Task_B", "Task_C"]
    - team_id: "team-002"
      scrum_master: "SM_Sarah_Johnson"
      product_owner: "PO_Tom_Williams"
      developers: ["Dev_4", "Dev_5", "Dev_6"]
      backlog: ["Task_D", "Task_E", "Task_F"]
  impediments: ["Dependency on shared API between team-001 and team-002"]
  decisions: ["Resolve API dependency in Sprint 3"]

# Executive Action Team (EAT)
executive_action_team:
  eat_id: "eat-001"
  scrum_masters: ["SM_John_Doe", "SM_Sarah_Johnson"]
  organizational_impediments:
    - "Scaling issue with new project management tool in Sprint 2"
  actions_taken:
    - "Added more capacity for development in Sprint 3"
    - "Integrated new project management tool training for all teams"

# Executive MetaScrum Team (EMT)
executive_meta_scrum_team:
  emt_id: "emt-001"
  executives: ["CEO_Mary_Jones", "CTO_Alex_Taylor"]
  organizational_backlog:
    - "Strategic Initiative: AI-powered automation in Q4"
  strategic_decisions:
    - "Prioritize automation and machine learning projects in next quarter"

# Sprint Backlog at Multiple Levels
sprint_backlog:
  backlog_id: "backlog-001"
  team_backlog: ["Task_A", "Task_D"]
  sos_backlog: ["Coordinate API dependency between team-001 and team-002"]
  organizational_backlog: ["AI-Powered Automation project", "Data Privacy Enhancements"]

# Chief Product Owner Cycle
product_owner_cycle:
  cycle_id: "cycle-001"
  cpo:
    cpo_id: "cpo-001"
    product_owner_team: ["PO_Jane_Smith", "PO_Tom_Williams"]
    responsibilities:
      - "Ensure product alignment with strategic goals"
      - "Backlog prioritization"
      - "Stakeholder communication"
  backlog_items:
    - "New feature prioritization for user experience"
    - "API improvements for external integration"

# Scrum Master Cycle
scrum_master_cycle:
  cycle_id: "cycle-002"
  ssm:
    sosm_id: "sosm-001"
    scrum_of_scrums_id: "sos-001"
    responsibilities:
      - "Facilitate cross-team coordination"
      - "Ensure impediments are resolved across teams"
    teams: ["team-001", "team-002"]
  impediments:
    - "Cross-team dependency on shared resources for backend integration"
  cross_team_dependencies:
    - "API integration delay between team-001 and team-002"

# Scrum Events
scrum_events:
  - event_id: "event-001"
    name: "Sprint Planning"
    participants: ["SM_John_Doe", "PO_Jane_Smith", "Dev_1", "Dev_2"]
    outcome: "Defined scope for next Sprint"
    frequency: "Bi-weekly"
  - event_id: "event-002"
    name: "Daily Scrum"
    participants: ["Dev_1", "Dev_2", "Dev_3"]
    outcome: "Discussed blockers, API integration issue highlighted"
    frequency: "Daily"

# Dependencies
dependencies:
  - dependency_id: "dep-001"
    description: "API shared between team-001 and team-002"
    blocked_team: "team-001"
    blocking_team: "team-002"
    resolution: "Agreed to resolve in Sprint 3"
    status: "In Progress"

# Metrics for Performance Tracking
metrics:
  - metric_id: "metric-001"
    name: "Team Velocity"
    value: 24.5
    target_value: 30
    trend: "Improving"
  - metric_id: "metric-002"
    name: "Defect Rate"
    value: 3.2
    target_value: 2.0
    trend: "Stable"

# Scaled Workflow for Coordination
scaled_workflow:
  workflow_id: "workflow-001"
  teams:
    - team_id: "team-001"
    - team_id: "team-002"
  scrum_of_scrums:
    sos_id: "sos-001"
    teams: ["team-001", "team-002"]
    impediments: ["API integration dependency"]
    decisions: ["Resolve by Sprint 3"]
  eat:
    eat_id: "eat-001"
    organizational_impediments: ["Scaling issue with project management tool"]
    actions_taken: ["Additional development resources allocated"]
  emt:
    emt_id: "emt-001"
    organizational_backlog: ["AI-powered automation in Q4"]
    strategic_decisions: ["Prioritize AI initiatives"]
  product_owner_cycle:
    cycle_id: "cycle-001"
    cpo:
      cpo_id: "cpo-001"
      product_owner_team: ["PO_Jane_Smith", "PO_Tom_Williams"]
    backlog_items: ["AI feature prioritization"]
  scrum_master_cycle:
    cycle_id: "cycle-002"
    ssm:
      sosm_id: "sosm-001"
      scrum_of_scrums_id: "sos-001"
    impediments: ["Cross-team API dependency"]
    cross_team_dependencies: ["Backend integration delays"]

---

# Key Insights:
This YAML breakdown showcases a scalable Scrum@Scale implementation through classes like ScrumTeam, ScrumOfScrums, and ExecutiveActionTeam. The system tracks cross-team dependencies, backlog prioritization, and organizational initiatives while ensuring efficient coordination through Product Owner and Scrum Master cycles. Metrics provide insight into team performance, while workflows ensure that organizational priorities, impediments, and cross-team coordination are handled systematically.
"""
from pydantic import Field
from dslmodel import DSLModel
from typing import List, TYPE_CHECKING



from dslmodel.examples.framework.camunda_house_bpmn_models import CamundaProcess


class ScrumTeam(DSLModel):
    team_id: str = Field(..., description="Unique identifier for the Scrum team.")
    scrum_master: str = Field(..., description="Scrum Master of the team.")
    product_owner: str = Field(..., description="Product Owner of the team.")
    developers: List[str] = Field(..., description="Developers in the team.")
    backlog: List[str] = Field(..., description="Tasks in the sprint backlog.")


class ScrumOfScrums(DSLModel):
    sos_id: str = Field(..., description="ID for the Scrum of Scrums.")
    teams: List[ScrumTeam] = Field(..., description="Teams involved in the SoS.")
    impediments: List[str] = Field(..., description="Impediments raised during SoS.")
    decisions: List[str] = Field(..., description="Decisions made to resolve impediments.")


class ExecutiveActionTeam(DSLModel):
    eat_id: str = Field(..., description="ID for the Executive Action Team.")
    scrum_masters: List[str] = Field(..., description="Scrum Masters at the executive level.")
    organizational_impediments: List[str] = Field(..., description="Issues affecting organization-wide processes.")
    actions_taken: List[str] = Field(..., description="Actions to resolve large-scale impediments.")


class ExecutiveMetaScrumTeam(DSLModel):
    emt_id: str = Field(..., description="ID for the Executive MetaScrum Team.")
    executives: List[str] = Field(..., description="Executives making strategic decisions.")
    organizational_backlog: List[str] = Field(..., description="High-level organizational tasks.")


class SprintBacklog(DSLModel):
    backlog_id: str = Field(..., description="Unique identifier for the backlog.")
    team_backlog: List[str] = Field(..., description="Backlog items at the Scrum team level.")
    sos_backlog: List[str] = Field(..., description="Backlog items coordinated between teams in the Scrum of Scrums.")
    organizational_backlog: List[str] = Field(..., description="Backlog items managed by the Executive MetaScrum Team (EMT).")


class OrganizationalBacklog(DSLModel):
    backlog_id: str = Field(..., description="Unique identifier for the organizational backlog.")
    initiatives: List[str] = Field(..., description="List of high-level organizational initiatives.")
    priority_items: List[str] = Field(..., description="Strategic items prioritized by the EMT for the organization.")


class ScrumOfScrumsMaster(DSLModel):
    sosm_id: str = Field(..., description="Unique identifier for the Scrum of Scrums Master.")
    scrum_of_scrums_id: str = Field(..., description="ID of the Scrum of Scrums the SoSM oversees.")
    responsibilities: List[str] = Field(..., description="List of responsibilities, including coordination and impediment removal.")
    teams: List[ScrumTeam] = Field(..., description="Teams under the Scrum of Scrums Master.")


class ChiefProductOwner(DSLModel):
    cpo_id: str = Field(..., description="Unique identifier for the Chief Product Owner.")
    product_owner_team: List[str] = Field(..., description="List of Product Owners in the Chief Product Owner's team.")
    responsibilities: List[str] = Field(..., description="Responsibilities include backlog prioritization, product alignment, and stakeholder communication.")


class ProductOwnerCycle(DSLModel):
    cycle_id: str = Field(..., description="Unique identifier for the Product Owner cycle.")
    cpo: ChiefProductOwner = Field(..., description="Chief Product Owner in charge of the Product Owner cycle.")
    backlog_items: List[str] = Field(..., description="List of items being prioritized by the Product Owner team.")


class ScrumMasterCycle(DSLModel):
    cycle_id: str = Field(..., description="Unique identifier for the Scrum Master cycle.")
    ssm: ScrumOfScrumsMaster = Field(..., description="Scrum of Scrums Master coordinating the Scrum Master cycle.")
    impediments: List[str] = Field(..., description="Impediments that need to be resolved at scale.")
    cross_team_dependencies: List[str] = Field(..., description="Dependencies that need to be coordinated across teams.")


class ScaledWorkflow(DSLModel):
    workflow_id: str = Field(..., description="Unique identifier for the Scrum@Scale workflow.")
    teams: List[ScrumTeam] = Field(..., description="List of Scrum Teams involved in the workflow.")
    scrum_of_scrums: ScrumOfScrums = Field(..., description="The Scrum of Scrums coordination mechanism.")
    eat: ExecutiveActionTeam = Field(..., description="The Executive Action Team responsible for organizational impediments.")
    emt: ExecutiveMetaScrumTeam = Field(..., description="The Executive MetaScrum Team overseeing the organizational backlog.")
    product_owner_cycle: ProductOwnerCycle = Field(..., description="Details of the Product Owner cycle.")
    scrum_master_cycle: ScrumMasterCycle = Field(..., description="Details of the Scrum Master cycle.")
    bpmn_process: "CamundaProcess" = Field(..., description="The BPMN process integrated into the scaled workflow.")



class ScrumEvent(DSLModel):
    event_id: str = Field(..., description="Unique identifier for the event.")
    name: str = Field(..., description="The name of the event, e.g., Sprint Planning, Daily Scrum.")
    participants: List[str] = Field(..., description="Participants in the event.")
    outcome: str = Field(..., description="Outcome or key decisions made during the event.")
    frequency: str = Field(..., description="How often the event occurs, e.g., daily, weekly.")


class Dependency(DSLModel):
    dependency_id: str = Field(..., description="Unique identifier for the dependency.")
    description: str = Field(..., description="Description of the dependency between teams.")
    blocked_team: str = Field(..., description="The team that is blocked by the dependency.")
    blocking_team: str = Field(..., description="The team that is causing the blockage.")
    resolution: str = Field(..., description="Description of how the dependency was resolved.")
    status: str = Field(..., description="Current status of the dependency (e.g., resolved, in progress).")


class Metrics(DSLModel):
    metric_id: str = Field(..., description="Unique identifier for the metric.")
    name: str = Field(..., description="Name of the metric, e.g., throughput, defect rate, team velocity.")
    value: float = Field(..., description="The current value of the metric.")
    target_value: float = Field(..., description="The target value for the metric.")
    trend: str = Field(..., description="Description of whether the metric is improving, worsening, or stable.")


