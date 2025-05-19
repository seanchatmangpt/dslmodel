from typing import Any, Dict, List
from pydantic import BaseModel, Field
from pydantic_ai import Agent

from dslmodel.utils.pydantic_ai_tools import instance, run_agent


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

async def get_workflow_agent() -> Agent[Dict[str, Any]]:
    """Create a workflow agent.
    
    Returns:
        An agent configured for workflow tasks
    """
    return Agent(
        "groq:llama-3.1-8b-instant",
        output_type=Dict[str, Any],
        system_prompt="You are a workflow manager. Execute tasks in sequence. "
                     "Always return a JSON object with keys 'task' and 'result'.",
        retries=0,  # No retries
    )


# ------------------------------------------
# Workflow Tools (Tasks)
# ------------------------------------------

async def task_1(deps: WorkflowDeps) -> Dict[str, Any]:
    """
    Task 1: Processes user input and updates the shared state.
    
    Args:
        deps: The workflow dependencies
        
    Returns:
        The task result
    """
    user_input = deps.user_input
    result = f"Processed '{user_input}' in Task 1."
    deps.task_1_result = result
    return WorkflowResult(task="Task 1", result=result).model_dump()


async def task_2(deps: WorkflowDeps) -> Dict[str, Any]:
    """
    Task 2: Builds on Task 1's result and updates the shared state.
    
    Args:
        deps: The workflow dependencies
        
    Returns:
        The task result
    """
    if not deps.task_1_result:
        raise ValueError("Task 1 result is missing.")
    result = f"Task 2 received: {deps.task_1_result}."
    deps.task_2_result = result
    return WorkflowResult(task="Task 2", result=result).model_dump()


# ------------------------------------------
# Workflow Manager
# ------------------------------------------

class Workflow:
    """
    Manages the execution of tasks in a sequence, using the agent and shared state.
    """

    def __init__(self, prompts: List[str], initial_state: WorkflowDeps):
        """Initialize the workflow.
        
        Args:
            prompts: List of prompts to execute
            initial_state: Initial workflow state
        """
        self.prompts = prompts
        self.state = initial_state
        self.agent = None

    async def run(self) -> WorkflowDeps:
        """
        Executes all tasks sequentially.
        
        Returns:
            The final workflow state
        """
        if self.agent is None:
            self.agent = await get_workflow_agent()
            
        for prompt in self.prompts:
            try:
                result = await run_agent(self.agent, prompt, deps=self.state)
                print(f"Prompt '{prompt}' completed. Result: {result}")
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
