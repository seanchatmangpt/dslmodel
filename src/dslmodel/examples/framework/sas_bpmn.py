from typing import List

from dslmodel.examples.framework.camunda_house_bpmn_models import *
from dslmodel.examples.framework.scrum_at_scale_models import *

# Assume all classes are imported from their respective modules:
# Task, Event, Gateway, SequenceFlow, CamundaTask, CamundaServiceTask, CamundaProcess, CamundaHouseBPMN,
# ScrumTeam, ScrumOfScrums, ExecutiveActionTeam, ExecutiveMetaScrumTeam,
# SprintBacklog, ScrumOfScrumsMaster, ChiefProductOwner, ProductOwnerCycle,
# ScrumMasterCycle, ScaledWorkflow, ScrumEvent, Dependency, Metrics

from typing import List

# Assume all classes are imported from their respective modules:
# Task, Event, Gateway, SequenceFlow, CamundaTask, CamundaServiceTask, CamundaProcess, CamundaHouseBPMN,
# ScrumTeam, ScrumOfScrums, ExecutiveActionTeam, ExecutiveMetaScrumTeam,
# SprintBacklog, ScrumOfScrumsMaster, ChiefProductOwner, ProductOwnerCycle,
# ScrumMasterCycle, ScaledWorkflow, ScrumEvent, Dependency, Metrics

# Step 1: Define BPMN Elements that correspond to Scrum Events and Activities


ScaledWorkflow.update_forward_refs()


def main():
    """Main function"""
    from dslmodel import init_lm, init_instant, init_text
    init_instant()

    # Create BPMN Tasks for Scrum Events
    sprint_planning_task = Task(
        task_id="task-001",
        task_name="Sprint Planning",
        task_description="Define the scope and goals for the next Sprint.",
        task_type="user task"
    )

    daily_scrum_task = Task(
        task_id="task-002",
        task_name="Daily Scrum",
        task_description="Daily meeting to discuss progress and impediments.",
        task_type="user task"
    )

    sprint_review_task = Task(
        task_id="task-003",
        task_name="Sprint Review",
        task_description="Review completed work and gather feedback.",
        task_type="user task"
    )

    sprint_retrospective_task = Task(
        task_id="task-004",
        task_name="Sprint Retrospective",
        task_description="Reflect on the past Sprint and plan improvements.",
        task_type="user task"
    )

    # Create BPMN Events
    start_event = Event(
        event_id="event-001",
        event_name="Sprint Start",
        event_type="start event",
        event_description="Marks the beginning of the Sprint."
    )

    end_event = Event(
        event_id="event-002",
        event_name="Sprint End",
        event_type="end event",
        event_description="Marks the completion of the Sprint."
    )

    # Create BPMN Sequence Flows to connect the events and tasks
    sequence_flows = [
        SequenceFlow(
            flow_id="flow-001",
            source_ref=start_event.event_id,
            target_ref=sprint_planning_task.task_id,
            condition=None
        ),
        SequenceFlow(
            flow_id="flow-002",
            source_ref=sprint_planning_task.task_id,
            target_ref=daily_scrum_task.task_id,
            condition=None
        ),
        SequenceFlow(
            flow_id="flow-003",
            source_ref=daily_scrum_task.task_id,
            target_ref=sprint_review_task.task_id,
            condition=None
        ),
        SequenceFlow(
            flow_id="flow-004",
            source_ref=sprint_review_task.task_id,
            target_ref=sprint_retrospective_task.task_id,
            condition=None
        ),
        SequenceFlow(
            flow_id="flow-005",
            source_ref=sprint_retrospective_task.task_id,
            target_ref=end_event.event_id,
            condition=None
        )
    ]

    # Step 2: Create Camunda Process incorporating the BPMN elements
    camunda_process = CamundaProcess(
        process_id="process-001",
        process_name="Agile Sprint Process",
        tasks=[sprint_planning_task, daily_scrum_task, sprint_review_task, sprint_retrospective_task],
        events=[start_event, end_event],
        gateways=[],  # No gateways in this example
        sequence_flows=sequence_flows,
        execution_listener="com.example.listeners.ProcessExecutionListener",
        start_event_listener="com.example.listeners.StartEventListener",
        end_event_listener="com.example.listeners.EndEventListener"
    )

    # Step 3: Create CamundaHouseBPMN that represents the entire process
    camunda_house_bpmn = CamundaHouseBPMN(
        house_id="house-001",
        bpmn_process=camunda_process,
        model_description="This model represents the Agile Sprint process in Camunda BPMN, integrating Scrum events and activities."
    )

    # Step 4: Define Scrum Teams
    team1 = ScrumTeam(
        team_id="team-001",
        scrum_master="SM_John_Doe",
        product_owner="PO_Jane_Smith",
        developers=["Dev_1", "Dev_2", "Dev_3"],
        backlog=["Task_A", "Task_B", "Task_C"]
    )

    team2 = ScrumTeam(
        team_id="team-002",
        scrum_master="SM_Sarah_Johnson",
        product_owner="PO_Tom_Williams",
        developers=["Dev_4", "Dev_5", "Dev_6"],
        backlog=["Task_D", "Task_E", "Task_F"]
    )

    # Step 5: Create ScrumOfScrums instance
    sos = ScrumOfScrums(
        sos_id="sos-001",
        teams=[team1, team2],
        impediments=["Dependency on shared API between team-001 and team-002"],
        decisions=["Resolve API dependency in Sprint 3"]
    )

    # Step 6: Create ExecutiveActionTeam instance
    eat = ExecutiveActionTeam(
        eat_id="eat-001",
        scrum_masters=["SM_John_Doe", "SM_Sarah_Johnson"],
        organizational_impediments=["Scaling issue with new project management tool in Sprint 2"],
        actions_taken=[
            "Added more capacity for development in Sprint 3",
            "Integrated new project management tool training for all teams"
        ]
    )

    # Step 7: Create ExecutiveMetaScrumTeam instance
    emt = ExecutiveMetaScrumTeam(
        emt_id="emt-001",
        executives=["CEO_Mary_Jones", "CTO_Alex_Taylor"],
        organizational_backlog=[
            "Strategic Initiative: AI-powered automation in Q4"
        ]
    )

    # Step 8: Create SprintBacklog instance
    sprint_backlog = SprintBacklog(
        backlog_id="backlog-001",
        team_backlog=["Task_A", "Task_D"],
        sos_backlog=["Coordinate API dependency between team-001 and team-002"],
        organizational_backlog=["AI-Powered Automation project", "Data Privacy Enhancements"]
    )

    # Step 9: Create ScrumOfScrumsMaster instance
    sosm = ScrumOfScrumsMaster(
        sosm_id="sosm-001",
        scrum_of_scrums_id="sos-001",

        responsibilities=[
            "Facilitate cross-team coordination",
            "Ensure impediments are resolved across teams"
        ],
        teams=[team1, team2]
    )

    # Step 10: Create ChiefProductOwner instance
    cpo = ChiefProductOwner(
        cpo_id="cpo-001",
        product_owner_team=["PO_Jane_Smith", "PO_Tom_Williams"],
        responsibilities=[
            "Ensure product alignment with strategic goals",
            "Backlog prioritization",
            "Stakeholder communication"
        ]
    )

    # Step 11: Create ProductOwnerCycle instance
    product_owner_cycle = ProductOwnerCycle(
        cycle_id="cycle-001",
        cpo=cpo,
        backlog_items=[
            "New feature prioritization for user experience",
            "API improvements for external integration"
        ]
    )

    # Step 12: Create ScrumMasterCycle instance
    scrum_master_cycle = ScrumMasterCycle(
        cycle_id="cycle-002",
        ssm=sosm,
        impediments=[
            "Cross-team dependency on shared resources for backend integration"
        ],
        cross_team_dependencies=[
            "API integration delay between team-001 and team-002"
        ]
    )

    # Step 13: Create ScaledWorkflow instance, integrating BPMN process
    scaled_workflow = ScaledWorkflow(
        workflow_id="workflow-001",
        teams=[team1, team2],
        scrum_of_scrums=sos,
        eat=eat,
        emt=emt,
        product_owner_cycle=product_owner_cycle,
        scrum_master_cycle=scrum_master_cycle,
        bpmn_process=camunda_process  # Added field in class definition
    )

    # Step 14: Create ScrumEvent instances, linking to BPMN Tasks
    event1 = ScrumEvent(
        event_id="event-001",
        name="Sprint Planning",
        participants=["SM_John_Doe", "PO_Jane_Smith", "Dev_1", "Dev_2"],
        outcome="Defined scope for next Sprint",
        frequency="Bi-weekly"
    )

    event2 = ScrumEvent(
        event_id="event-002",
        name="Daily Scrum",
        participants=["Dev_1", "Dev_2", "Dev_3"],
        outcome="Discussed blockers, API integration issue highlighted",
        frequency="Daily"
    )

    # Map Scrum Events to BPMN Tasks (for traceability)
    scrum_event_to_bpmn_task = {
        event1.event_id: sprint_planning_task.task_id,
        event2.event_id: daily_scrum_task.task_id
    }

    # Step 15: Create Dependency instance
    dependency = Dependency(
        dependency_id="dep-001",
        description="API shared between team-001 and team-002",
        blocked_team="team-001",
        blocking_team="team-002",
        resolution="Agreed to resolve in Sprint 3",
        status="In Progress"
    )

    # Step 16: Create Metrics instances
    metric1 = Metrics(
        metric_id="metric-001",
        name="Team Velocity",
        value=24.5,
        target_value=30.0,
        trend="Improving"
    )

    metric2 = Metrics(
        metric_id="metric-002",
        name="Defect Rate",
        value=3.2,
        target_value=2.0,
        trend="Stable"
    )

    # Step 17: Integrate BPMN and Scrum@Scale models
    # The integration is already done in Step 13 by including the BPMN process in the ScaledWorkflow

    # Optionally, add the BPMN tasks as activities in the Sprint Backlog
    sprint_backlog.team_backlog.extend([
        sprint_planning_task.task_name,
        daily_scrum_task.task_name,
        sprint_review_task.task_name,
        sprint_retrospective_task.task_name
    ])

    # Map Scrum Teams to BPMN Participants (if modeling BPMN Pools/Lanes)
    # For simplicity, let's assume each team corresponds to a BPMN Lane
    bpmn_lanes = {
        team1.team_id: "Lane_Team_001",
        team2.team_id: "Lane_Team_002"
    }

    # Example of accessing data and demonstrating the connections
    print(f"Camunda Process Name: {camunda_process.process_name}")
    print(f"Process Tasks: {[task.task_name for task in camunda_process.tasks]}")
    print(f"Scaled Workflow ID: {scaled_workflow.workflow_id}")
    print(f"Associated BPMN Process ID: {scaled_workflow.bpmn_process.process_id}")
    print(f"Teams in Scaled Workflow: {[team.team_id for team in scaled_workflow.teams]}")
    print(f"Sprint Backlog Items: {sprint_backlog.team_backlog}")
    print(f"Scrum Event to BPMN Task Mapping: {scrum_event_to_bpmn_task}")
    print(f"Dependencies: {dependency.description} between {dependency.blocked_team} and {dependency.blocking_team}")
    print(f"Metrics: {[metric.name + ': ' + str(metric.value) for metric in [metric1, metric2]]}")


if __name__ == '__main__':
    main()


