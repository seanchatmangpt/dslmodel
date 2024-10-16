import logging
from functools import reduce

from pydantic import Field

from dslmodel import DSLModel, init_instant


def from_prompt_chain(initial_prompt: str, models: list[type[DSLModel]]) -> list[DSLModel]:
    """
    Executes a chain of DSLModel.from_prompt calls, where the result of one is passed as the prompt to the next.

    Args:
        initial_prompt (str): The initial prompt to start the chain.
        models (List[Type[DSLModel]]): A list of DSLModel subclasses to be instantiated in sequence.

    Returns
    -------
        List[DSLModel]: A list of instantiated DSLModel objects resulting from the chain.
    """
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        logging.basicConfig(level=logging.INFO)

    accumulator_str = initial_prompt

    def chain(accumulator: list[DSLModel], model_class: type[DSLModel]) -> list[DSLModel]:
        """
        Helper function for reduce to execute from_prompt and accumulate results.

        Args:
            accumulator (List[DSLModel]): The list of previously instantiated models.
            model_class (Type[DSLModel]): The current DSLModel subclass to instantiate.

        Returns
        -------
            List[DSLModel]: Updated list of instantiated models.
        """
        nonlocal accumulator_str  # Ensure accumulator_str is updated outside of the function
        prompt = accumulator_str

        logger.debug(f"Prompt for {model_class.__name__}: {prompt}")

        try:
            # Instantiate the current model using from_prompt
            model_instance = model_class.from_prompt(prompt)
            logger.info(f"Successfully instantiated {model_class.__name__}")

            # Append the generated result to the accumulator_str for the next model
            accumulator_str += f"\n{model_instance!s}"

            return accumulator + [model_instance]
        except Exception as e:
            logger.error(f"Error instantiating {model_class.__name__} with prompt '{prompt}': {e}")
            # Depending on requirements, you can choose to append None or skip
            return accumulator + [None]

    # Use reduce to apply the chain function across the models list
    results = reduce(chain, models, [])

    return results


class Task(DSLModel):
    """
    Represents a task within a work session.
    """

    name: str = Field(..., description="The name of the task.")
    description: str | None = Field(None, description="A brief description of the task.")
    duration_minutes: int = Field(..., description="Estimated duration to complete the task.")
    status: str = Field(
        "Pending", description="Current status of the task (e.g., Pending, In Progress, Completed)."
    )


class SMARTGoal(DSLModel):
    """
    Defines a SMART (Specific, Measurable, Achievable, Relevant, Time-bound) goal with detailed fields for each criterion.

    Attributes
    ----------
        title (str): A concise name or label for the goal, capturing its essence.
        specific (str): A clear and detailed explanation of the exact outcome to be achieved.
        measurable (str): Quantifiable or observable metrics that track progress toward the goal's completion.
        achievable (str): The specific conditions, resources, or criteria that make the goal realistic and attainable.
        relevant (str): The explicit link between the goal and broader organizational or personal objectives, ensuring alignment.
        time_bound (str): A defined start and end period or deadline for achieving the goal, ensuring time constraints are respected.
    """

    title: str = Field(..., description="A concise name or label for the goal.")
    specific: str = Field(
        ..., description="Detailed explanation of the exact outcome to be achieved."
    )
    measurable: str = Field(
        ..., description="Quantifiable or observable metrics to track progress."
    )
    achievable: str = Field(
        ..., description="Specific criteria or conditions that make the goal attainable."
    )
    relevant: str = Field(..., description="How the goal aligns with broader objectives.")
    time_bound: str = Field(
        ..., description="The defined timeframe or deadline for achieving the goal."
    )


class EndOfDayJournalEntry(DSLModel):
    """
    Represents a journal entry at the end of the day.
    """

    date: str = Field(..., description="The date of the journal entry.")
    content: str = Field(..., description="The content of the journal entry.")


def main():
    """Main function"""
    # Define the initial prompt
    initial_prompt = "Grocery shopping for milk, cheese, and bread. Verbose responses"

    # Define the list of models in the desired sequence
    models_chain = [SMARTGoal, Task, EndOfDayJournalEntry]

    # init_text()
    init_instant()

    # Execute the from_prompt_chain function
    chain_results = from_prompt_chain(initial_prompt, models_chain)

    # Access and print the results
    for idx, result in enumerate(chain_results):
        if result:
            print(f"Result {idx + 1} ({result.__class__.__name__}): {result}")
        else:
            print(f"Result {idx + 1}: Failed to instantiate the model.")


if __name__ == "__main__":
    main()
