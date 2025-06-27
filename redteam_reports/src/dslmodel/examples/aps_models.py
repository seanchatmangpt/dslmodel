from pydantic import Field

from dslmodel import DSLModel
from dslmodel.utils.model_tools import run_dsls


class Task(DSLModel):
    """Represents a task in a simplified format for the LLM."""

    task_id: str = Field(..., description="Unique identifier for the task.")
    name: str = Field(..., description="Name of the task.")
    description: str | None = Field(None, description="Detailed description of the task.")
    assigned_to: list[str] = Field(default_factory=list, description="Roles assigned to the task.")
    status: str | None = Field("Not Started", description="Current status of the task.")
    start_date: str | None = Field(None, description="Start date of the task.")
    end_date: str | None = Field(None, description="End date of the task.")


class Subtask(DSLModel):
    """Represents a subtask with minimal fields."""

    subtask_id: str = Field(..., description="Unique identifier for the subtask.")
    name: str = Field(..., description="Name of the subtask.")
    assigned_to: list[str] = Field(
        default_factory=list, description="Roles assigned to the subtask."
    )
    status: str | None = Field("Not Started", description="Current status of the subtask.")


class Project(DSLModel):
    """Simplified project model with key fields."""

    name: str = Field(..., description="Name of the project.")
    description: str | None = Field(None, description="Description of the project.")
    tasks: list[Task] = Field(default_factory=list, description="List of tasks in the project.")


class BusinessRequirements(DSLModel):
    """Describes the business requirements for the project."""

    key_features: list[str] = Field(..., description="Key features required by the business.")
    target_audience: str = Field(..., description="Primary audience for the business requirements.")
    success_metrics: list[str] = Field(
        ..., description="Metrics to measure the success of business requirements."
    )


class Development(DSLModel):
    """Describes development setup, guidelines, and review processes."""

    setup_steps: list[str] = Field(..., description="Steps to set up the development environments.")
    build_command: str | None = Field(None, description="Command to build the project.")
    test_command: str | None = Field(None, description="Command to run tests.")
    guidelines: list[str] | None = Field(
        None, description="Guidelines to follow during development."
    )
    review_process: list[str] | None = Field(
        None, description="Process for reviewing the development work."
    )


class Deployment(DSLModel):
    """Represents deployment configurations, platforms, and environments."""

    platform: str = Field(..., description="Deployment platform used.")
    cicd_pipeline: str | None = Field(None, description="CI/CD pipeline configuration.")
    staging_environment: str | None = Field(None, description="Staging environments setup.")
    production_environment: str | None = Field(None, description="Production environments setup.")
    review_cycle: str | None = Field(None, description="Frequency of deployment reviews.")


class Interaction(DSLModel):
    """Defines an interaction between roles, specifying the type and involved roles."""

    interaction_type: str = Field(..., description="Type of interaction between roles.")
    with_role: str = Field(..., description="Role with which the interaction occurs.")
    description: str | None = Field(None, description="Description of the interaction.")
    notifications: list[str] | None = Field(
        None, description="Notifications triggered by the interaction."
    )


# class Subtask(DSLModel):
#     """Represents a subtask within a larger task, including its dependencies and interactions."""
#     subtask_id: str = Field(..., description="Unique identifier for the subtask.")
#     name: str = Field(..., description="Name of the subtask.")
#     assigned_to: List[str] = Field(..., description="Roles assigned to the subtask.")
#     dependencies: Optional[List[str]] = Field(None, description="List of task IDs that this subtask depends on.")
#     estimated_time: Optional[str] = Field(None, description="Estimated time to complete the subtask.")
#     interactions: Optional[List[Interaction]] = Field(None, description="Interactions involved in the subtask.")
#     status: Optional[str] = Field(None, description="Current status of the subtask.")
#     start_date: Optional[date] = Field(None, description="Start date of the subtask.")
#     end_date: Optional[date] = Field(None, description="End date of the subtask.")
#
#
# class Task(DSLModel):
#     """Represents a task, including its description, dependencies, and subtasks."""
#     task_id: str = Field(..., description="Unique identifier for the task.")
#     name: str = Field(..., description="Name of the task.")
#     description: Optional[str] = Field(None, description="Detailed description of the task.")
#     assigned_to: List[str] = Field(..., description="Roles assigned to the task.")
#     dependencies: Optional[List[str]] = Field(None, description="List of task IDs that this task depends on.")
#     interactions: Optional[List[Interaction]] = Field(None, description="Interactions involved in the task.")
#     subtasks: Optional[List[Subtask]] = Field(None, description="List of subtasks under this task.")
#     estimated_time: Optional[str] = Field(None, description="Estimated time to complete the task.")
#     priority: Optional[str] = Field(None, description="Priority level of the task.")
#     status: Optional[str] = Field(None, description="Current status of the task.")
#     start_date: Optional[date] = Field(None, description="Start date of the task.")
#     end_date: Optional[date] = Field(None, description="End date of the task.")
#     results: Optional[List[str]] = Field(None, description="Results or outputs from the task.")
#     scheduled_date: Optional[date] = Field(None, description="Scheduled date for the task.")


class Workflow(DSLModel):
    """Defines the workflow for the project, organizing tasks in a specific order."""

    workflow_type: str = Field(..., description="Type of workflow (Sequential or Parallel).")
    tasks: list[Task] = Field(
        ..., description="List of task IDs in the workflow order.", min_length=5
    )


# class Role(DSLModel):
#     """Represents a role in the project, with its responsibilities and type."""
#     name: str = Field(..., description="Name of the role.")
#     role_type: str = Field(..., description="Type of the role (Human or AI).")
#     description: Optional[str] = Field(None, description="Description of the role.")
#     responsibilities: Optional[List[str]] = Field(None, description="List of responsibilities for the role.")
#     abbreviation: Optional[str] = Field(None, description="Abbreviation for the role.")
#

# class Project(DSLModel):
#     """Represents a project, its roles, tasks, and overall workflow."""
#     name: str = Field(..., description="Name of the project.")
#     description: Optional[str] = Field(None, description="Description of the project.")
#     timeframe: Optional[Dict[str, date]] = Field(None, description="Start and end dates of the project.")
#     roles: List[str] = Field(..., description="List of roles involved in the project.")
#     tasks: List[Task] = Field(..., description="List of tasks within the project.")
#     workflow: Optional[Workflow] = Field(None, description="Workflow structure of the project.")
#


class Amendment(DSLModel):
    """Represents an amendment made during a meeting, including the vote required to pass it."""

    amendment_id: str = Field(..., description="Unique identifier for the amendment.")
    description: str = Field(..., description="Description of the amendment.")
    made_by: str = Field(..., description="Participant who made the amendment.")
    seconded_by: str | None = Field(None, description="Participant who seconded the amendment.")
    debate_allowed: bool = Field(
        ..., description="Indicates if debate is allowed on the amendment."
    )
    vote_required: str = Field(..., description="Type of vote required to pass the amendment.")
    debate: dict[str, list[str] | list[str]] | None = Field(
        None, description="Details of the debate if allowed."
    )


class Participant(DSLModel):
    """Represents a participant in a meeting."""

    name: str = Field("{{ fake_name() }}", description="Name of the participant.")
    role: str = Field("{{ fake_job() }}", description="Role of the participant.")


class Meeting(DSLModel):
    """Represents a meeting, its participants, agenda, and other details."""

    name: str = Field(..., description="Name of the meeting.")
    meeting_date: str = Field(..., description="Date of the meeting.")
    location: str | None = Field(None, description="Location where the meeting is held.")
    chairperson: Participant = Field(..., description="Chairperson of the meeting.")
    secretary: Participant = Field(..., description="Secretary responsible for taking minutes.")
    participants: list[Participant] = Field(
        ..., description="List of all participants in the meeting."
    )
    agenda: list[str] = Field(..., description="Agenda items for the meeting.", min_length=3)
    minutes: list[str] = Field(
        ..., description="Minutes of the meeting. Time, Description", min_length=3
    )
    rules_of_order: list[str] = Field(..., description="Rules governing the meeting.", min_length=3)


meeting_template = """Fortune 10 Board Meeting about implementing TOGAF with medallion architecture.
with {% for participant in participants %}{{ participant }}{% if not loop.last %}, {% endif %}{% endfor %}.

MAKE SURE ALL FIELDS ARE VERBOSE WITH RELEVANT EXAMPLE TEXT. WE NEED THIS TO BE ACTIONABLE.
"""


def main():
    """Main function"""
    participants = [Participant() for _ in range(10)]

    # Output the generated participants
    for i, participant in enumerate(participants):
        print(f"Participant {i+1}: {participant}")

    instance = Meeting.from_prompt(meeting_template, participants=participants)
    print(instance.to_yaml())

    for agenda_item in instance.agenda:
        new_task = Task.from_prompt(
            f"{agenda_item}\nMAKE SURE ALL FIELDS ARE VERBOSE WITH RELEVANT EXAMPLE TEXT. WE NEED THIS TO BE ACTIONABLE."
        )
        print(new_task.to_yaml())


def run_participants_concurrently():
    """Create 5 participants concurrently using the run_dsls function."""
    # Prepare tasks for creating 5 different participants concurrently
    from dslmodel.template import render

    tasks = [
        (
            Participant,
            render(
                "Generate participant {{fake_name()}}, {{ fake_job() }} for the board meeting. "
                "Start time {{ fake_time() }}"
            ),
        )
        for i in range(5)
    ]

    # Run tasks concurrently
    results = run_dsls(tasks, max_workers=5)

    # Output the generated participants
    for i, result in enumerate(results):
        print(f"Participant {i+1}: {result}")


if __name__ == "__main__":
    from dslmodel.utils.dspy_tools import init_text

    init_text()
    # init_instant()
    # run_participants_concurrently()
    main()

# if __name__ == '__main__':
#     main()
