# tests/test_dspy_tools.py

import pytest
from unittest.mock import patch, MagicMock
from dslmodel.utils.dspy_tools import (
    init_lm,
    init_instant,
    init_versatile,
    init_text,
)


# Fixtures for mocking
@pytest.fixture
def mock_dspy_LM():
    """
    Fixture to mock the `dspy.LM` class.
    """
    with patch("dslmodel.utils.dspy_tools.dspy.LM") as mock_LM:
        yield mock_LM


@pytest.fixture
def mock_dspy_settings_configure():
    """
    Fixture to mock the `dspy.settings.configure` method.
    """
    with patch("dslmodel.utils.dspy_tools.dspy.settings.configure") as mock_configure:
        yield mock_configure


@pytest.fixture
def mock_dspy_ChatAdapter():
    """
    Fixture to mock the `dspy.ChatAdapter` class.
    """
    with patch("dslmodel.utils.dspy_tools.dspy.ChatAdapter") as mock_Adapter:
        yield mock_Adapter


# Tests for init_lm
def test_init_lm_default(mock_dspy_LM, mock_dspy_settings_configure):
    """
    Test initializing LM with default parameters.
    """
    lm_instance = MagicMock()
    mock_dspy_LM.return_value = lm_instance

    lm = init_lm()

    # Check that dspy.LM was called with default configuration
    mock_dspy_LM.assert_called_once_with(
        model="openai/gpt-4o-mini",
        temperature=0.0,
        max_tokens=1000,
        cache=True,
        model_type="chat",
    )

    # Check that dspy.settings.configure was called correctly
    mock_dspy_settings_configure.assert_called_once_with(
        lm=lm_instance, adapter=None, experimental=True
    )

    # Verify the returned LM is the instance created
    assert lm == lm_instance


def test_init_lm_with_kwargs(mock_dspy_LM, mock_dspy_settings_configure):
    """
    Test initializing LM with custom keyword arguments.
    """
    lm_instance = MagicMock()
    mock_dspy_LM.return_value = lm_instance

    lm = init_lm(
        model="openai/custom-model",
        experimental=False,
        api_key="test_key",
        temperature=0.5,
        max_tokens=500,
        cache=False,
        model_type="text",
        stop=["\n"],
    )

    # Check that dspy.LM was called with updated configuration
    mock_dspy_LM.assert_called_once_with(
        model="openai/custom-model",
        temperature=0.5,
        max_tokens=500,
        cache=False,
        model_type="text",
        api_key="test_key",
        stop=["\n"],
    )

    # Check that dspy.settings.configure was called correctly
    mock_dspy_settings_configure.assert_called_once_with(
        lm=lm_instance, adapter=None, experimental=False
    )

    # Verify the returned LM is the instance created
    assert lm == lm_instance


def test_init_lm_with_adapter(mock_dspy_LM, mock_dspy_settings_configure, mock_dspy_ChatAdapter):
    """
    Test initializing LM with a ChatAdapter.
    """
    adapter_instance = MagicMock()
    lm_instance = MagicMock()
    mock_dspy_LM.return_value = lm_instance

    lm = init_lm(adapter=adapter_instance, experimental=False)

    # Check that dspy.LM was called with default configuration
    mock_dspy_LM.assert_called_once_with(
        model="openai/gpt-4o-mini",
        temperature=0.0,
        max_tokens=1000,
        cache=True,
        model_type="chat",
    )

    # Check that dspy.settings.configure was called correctly with adapter
    mock_dspy_settings_configure.assert_called_once_with(
        lm=lm_instance, adapter=adapter_instance, experimental=False
    )

    # Verify the returned LM is the instance created
    assert lm == lm_instance


def test_init_lm_removes_none_values(mock_dspy_LM, mock_dspy_settings_configure):
    """
    Test that initializing LM removes parameters with None values.
    """
    lm_instance = MagicMock()
    mock_dspy_LM.return_value = lm_instance

    # Pass some kwargs with None values
    lm = init_lm(
        model=None,
        temperature=0.3,
        max_tokens=None,
        cache=False,
        extra_param=None,
    )

    # Expected configuration after removing None values
    mock_dspy_LM.assert_called_once_with(
        temperature=0.3,
        cache=False,
        model_type="chat",
    )

    # Check that dspy.settings.configure was called correctly
    mock_dspy_settings_configure.assert_called_once_with(
        lm=lm_instance, adapter=None, experimental=True
    )

    # Verify the returned LM is the instance created
    assert lm == lm_instance


# Tests for preset initialization functions
def test_init_instant(mock_dspy_LM, mock_dspy_settings_configure):
    """
    Test the `init_instant` preset function.
    """
    lm_instance = MagicMock()
    mock_dspy_LM.return_value = lm_instance

    lm = init_instant()

    mock_dspy_LM.assert_called_once_with(
        model="groq/llama-3.1-8b-instant",
        model_type="chat",
        max_tokens=8000,
        temperature=0.0,
        cache=True,
    )

    mock_dspy_settings_configure.assert_called_once_with(
        lm=lm_instance, adapter=None, experimental=True
    )

    assert lm == lm_instance


def test_init_versatile(mock_dspy_LM, mock_dspy_settings_configure):
    """
    Test the `init_versatile` preset function.
    """
    lm_instance = MagicMock()
    mock_dspy_LM.return_value = lm_instance

    lm = init_versatile()

    mock_dspy_LM.assert_called_once_with(
        model="groq/llama-3.1-70b-versatile",
        model_type="chat",
        max_tokens=8000,
        temperature=0.0,
        cache=True,
    )

    mock_dspy_settings_configure.assert_called_once_with(
        lm=lm_instance, adapter=None, experimental=True
    )

    assert lm == lm_instance


def test_init_text(mock_dspy_LM, mock_dspy_settings_configure):
    """
    Test the `init_text` preset function.
    """
    lm_instance = MagicMock()
    mock_dspy_LM.return_value = lm_instance

    lm = init_text()

    mock_dspy_LM.assert_called_once_with(
        model="groq/llama-3.2-90b-text-preview",
        model_type="chat",
        max_tokens=8000,
        temperature=0.0,
        cache=True,
    )

    mock_dspy_settings_configure.assert_called_once_with(
        lm=lm_instance, adapter=None, experimental=True
    )

    assert lm == lm_instance


# Parameterized tests for different configurations
@pytest.mark.parametrize(
    "preset_func, model, temperature, max_tokens",
    [
        (init_instant, "groq/llama-3.1-8b-instant", 0.0, 8000),
        (init_versatile, "groq/llama-3.1-70b-versatile", 0.0, 8000),
        (init_text, "groq/llama-3.2-90b-text-preview", 0.0, 8000),
    ],
)
def test_presets(
    mock_dspy_LM,
    mock_dspy_settings_configure,
    preset_func,
    model,
    temperature,
    max_tokens,
):
    """
    Parameterized test for preset initialization functions.

    :param preset_func: The preset function to test.
    :type preset_func: function
    :param model: Expected model name.
    :type model: str
    :param temperature: Expected temperature value.
    :type temperature: float
    :param max_tokens: Expected maximum tokens.
    :type max_tokens: int
    """
    lm_instance = MagicMock()
    mock_dspy_LM.return_value = lm_instance

    lm = preset_func()

    mock_dspy_LM.assert_called_once_with(
        model=model,
        model_type="chat",
        max_tokens=max_tokens,
        temperature=temperature,
        cache=True,
    )

    mock_dspy_settings_configure.assert_called_once_with(
        lm=lm_instance, adapter=None, experimental=True
    )

    assert lm == lm_instance
