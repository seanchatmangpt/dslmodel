from pydantic import BaseModel, Field
from typing import List
from openai import OpenAI

from dslmodel import DSLModel

client = OpenAI()

# Define Pydantic models dynamically validated at runtime
class WorkflowRequirement(BaseModel):
    id: str = Field(..., description="Unique identifier for the requirement.")
    description: str = Field(..., description="Detailed explanation of the requirement.")
    parallelizable: bool = Field(..., description="Can the task be executed in parallel?")
    conditional: bool = Field(..., description="Does this task involve conditional logic?")
    iterative: bool = Field(..., description="Does this task involve iterative execution?")


class WorkflowPattern(BaseModel):
    workflow_pattern_number: int = Field(..., description="Number of the pattern from the 40 workflow patterns.")
    name: str = Field(..., description="Name of the workflow pattern.")
    description: str = Field(..., description="Detailed description of the pattern.")
    complexity: int = Field(..., description="Score representing the complexity of the pattern.")
    type: str = Field(..., description="Type of pattern (e.g., Parallel, Conditional).")


class WorkflowReasoningStep(BaseModel):
    step_number: int = Field(..., description="Step number in the reasoning process.")
    explanation: str = Field(..., description="Explanation of why this step was taken.")
    chosen_pattern: WorkflowPattern = Field(..., description="The workflow pattern chosen at this step.")


class WorkflowReasoningOutput(DSLModel):
    problem_context: str = Field(..., description="Overall context of the workflow problem.")
    requirements: List[WorkflowRequirement] = Field(..., description="List of extracted requirements.")
    reasoning_steps: List[WorkflowReasoningStep] = Field(
        ..., description="Step-by-step reasoning for workflow pattern selection."
    )
    final_patterns: List[WorkflowPattern] = Field(
        ..., description="The final set of workflow patterns chosen."
    )




def main():
    """Main function"""
    from dslmodel import init_lm, init_instant, init_text
    init_instant()

    workflow_reasoning = WorkflowReasoningOutput.from_prompt("You are an expert in workflow reasoning. "
                                                             "Given requirements, generate dynamic reasoning and final workflow patterns.")

    # Example output actions
    print(workflow_reasoning.to_yaml())

if __name__ == '__main__':
    main()
