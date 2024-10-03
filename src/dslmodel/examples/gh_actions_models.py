from __future__ import annotations
from typing import List, Optional, Union, Literal, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
import yaml

from dslmodel import DSLModel


class Trigger(DSLModel):
    """
    Represents the trigger section of a GitHub Actions workflow.
    """
    push: Optional[Dict[str, Any]] = Field(
        None, description="Configuration for push events."
    )
    pull_request: Optional[Dict[str, Any]] = Field(
        None, description="Configuration for pull request events."
    )
    schedule: Optional[List[Dict[str, str]]] = Field(
        None, description="Configuration for scheduled events."
    )


class ActionReference(BaseModel):
    """
    Represents a reference to a GitHub Action.
    """
    uses: str = Field(
        ..., description="The action to use, in the format 'owner/repo@ref'."
    )
    with_: Optional[Dict[str, Any]] = Field(
        None, alias="with", description="Input parameters for the action."
    )
    env: Optional[Dict[str, str]] = Field(
        None, description="Environment variables for the action."
    )


class Step(DSLModel):
    """
    Represents a single step within a job.
    """
    name: Optional[str] = Field(
        None, description="The name of the step."
    )
    uses: Optional[str] = Field(
        None, description="The action to use for this step."
    )
    run: Optional[str] = Field(
        None, description="The shell command to execute for this step."
    )
    with_: Optional[Dict[str, Any]] = Field(
        None, alias="with", description="Input parameters for the step."
    )
    env: Optional[Dict[str, str]] = Field(
        None, description="Environment variables for the step."
    )


class Job(DSLModel):
    """
    Represents a single job within a GitHub Actions workflow.
    """
    name: Optional[str] = Field(
        None, description="The name of the job."
    )
    runs_on: str = Field(
        "ubuntu-latest", description="The runner environment for the job. "
                         "Valid values are 'ubuntu-latest', 'macos-latest', and 'windows-latest'."
    )
    steps: List[Step] = Field(
        [], description="List of steps to execute in the job."
    )
    needs: Optional[List[str]] = Field(
        None, description="List of jobs that this job depends on."
    )
    env: Optional[Dict[str, str]] = Field(
        None, description="Environment variables for the job."
    )


class Workflow(DSLModel):
    """
    Represents a GitHub Actions workflow.
    """
    name: Optional[str] = Field(
        None, description="The name of the workflow."
    )
    on: Trigger = Field(
        ..., description="The events that trigger the workflow."
    )
    jobs: list[Job] = Field(
        [], description="Dictionary of jobs to execute in the workflow."
    )
    env: Optional[Dict[str, str]] = Field(
        None, description="Environment variables for the workflow."
    )


class GHActionsDocument(DSLModel):
    """
    Represents the entire GitHub Actions document.
    """
    workflow: Workflow = Field(
        ..., description="The Workflow defined in the GitHub Actions document."
    )


# Split the prompt into smaller parts
trigger_prompt = """Create a GitHub Actions workflow that triggers on push and pull_request events for the main and develop branches."""

job_prompt = """The workflow should run on ubuntu-latest and have a single job named CI."""

steps_prompt = """This job should contain the following steps: 
1. Check out the repository using the actions/checkout@v3 action.
2. Set up Python using actions/setup-python@v4 with Python version 3.9.
3. Install dependencies with the command pip install -r requirements.txt.
4. Run tests using pytest. Ensure the workflow is clean and excludes any unnecessary fields."""

def main():
    """Main function"""
    from dslmodel.utils.dspy_tools import init_lm, init_instant, init_text
    init_instant()

    # Create the trigger
    trigger = Trigger.from_prompt(trigger_prompt)

    # Create the job
    job = Job.from_prompt(job_prompt)

    # Create the steps
    steps = [
        Step.from_prompt("Check out the repository using the actions/checkout@v3 action."),
        Step.from_prompt("Set up Python using actions/setup-python@v4 with Python version 3.9."),
        Step.from_prompt("Install dependencies with the command pip install -r requirements.txt."),
        Step.from_prompt("Run tests using pytest.")
    ]

    # Assign steps to the job
    job.steps = steps

    # Create the workflow
    workflow = Workflow(
        name="CI Workflow",
        on=trigger,
        jobs=[job]
    )

    # Create the GHActionsDocument
    doc = GHActionsDocument(workflow=workflow)
    print(doc.to_yaml())

if __name__ == '__main__':
    main()

