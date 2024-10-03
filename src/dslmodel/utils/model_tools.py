from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from typing import List, Tuple
from dslmodel import DSLModel  # Assuming DSLModel is defined
from dslmodel.utils.dspy_tools import init_instant


def run_dsls(tasks: List[Tuple[type(DSLModel), str]], max_workers=5) -> List[DSLModel]:
    """
    Execute a list of (DSLModel subclass, prompt) tuples concurrently and return the results in the same order.
    """
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        logging.basicConfig(level=logging.INFO)

    def run_task(index: int, model_class: type(DSLModel), prompt: str) -> Tuple[int, DSLModel]:
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
        futures = {executor.submit(run_task, i, model_class, prompt): i for i, (model_class, prompt) in enumerate(tasks)}

        results: List[DSLModel | None] = [None] * len(tasks)

        for future in as_completed(futures):
            try:
                index, result = future.result()
                results[index] = result
            except Exception as e:
                logger.error(f"Error in task {futures[future]}: {e}")

    return results


class ModelA(DSLModel):
    user_story: str


def main():
    init_instant()
    # Prepare tasks with the same model but dynamically varying prompt using f-string
    tasks = [
        (ModelA, f"Generate a model for task {i} for the user login feature.") for i in range(1, 6)  # Running the same prompt with varying index
    ]

    # Run tasks concurrently and get results in order
    results = run_dsls(tasks, max_workers=3)

    for i, result in enumerate(results):
        print(f"Result {i}: {result}")


if __name__ == '__main__':
    main()
