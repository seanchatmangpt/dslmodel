import dspy

GPT_DEFAULT_MODEL = "gpt-4o-mini"

def init_lm(
    model: str = f"openai/{GPT_DEFAULT_MODEL}",
    experimental: bool = True,
    adapter: dspy.ChatAdapter | None = None,
    **kwargs) -> dspy.LM:
    """
    Initialize a language model using the new DSPy 2.5 setup.

    Args:
        model (str): Model name, with support for openai/ prefixed endpoints (default: 'openai/gpt-4o-mini').
        experimental (bool): Enable experimental DSPy settings for the LM (default: True).
        adapter (dspy.ChatAdapter | None): DSPy Adapter to manage input/output formatting (default: None).
        **kwargs: Additional keyword arguments to pass to dspy.LM. These may include:
            - api_key (str): API key for authentication, if required.
            - api_base (str): API base URL for specific LMs (e.g., localhost setups).
            - temperature (float): Temperature for controlling randomness (default: 0.7).
            - max_tokens (int): Maximum number of tokens for a single prediction (default: 1000).
            - cache (bool): Whether to cache results from the LM (default: False).
            - model_type (str): Specify the model type, such as 'text' for text-based predictions.
            - stop (list): Tokens or strings to stop generating at.

    Returns
    -------
        dspy.LM: Configured LM object.
    """
    # Default configuration
    default_config = {
        "model": "openai/gpt-4o-mini",
        "api_key": None,
        "api_base": None,
        "temperature": 0.0,
        "max_tokens": 1000,
        "cache": True,
        "model_type": "chat",
        "stop": None,
        # "experimental": True,
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

# def init_o1(**kwargs):
#     """Initialize a reasoning model designed to solve hard problems across domains."""
#     return init_lm("openai/gpt-o1-preview", temperature=0.2, max_tokens=12000, model_type="chat", **kwargs)

# def init_o1_mini(**kwargs):
#     """Initialize a model optimized for complex tasks, coding and problem-solving."""
#     return init_lm("openai/gpt-o1-mini", temperature=0.2, max_tokens=8000, model_type="chat", **kwargs)



def init_instant(**kwargs):
    """Initialize the instant version of the model for quick responses."""
    return init_lm("groq/llama-3.1-8b-instant", model_type="chat", max_tokens=8000, **kwargs)

def init_versatile(**kwargs):
    """Initialize the versatile version of the model for general-purpose tasks."""
    return init_lm("groq/llama-3.1-70b-versatile", model_type="chat", max_tokens=8000, **kwargs)

def init_text(**kwargs):
    """Initialize the text preview version of the model for advanced text processing."""
    return init_lm("groq/llama-3.2-90b-text-preview", model_type="chat", max_tokens=8000, **kwargs)

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
