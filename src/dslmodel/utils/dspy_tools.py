from typing import Optional

import dspy

GPT_DEFAULT_MODEL = "gpt-4o-mini"


def init_lm(model: str = "openai/gpt-4o-mini",
            api_key: Optional[str] = None,
            api_base: Optional[str] = None,
            temperature: float = 0.0,
            max_tokens: int = 1000,
            cache: bool = True,
            model_type: Optional[str] = "text",
            stop: Optional[list] = None,
            experimental: bool = True) -> dspy.LM:
    """
    Initialize a language model using the new DSPy 2.5 setup.

    Args:
        model (str): Model name, with support for openai/ prefixed endpoints (default: 'openai/gpt-4o-mini').
        model_type (Optional[str]): Specify the model type, such as 'text' for text-based predictions (default: None).
        api_key (Optional[str]): Optional API key for authentication, if required.
        api_base (Optional[str]): Optional API base URL for specific LMs (e.g., localhost setups).
        temperature (float): Temperature for controlling randomness in the model's predictions (default: 0.7).
        max_tokens (int): Maximum number of tokens to allow for a single prediction (default: 1000).
        cache (bool): Whether to cache results from the LM (default: False).
        model_type (Optional[str]): Specify the model type, such as 'text' for text-based predictions (default: None).
        stop (Optional[list]): Tokens or strings to stop generating at (default: None).
        adapter (Optional[dspy.ChatAdapter]): DSPy Adapter to manage input/output formatting (default: None).
        experimental (bool): Enable experimental DSPy settings for the LM (default: True).

    Returns:
        dspy.LM: Configured LM object.
    """
    # Initialize the LM with flexible configuration options
    if model == "openai/gpt-4o-mini":
        lm = dspy.LM('openai/gpt-4o-mini')
        dspy.settings.configure(lm=lm, experimental=experimental)
        return lm

    lm = dspy.LM(model=model)

    # Configure the LM with DSPy settings
    dspy.settings.configure(lm=lm, adapter=None, experimental=experimental)

    return lm


def init_instant():
    """Initialize the instant version of the model."""
    return init_lm("groq/llama-3.1-8b-instant", model_type="chat", max_tokens=8000)


def init_versatile():
    """Initialize the versatile version of the model."""
    return init_lm("groq/llama-3.1-70b-versatile", model_type="chat", max_tokens=8000)


def init_text():
    """Initialize the text preview version of the model."""
    return init_lm("groq/llama-3.2-90b-text-preview", model_type="chat", max_tokens=8000)
