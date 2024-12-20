"""
The DSLModel Workflow Execution Module

This module introduces a comprehensive system for defining, managing, and executing complex workflows within the DSLModel framework. Utilizing a Domain-Specific Language (DSL), it empowers users to articulate intricate data processing and analysis tasks through a series of jobs, actions, and conditions. Designed with flexibility and ease of use in mind, the module caters to both seasoned developers and those new to programming or data science.

Key Concepts:
- Workflow: The central organizing structure that encapsulates a complete automated process. It is triggered by specified events and consists of one or more jobs that are executed to accomplish a task or series of tasks.
- Job: Represents a logical grouping of actions (steps) that are executed as part of the workflow. Jobs can be interdependent, with specific jobs waiting for others to complete before starting.
- Action: The atomic unit of work within a job, which can range from executing a predefined module with arguments, running custom Python code, to configuring environments variables. Actions can be conditionally executed or repeated over data collections through loops.
- Condition: A dynamic expression evaluated at runtime to determine whether certain actions should be executed. This allows for adaptive workflow behavior based on the current execution context.
- Loop: Enables repeated execution of actions over each item in an iterable, facilitating batch processing or iterative data manipulation within a workflow.

Features:
- Declarative Syntax: Leverages a YAML-based DSL for defining workflows, allowing for clear, readable configuration of complex logic and data flows.
- Dynamic Execution: Supports conditional logic and loops, enabling workflows to adapt to varying data and contexts dynamically.
- Modular Design: Encourages the modular composition of workflows into jobs and actions, promoting reuse and simplifying maintenance.

Usage:
The module is designed to be used programmatically within the DSLModel framework. Users define their workflows in YAML format, detailing the jobs, actions, conditions, and schedules that constitute the automated process. The DSLModel engine then interprets and executes these workflows, handling the orchestration of jobs, the evaluation of conditions, and the execution of actions as defined.

Intended for data scientists, developers, and analysts, this module simplifies the automation of complex data processing and analysis tasks, enabling users to focus on insights and innovation rather than the intricacies of workflow management.
"""

from datetime import datetime
from typing import Any, Union, Callable

from pydantic import Field

from dslmodel import DSLModel


class Condition(DSLModel):
    """
    Represents a conditional expression that can be evaluated to determine whether
    certain actions within a workflow should be executed. This class allows the
    definition of dynamic behavior based on the context of the workflow execution.

    The expression should be a valid Python expression that returns a Boolean value.
    """

    expr: str = Field(..., description="A Python expression as a string to evaluate the condition.")


class Action(DSLModel):
    """
    Describes an individual unit of work or operation to be performed as part of a job in the workflow.
    Actions can represent a wide range of operations, from executing a specific module with arguments,
    running custom Python code, to setting environments variables for the execution context.

    Conditional execution and looping over actions are supported to allow complex, dynamic workflows.
    """

    name: str = Field(..., description="The unique name of the action.")
    use: str | None = Field(None, description="Identifier for the module or action to be used.")
    args: dict[str, Any] | None = Field(
        None, description="Arguments to pass to the module or action."
    )
    code: str | None = Field(None, description="Python code to be executed directly.")
    env: dict[str, str] | None = Field(
        None,
        description="Environment variables accessible during the action's execution.",
    )
    cond: Condition | None = Field(
        None, description="Condition required to be true for the action to be executed."
    )
    callable: Callable[[dict[str, Any]], Any] | None = Field(
        None, description="A callable function that is executed when the action runs."
    )
    shell: str | None = Field(None, description="Shell command to be executed directly.")



class Job(DSLModel):
    """
    A job represents a collection of actions that are executed as part of the workflow. Each job
    can contain multiple steps (actions) and may depend on other jobs to complete before starting.
    This class enables the organization and modularization of workflow logic into coherent units
    of work that achieve specific objectives within the larger process.

    Jobs specify where they run, allowing for flexibility in execution environments.
    """

    name: str = Field("default", description="The unique name of the job.")
    depends_on: list[str] | None = Field(
        None,
        description="List of job names that this job depends on to complete before it starts.",
    )
    runner: str = Field(
        "local",
        description="Specification of where the job will run, such as a machine or container identifier.",
    )
    steps: list[Action] = Field(
        ..., description="A sequence of actions that are executed as part of this job."
    )
    env: dict[str, str] | None = Field(
        None, description="Environment variables accessible during the job's execution."
    )
    max_retries: int | None = Field(
        None, description="Maximum number of retry attempts for the job."
    )
    retry_delay_seconds: int | None = Field(
        None, description="Delay between retry attempts in seconds."
    )
    sla_seconds: int | None = Field(
        None, description="Service Level Agreement for the job completion, specified in seconds."
    )


class CronSchedule(DSLModel):
    type: str = Field("cron")
    cron: str = Field(..., description="Cron-like schedule for workflow triggering")


class DateSchedule(DSLModel):
    type: str = Field("date")
    run_date: str | datetime = Field(
        ..., description="Date and time to run the workflow, or 'now' for immediate execution"
    )


Schedule = Union[CronSchedule, DateSchedule]


class Workflow(DSLModel):
    """
    The top-level container for defining a sequence of operations, organized into jobs, to be executed
    when certain schedules occur. Workflows orchestrate the execution of jobs based on defined schedules,
    managing dependencies between jobs and ensuring the correct execution environments.

    This class serves as the blueprint for automating complex processes, linking together various
    actions into a cohesive, automated sequence that accomplishes a specific task or set of tasks.
    """

    name: str = Field(..., description="The unique name of the workflow.")
    description: str | None = Field(None, description="A brief description of the workflow.")
    schedules: list[CronSchedule | DateSchedule] = Field(
        [], description="List of schedules for the workflow execution."
    )
    jobs: list[Job] = Field(
        ..., description="A collection of jobs that are defined within the workflow."
    )
    imports: list[str] | None = Field(
        [], description="List of external workflow files to import and execute."
    )
    context: dict[str, Any] | None = Field(
        {}, description="Global context variables for the workflow execution."
    )
    env: dict[str, str] | None = Field(
        {}, description="Global environments variables for the workflow."
    )

    def process_imports(self) -> None:
        """Process imported workflows and integrate them into the current workflow."""
        for import_path in self.imports:
            imported_workflow = Workflow.from_yaml(import_path)
            # Integrate jobs from the imported workflow
            self.jobs.extend(imported_workflow.jobs)
            # Integrate or merge contexts if necessary
            self.context.update(imported_workflow.context)
            # Recursively process imports
            imported_workflow.process_imports()

    def topological_sort(self):
        from collections import deque

        jobs = self.jobs

        # Create a mapping from job name to job object for quick access
        job_map = {job.name: job for job in jobs}

        # Initialize a dictionary to count the number of dependencies each job has
        in_degree = {job.name: 0 for job in jobs}
        # A graph to keep track of jobs dependencies
        graph = {job.name: [] for job in jobs}

        # Build the graph
        for job in jobs:
            if job.depends_on:
                for dependency in job.depends_on:
                    graph[dependency].append(job.name)
                    in_degree[job.name] += 1

        # Find all jobs that have no dependencies to start the process
        queue = deque([job.name for job in jobs if in_degree[job.name] == 0])

        sorted_jobs = []

        while queue:
            current_job = queue.popleft()
            sorted_jobs.append(job_map[current_job])

            for dependent in graph[current_job]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        if len(sorted_jobs) != len(jobs):
            raise ValueError("There is a cycle in the job dependencies.")

        self.jobs = sorted_jobs

    def run(self):
        """Run the workflow."""
        from dslmodel.workflow.workflow_executor import schedule_workflow

        if not self.schedules:
            self.schedules = [DateSchedule(run_date="now")]

        schedule_workflow(self)
