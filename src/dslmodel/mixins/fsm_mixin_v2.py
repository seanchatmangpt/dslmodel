from enum import Enum

from transitions import State
from transitions import Machine
import asyncio

from pydantic_ai import Agent, RunContext
from pydantic import BaseModel
from typing import Optional

from dslmodel.mixins import FSMMixin, trigger
from dslmodel.utils.pydantic_ai_tools import get_agent


# Define the dependencies for the FSM Agent
class FSMDeps(BaseModel):
    current_state: str
    available_transitions: dict  # Maps triggers to destination states


# Define the result model for the FSM Agent
class FSMResult(BaseModel):
    next_trigger: Optional[str]  # Selected trigger, if any
    explanation: str  # Explanation of why this transition was chosen


# Create the FSM agent
fsm_agent = get_agent(
    deps_type=FSMDeps,
    result_type=FSMResult,
    system_prompt=(
        "You are a state machine decision-making assistant. "
        "Based on the current state and available transitions, select the most appropriate transition trigger. "
        "Explain your reasoning clearly."
    ),
)


# Define the fsm_trigger_call function
async def fsm_trigger_call(prompt: str, fsm, **kwargs) -> str:
    """
    Determine the next trigger for an FSM based on the provided prompt and state.

    Args:
        prompt: A description of the desired outcome.
        fsm: The FSM object that implements the state machine.
        kwargs: Additional context for decision-making.

    Returns:
        str: The chosen trigger for the FSM transition.
    """
    # Prepare dependencies
    available_transitions = {
        trigger: transition.dest
        for trigger, event in fsm.machine.events.items()
        for transition in event.transitions.get(fsm.state, [])
    }

    if not available_transitions:
        raise ValueError("No transitions available from the current state.")

    possible_triggers = "\n".join(
        [f"{trigger} -> {destination}" for trigger, destination in available_transitions.items()]
    )

    # Format the decision-making prompt
    decision_prompt = (
        f"```prompt\n{prompt}\n```\n\n"
        f"Choose from Possible State Transition Triggers based on prompt:\n\n"
        f"```possible_triggers\n{possible_triggers}\n```\n\n"
        f"You must choose one of the possible triggers to proceed."
    )

    # Prepare dependencies for the FSM Agent
    deps = FSMDeps(
        current_state=fsm.state,
        available_transitions=available_transitions,
    )

    # Run the agent with the formatted prompt
    result = await fsm_agent.run(decision_prompt, deps=deps)

    # Extract the trigger from the result
    chosen_trigger = result.data.next_trigger
    if not chosen_trigger:
        raise ValueError("No valid trigger selected by the agent.")

    # Execute the trigger
    fsm.trigger(chosen_trigger)
    return chosen_trigger


class StateEnum(Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class SimpleFSM(FSMMixin):
    def __init__(self):
        super().__init__()  # Initialize FSMMixin
        self.setup_fsm(self.StateEnum, initial=self.StateEnum.IDLE)

    @trigger(source="idle", dest="processing")
    def start(self):
        """
        Start processing from the idle state.
        """
        print("Transitioning from idle to processing.")

    @trigger(source="processing", dest="completed")
    def complete(self):
        """
        Complete processing and move to the completed state.
        """
        print("Transitioning from processing to completed.")

    @trigger(source="processing", dest="error")
    def fail(self):
        """
        Fail processing and move to the error state.
        """
        print("Transitioning from processing to error.")

    @trigger(source=["completed", "error"], dest="idle")
    def reset(self):
        """
        Reset the FSM to the idle state.
        """
        print("Resetting to the idle state.")

    def setup_transitions(self):
        """
        Add any additional manual transitions or overrides here if necessary.
        """
        pass

    def forward(self, prompt, **kwargs):
        """
        Decide and execute the next action based on a prompt.
        """
        return super().forward(prompt, **kwargs)


# Test the FSM and `fsm_trigger_call`
async def main():
    # Initialize the FSM
    fsm = SimpleFSM().machine

    print(f"Initial state: {fsm.state}")

    # Use fsm_trigger_call to decide the next transition
    try:
        # Prompt the agent for a decision
        next_trigger = await fsm_trigger_call(
            prompt="Process the item to completion.",
            fsm=fsm
        )
        print(f"Selected trigger: {next_trigger}")
        print(f"State after transition: {fsm.state}")
    except ValueError as e:
        print(f"Error: {e}")

    # Test another transition
    if fsm.state == "processing":
        next_trigger = await fsm_trigger_call(
            prompt="Finish the process successfully.",
            fsm=fsm
        )
        print(f"Selected trigger: {next_trigger}")
        print(f"State after transition: {fsm.state}")

    # Reset to idle
    if fsm.state in ["completed", "error"]:
        next_trigger = await fsm_trigger_call(
            prompt="Reset to the initial state.",
            fsm=fsm
        )
        print(f"Selected trigger: {next_trigger}")
        print(f"State after transition: {fsm.state}")


if __name__ == "__main__":
    asyncio.run(main())
