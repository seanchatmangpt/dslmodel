import pytest
from dslmodel import DSLModel
from dslmodel.utils.model_tools import run_dsls  # Assuming run_dsls is in model_tools


class ExampleDSLModel(DSLModel):
    field_1: str
    field_2: int

    @classmethod
    def from_prompt(cls, prompt: str) -> "ExampleDSLModel":
        # Simulate model creation based on the prompt
        data = {
            "field_1": prompt,
            "field_2": len(prompt)
        }
        return cls(**data)


def test_run_dsls_success():
    # List of tuples (DSLModel subclass, prompt) instead of DSLTask
    tasks = [
        (ExampleDSLModel, "test1"),
        (ExampleDSLModel, "test2"),
        (ExampleDSLModel, "test3")
    ]

    results = run_dsls(tasks)

    assert len(results) == 3
    assert isinstance(results[0], ExampleDSLModel)
    assert results[0].field_1 == "test1"
    assert results[1].field_1 == "test2"
    assert results[2].field_1 == "test3"


class ErrorDSLModel(DSLModel):
    @classmethod
    def from_prompt(cls, prompt: str) -> "ErrorDSLModel":
        raise ValueError("Error generating model")


def test_run_dsls_error_handling(caplog):
    # List of tuples (DSLModel subclass, prompt) with an error-generating model
    tasks = [
        (ExampleDSLModel, "valid"),
        (ErrorDSLModel, "error")
    ]

    run_dsls(tasks)

    # Ensure the log contains the failure message for the second task
    assert "Task 1 failed" in caplog.text


import time
import random
from unittest.mock import patch


class DelayedDSLModel(DSLModel):
    field: str

    @classmethod
    def from_prompt(cls, prompt: str) -> "DelayedDSLModel":
        # Simulate a delay in processing
        time.sleep(0.0000001 + random.uniform(0.001, 0.01))
        return cls(field=prompt)


@patch("time.sleep", return_value=None)  # Mock time.sleep to skip delays
def test_run_dsls_concurrency_and_order_preservation(mock_sleep):
    # List of tuples (DSLModel subclass, prompt)
    tasks = [
        (DelayedDSLModel, "task1"),
        (DelayedDSLModel, "task2"),
        (DelayedDSLModel, "task3")
    ]

    # Capture the start time
    start_time = time.time()

    # Run the DSL tasks concurrently
    results = run_dsls(tasks, max_workers=3)

    # Capture the end time
    end_time = time.time()

    # Since we mocked time.sleep, the actual execution should be extremely fast
    assert end_time - start_time < 0.001  # Expect instant execution

    # Check that the results preserve the input order
    assert len(results) == 3
    assert results[0].field == "task1"
    assert results[1].field == "task2"
    assert results[2].field == "task3"


def test_run_dsls_number_tuple_method():
    """
    Test using the number tuple method, dynamically varying a part of the prompt
    with an index or number using f-strings.
    """
    # Generate prompts dynamically using index numbers in f-strings
    tasks = [(ExampleDSLModel, f"Task {i}") for i in range(1, 6)]

    # Run tasks concurrently
    results = run_dsls(tasks)

    # Verify that the correct models were created and the prompts were used
    assert len(results) == 5
    for i, result in enumerate(results):
        assert result.field_1 == f"Task {i + 1}"  # Check that the prompt was properly used in the model
        assert result.field_2 == len(f"Task {i + 1}")  # Check the field length logic


# Running this test suite
if __name__ == '__main__':
    pytest.main()
