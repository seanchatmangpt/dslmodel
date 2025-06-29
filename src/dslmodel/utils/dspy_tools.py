import dspy
import os
from typing import Optional


def init_lm(
        model: Optional[str] = None,
        experimental: bool = True,
        adapter: dspy.ChatAdapter | None = None,
        validate_ollama: bool = True,
        **kwargs
) -> dspy.LM:
    """
    Initialize a language model using the new DSPy 2.5 setup.
    Reads configuration from environment variables.

    :param model: Model name, supporting `openai/` prefixed endpoints.
                  Defaults to SWARMSH_LM env var or 'ollama/qwen3'.
    :type model: str, optional
    :param experimental: Enable experimental DSPy settings for the LM.
                         Defaults to `True`.
    :type experimental: bool, optional
    :param adapter: DSPy Adapter to manage input/output formatting.
                    Defaults to `None`.
    :type adapter: dspy.ChatAdapter or None, optional
    :param validate_ollama: Whether to validate Ollama models before initialization.
                           Defaults to `True`.
    :type validate_ollama: bool, optional
    :param kwargs: Additional keyword arguments to pass to `dspy.LM`.
                   Supported kwargs include:
                   - `api_key` (str): API key for authentication, if required.
                   - `api_base` (str): API base URL for specific LMs
                                        (e.g., localhost setups).
                   - `temperature` (float): Temperature for controlling randomness.
                                            Defaults to `0.0`.
                   - `max_tokens` (int): Maximum number of tokens for a single prediction.
                                           Defaults to `1000`.
                   - `cache` (bool): Whether to cache results from the LM.
                                     Defaults to `True`.
                   - `model_type` (str): Specify the model type, such as `'text'`
                                         for text-based predictions.
                   - `stop` (list): Tokens or strings to stop generating at.

    :return: Configured LM object.
    :rtype: dspy.LM
    """
    # Read configuration from environment variables
    if model is None:
        model = os.getenv('SWARMSH_LM', 'ollama/qwen3')
    
    # Override kwargs with environment defaults if not provided
    env_config = {
        'temperature': float(os.getenv('SWARMSH_LM_TEMPERATURE', '0.0')),
        'max_tokens': int(os.getenv('SWARMSH_LM_MAX_TOKENS', '1000'))
    }
    
    # Update with env values only if not explicitly provided
    for key, value in env_config.items():
        if key not in kwargs:
            kwargs[key] = value
    
    # Validate Ollama models if enabled and model starts with "ollama/"
    if validate_ollama and model.startswith("ollama/"):
        try:
            from .ollama_validator import safe_init_ollama
            success, validated_lm, message = safe_init_ollama(model, experimental=experimental, adapter=adapter, **kwargs)
            if success:
                return validated_lm
            else:
                # Fallback to standard initialization with warning
                import warnings
                warnings.warn(f"Ollama validation failed ({message}), proceeding with standard initialization")
        except ImportError:
            # Validator not available, proceed normally
            pass

    # Default configuration with 'model' parameter
    default_config = {
        "model": model,  # Use the 'model' parameter here
        "api_key": None,
        "api_base": None,
        "temperature": 0.0,
        "max_tokens": 1000,
        "cache": True,
        "model_type": "chat",
        "stop": None,
    }

    # Update default config with user-provided kwargs
    lm_config = {**default_config, **kwargs}

    # Remove None values to use default settings from dspy.LM
    lm_config = {k: v for k, v in lm_config.items() if v is not None}
    lm = dspy.LM(**lm_config)

    # Configure the LM with DSPy settings
    dspy.settings.configure(lm=lm, adapter=adapter, experimental=experimental)

    return lm


# Presets for different use cases


def init_instant(model_type="chat", max_tokens=8000, **kwargs):
    """
    Initialize the instant version of the model for quick responses.

    :param **kwargs: Additional keyword arguments to pass to `init_lm`.
    :return: Configured LM object for instant responses.
    :rtype: dspy.LM
    """
    return init_lm(
        "groq/llama-3.1-8b-instant", model_type=model_type, max_tokens=max_tokens, **kwargs
    )


def init_versatile(**kwargs):
    """
    Initialize the versatile version of the model for general-purpose tasks.

    :param **kwargs: Additional keyword arguments to pass to `init_lm`.
    :return: Configured LM object for versatile tasks.
    :rtype: dspy.LM
    """
    return init_lm(
        "groq/llama-3.3-70b-versatile", model_type="chat", max_tokens=8000, **kwargs
    )


def init_text(model_type="chat", max_tokens=8000, **kwargs):
    """
    Initialize the text preview version of the model for advanced text processing.

    :param **kwargs: Additional keyword arguments to pass to `init_lm`.
    :return: Configured LM object for text processing.
    :rtype: dspy.LM
    """
    return init_lm(
        "groq/llama3-groq-70b-8192-tool-use-preview", model_type=model_type,
        max_tokens=max_tokens, **kwargs
    )

# Presets for different use cases

# def init_o1(**kwargs):
#     """Initialize a reasoning model designed to solve hard problems across domains."""
#     return init_lm("openai/gpt-o1-preview", temperature=0.2, max_tokens=12000, model_type="chat", **kwargs)

# def init_o1_mini(**kwargs):
#     """Initialize a model optimized for complex tasks, coding and problem-solving."""
#     return init_lm("openai/gpt-o1-mini", temperature=0.2, max_tokens=8000, model_type="chat", **kwargs)


# def init_creative(**kwargs):
#     """Initialize a model optimized for creative writing tasks."""
#     return init_lm("openai/gpt-4o-mini", temperature=0.9, max_tokens=2000, model_type="chat", **kwargs)

# def init_analytical(**kwargs):
#     """Initialize a model optimized for analytical tasks and problem-solving."""
#     return init_lm("openai/gpt-4o", temperature=0.2, max_tokens=4000, model_type="chat", **kwargs)

# def init_coding(**kwargs):
#     """Initialize a model optimized for code generation and analysis."""
#     return init_lm("openai/gpt-4o", temperature=0.3, max_tokens=8000, model_type="chat", stop=["\n\n"], **kwargs)

# def init_summarization(**kwargs):
#     """Initialize a model optimized for text summarization tasks."""
#     return init_lm("openai/gpt-4-turbo", temperature=0.5, max_tokens=150, model_type="chat", **kwargs)

# def init_qa(**kwargs):
#     """Initialize a model optimized for question-answering tasks."""
#     return init_lm("openai/gpt-4o-mini", temperature=0.4, max_tokens=1000, model_type="chat", **kwargs)
