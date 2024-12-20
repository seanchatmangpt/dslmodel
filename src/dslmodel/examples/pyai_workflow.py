from typing import Any, Dict, List
from pydantic import BaseModel, Field
from pydantic_ai import RunContext

from dslmodel.utils.pydantic_ai_tools import get_agent


# ------------------------------------------
# Shared State Model
# ------------------------------------------

class WorkflowDeps(BaseModel):
    """
    Shared dependencies for the workflow, representing the state passed between tasks.
    """
    user_input: str
    task_1_result: str = Field(default="", description="Output from Task 1.")
    task_2_result: str = Field(default="", description="Output from Task 2.")


# ------------------------------------------
# Task Result Model
# ------------------------------------------

class WorkflowResult(BaseModel):
    """
    Represents the result of a workflow task.
    """
    task: str
    result: str


# ------------------------------------------
# Workflow Agent Setup
# ------------------------------------------

workflow_agent = get_agent(
    system_prompt="You are a workflow manager. Execute tasks in sequence. "
                  "Always return a JSON object with keys 'task' and 'result'.",
    deps_type=WorkflowDeps,
    result_type=Dict[str, Any],  # Ensure JSON-compatible result structure
    retries=0,  # No retries
)


# ------------------------------------------
# Workflow Tools (Tasks)
# ------------------------------------------

@workflow_agent.tool
async def task_1(ctx: RunContext[WorkflowDeps]) -> Dict[str, Any]:
    """
    Task 1: Processes user input and updates the shared state.
    """
    user_input = ctx.deps.user_input
    result = f"Processed '{user_input}' in Task 1."
    ctx.deps.task_1_result = result
    return WorkflowResult(task="Task 1", result=result).model_dump()


@workflow_agent.tool
async def task_2(ctx: RunContext[WorkflowDeps]) -> Dict[str, Any]:
    """
    Task 2: Builds on Task 1's result and updates the shared state.
    """
    if not ctx.deps.task_1_result:
        raise ValueError("Task 1 result is missing.")
    result = f"Task 2 received: {ctx.deps.task_1_result}."
    ctx.deps.task_2_result = result
    return WorkflowResult(task="Task 2", result=result).model_dump()


# ------------------------------------------
# Workflow Manager
# ------------------------------------------

class Workflow:
    """
    Manages the execution of tasks in a sequence, using the agent and shared state.
    """

    def __init__(self, prompts: List[str], initial_state: WorkflowDeps):
        self.prompts = prompts
        self.state = initial_state

    async def run(self) -> WorkflowDeps:
        """
        Executes all tasks sequentially.
        """
        for prompt in self.prompts:
            try:
                result = await workflow_agent.run(prompt, deps=self.state)
                print(f"Prompt '{prompt}' completed. Result: {result.data}")
            except Exception as e:
                print(f"Error during prompt '{prompt}': {e}")
                raise
        return self.state


# ------------------------------------------
# Example Workflow Execution
# ------------------------------------------

async def main():
    """
    Entry point for the workflow execution.
    """
    # Initial shared state
    initial_state = WorkflowDeps(user_input="Example input")

    # Define the workflow sequence using explicit prompts
    workflow = Workflow(
        prompts=[
            "Run task_1 to process user input and return the result.",
            "Run task_2 to handle Task 1's result and return the result.",
        ],
        initial_state=initial_state,
    )

    # Run the workflow
    try:
        final_state = await workflow.run()
        print("Final Workflow State:", final_state.model_dump())
    except Exception as e:
        print(f"Workflow failed: {e}")


# ------------------------------------------
# Run the Workflow
# ------------------------------------------

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
