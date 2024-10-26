import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

from pydantic import Field

from dslmodel import DSLModel, init_log, log_debug, log_info, log_error  # Assuming DSLModel is defined
from dslmodel.utils.dspy_tools import init_instant, init_text


def run_dsls(tasks: list[tuple[type(DSLModel), str]], max_workers=5) -> list[DSLModel]:
    """
    Execute a list of (DSLModel subclass, prompt) tuples concurrently and return the results in the same order.
    """
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        logging.basicConfig(level=logging.INFO)

    def run_task(index: int, model_class: type(DSLModel), prompt: str) -> tuple[int, DSLModel]:
        """Generate model instance from prompt, return result along with task index."""
        logger.debug(f"Starting task {index} with prompt: {prompt}")
        try:
            model_instance = model_class.from_prompt(prompt)
            logger.debug(f"Task {index} completed successfully.")
            return index, model_instance
        except Exception as e:
            logger.error(f"Task {index} failed with error: {e}")
            raise

    # Use a ThreadPoolExecutor to run tasks concurrently
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(run_task, i, model_class, prompt): i
            for i, (model_class, prompt) in enumerate(tasks)
        }

        results: list[DSLModel | None] = [None] * len(tasks)

        for future in as_completed(futures):
            try:
                index, result = future.result()
                results[index] = result
            except Exception as e:
                logger.error(f"Error in task {futures[future]}: {e}")

    return results


import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import reduce
from dslmodel import DSLModel  # Assuming DSLModel is defined
from dslmodel.utils.dspy_tools import init_instant


import logging
from typing import List
from pydantic import Field

from dslmodel import DSLModel, init_log, init_instant


def model_to_string_values(model_instance: DSLModel) -> str:
    """
    Converts a DSLModel instance into a string representation that includes only the values.

    Args:
        model_instance (DSLModel): The model instance to extract values from.

    Returns:
        str: A string containing the values of the model instance, separated by commas.
    """
    # Extract all values from the model's fields without field names.
    values = [str(value) for value in model_instance.dict().values()]
    return ", ".join(values)


def from_prompt_chain(initial_prompt: str, models: List[type[DSLModel]]) -> List[DSLModel]:
    current_prompt = initial_prompt
    results = []
    previous_analyses = []

    for idx, model_class in enumerate(models):
        log_debug(f"Using prompt for {model_class.__name__}: {current_prompt}")

        try:
            # Generate the model instance using from_prompt
            model_instance = model_class.from_prompt(current_prompt)
            log_info(f"Generated {model_class.__name__}: {model_instance}")

            # Store the generated model instance
            results.append(model_instance)

            # Append the current analysis to the list of previous analyses
            previous_analyses.append(model_instance.analysis)

            # Build the new prompt dynamically without hardcoding
            analyses_text = "\n\nPrevious results:\n" + "\n".join(f"- {a}" for a in previous_analyses)
            current_prompt = f"{initial_prompt}{analyses_text}\n\n. What is next?"

            log_info(f"Updated prompt: {current_prompt}")
        except Exception as e:
            log_error(f"Failed to generate {model_class.__name__} with prompt '{current_prompt}': {e}")
            results.append(None)

    return results



def main():
    init_text(temperature=1)

    class Perspective(DSLModel):
        name: str = Field(..., description="Name of the perspective.")
        analysis: str = Field(..., description="Analysis details from this perspective.")

    class ScenarioAnalysis(DSLModel):
        perspectives: List[Perspective] = Field(..., description="Different perspectives for analysis.")

    initial_prompt = "Analyze the impact of remote work."
    models_chain = [Perspective, Perspective, Perspective]

    # Generate perspectives for a scenario analysis using from_prompt_chain
    analysis_result = from_prompt_chain(initial_prompt, models_chain)
    print("Scenario Analysis:", analysis_result)


if __name__ == "__main__":
    main()
