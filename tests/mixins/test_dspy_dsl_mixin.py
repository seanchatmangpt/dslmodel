import pytest
from typing import Any
from pydantic import BaseModel
from dslmodel.mixins.dspy_dsl_mixin import DSPyDSLMixin
import dspy
from dspy.utils.dummies import DummyLM


# Define a simple model inheriting from BaseModel and DSPyDSLMixin
class MyModel(BaseModel, DSPyDSLMixin):
    name: str
    value: int


@pytest.fixture(scope="function", autouse=True)
def configure_dspy_dummy():
    """
    Fixture that configures dspy with a DummyLM before each test.
    """
    # Set up DummyLM with a mocked response for 'root_model_kwargs_dict'
    lm = DummyLM([{"root_model_kwargs_dict": "{'name':'Test', 'value':42}"}])
    dspy.settings.configure(lm=lm)
    yield
    # No need for explicit teardown; pytest handles cleanup


# Test from_prompt method
def test_from_prompt():
    lm = DummyLM([{"root_model_kwargs_dict": "{'name':'Test', 'value':42}"}])
    dspy.settings.configure(lm=lm)

    prompt = "This is a test prompt"

    # Call from_prompt and check the returned model
    result = MyModel.from_prompt(prompt)

    # Ensure the model returned is of type MyModel and has the correct attributes
    assert isinstance(result, MyModel)
    assert result.name == "Test"
    assert result.value == 42


# Test from_template method
def test_from_template():
    lm = DummyLM([{"root_model_kwargs_dict": "{'name':'Test', 'value':42}"}])
    dspy.settings.configure(lm=lm)

    template = "This is a test template"

    # Call from_template and check the returned model
    result = MyModel.from_template(template)

    # Ensure the model returned is of type MyModel and has the correct attributes
    assert isinstance(result, MyModel)
    assert result.name == "Test"
    assert result.value == 42


# Test from_signature method
def test_from_signature():
    lm = DummyLM([
        {"result": "result"},
        {"root_model_kwargs_dict": "{'name':'Test', 'value':42}"}
    ])
    dspy.settings.configure(lm=lm)

    signature = "result -> result"

    # Call from_signature and check the returned model
    result = MyModel.from_signature(signature)

    # Ensure the model returned is of type MyModel and has the correct attributes
    assert isinstance(result, MyModel)
    assert result.name == "Test"
    assert result.value == 42
