"""
LLM Initialization Utilities for DSLModel

Provides convenient functions to initialize various language models
with DSPy for use in DSLModel components.
"""
import dspy
from typing import Optional, Dict, Any
from loguru import logger


def init_lm(
    model: str,
    temperature: float = 0.1,
    max_tokens: int = 2048,
    model_type: str = "chat",
    **kwargs
) -> dspy.LM:
    """
    Initialize a language model with DSPy.
    
    Args:
        model: Model identifier (e.g., "ollama/qwen3", "openai/gpt-4")
        temperature: Sampling temperature (0.0-1.0)
        max_tokens: Maximum tokens to generate
        model_type: "chat" or "text"
        **kwargs: Additional arguments passed to dspy.LM
        
    Returns:
        Configured DSPy language model
        
    Examples:
        >>> # Initialize Ollama Qwen3
        >>> lm = init_lm("ollama/qwen3")
        
        >>> # Initialize OpenAI GPT-4
        >>> lm = init_lm("openai/gpt-4", temperature=0.2)
        
        >>> # Initialize with custom parameters
        >>> lm = init_lm("ollama/phi4", max_tokens=4096, temperature=0.0)
    """
    try:
        lm = dspy.LM(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            model_type=model_type,
            **kwargs
        )
        
        # Set as default LM
        dspy.configure(lm=lm)
        
        # Test connection
        test_response = lm("Hello")
        
        logger.success(f"Initialized DSPy with {model}")
        logger.info(f"Temperature: {temperature}, Max tokens: {max_tokens}")
        logger.debug(f"Test response length: {len(str(test_response))} chars")
        
        return lm
        
    except Exception as e:
        logger.error(f"Failed to initialize {model}: {e}")
        raise


def init_ollama(
    model_name: str = "qwen3:latest",
    base_url: str = "http://localhost:11434",
    **kwargs
) -> dspy.LM:
    """
    Initialize Ollama model with DSPy.
    
    Args:
        model_name: Ollama model name (e.g., "qwen3:latest", "phi4:latest")
        base_url: Ollama server URL
        **kwargs: Additional arguments for init_lm
        
    Returns:
        Configured DSPy language model
        
    Examples:
        >>> # Use default Qwen3
        >>> lm = init_ollama()
        
        >>> # Use different model
        >>> lm = init_ollama("phi4:latest")
        
        >>> # Custom Ollama server
        >>> lm = init_ollama("qwen3:latest", base_url="http://192.168.1.100:11434")
    """
    model_path = f"ollama/{model_name}"
    
    # Add base_url to kwargs if specified and different from default
    if base_url != "http://localhost:11434":
        kwargs["base_url"] = base_url
        
    return init_lm(model_path, **kwargs)


def init_openai(
    model_name: str = "gpt-4o-mini",
    api_key: Optional[str] = None,
    **kwargs
) -> dspy.LM:
    """
    Initialize OpenAI model with DSPy.
    
    Args:
        model_name: OpenAI model name (e.g., "gpt-4o", "gpt-4o-mini")
        api_key: OpenAI API key (uses environment variable if not provided)
        **kwargs: Additional arguments for init_lm
        
    Returns:
        Configured DSPy language model
    """
    model_path = f"openai/{model_name}"
    
    if api_key:
        kwargs["api_key"] = api_key
        
    return init_lm(model_path, **kwargs)


def get_available_ollama_models() -> list[str]:
    """
    Get list of available Ollama models.
    
    Returns:
        List of available model names
    """
    import subprocess
    
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse ollama list output
        lines = result.stdout.strip().split("\n")[1:]  # Skip header
        models = []
        
        for line in lines:
            if line.strip():
                model_name = line.split()[0]  # First column is model name
                models.append(model_name)
                
        return models
        
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        logger.warning(f"Could not get Ollama models: {e}")
        return []


def test_model(lm: Optional[dspy.LM] = None, prompt: str = "Say hello briefly") -> str:
    """
    Test a language model with a simple prompt.
    
    Args:
        lm: Language model to test (uses current DSPy LM if None)
        prompt: Test prompt to send
        
    Returns:
        Model response
    """
    if lm is None:
        lm = dspy.settings.lm
        
    if lm is None:
        raise ValueError("No language model configured. Call init_lm() first.")
        
    try:
        response = lm(prompt)
        logger.success(f"Model test successful: {len(str(response))} chars")
        return str(response)
        
    except Exception as e:
        logger.error(f"Model test failed: {e}")
        raise


# Convenience function for the init_lm("ollama/qwen3") pattern
def init_qwen3(**kwargs) -> dspy.LM:
    """Initialize Qwen3 model (convenience function)."""
    return init_ollama("qwen3:latest", **kwargs)


def init_phi4(**kwargs) -> dspy.LM:
    """Initialize Phi4 model (convenience function).""" 
    return init_ollama("phi4:latest", **kwargs)


# Global initialization function
_current_lm = None

def current_lm() -> Optional[dspy.LM]:
    """Get the currently configured language model."""
    return dspy.settings.lm if hasattr(dspy.settings, 'lm') else None


def is_lm_initialized() -> bool:
    """Check if a language model is initialized."""
    return current_lm() is not None


if __name__ == "__main__":
    # Demo usage
    print("Available Ollama models:")
    for model in get_available_ollama_models():
        print(f"  - {model}")
    
    print("\nInitializing Qwen3...")
    lm = init_qwen3()
    
    print("Testing model...")
    response = test_model(prompt="What is 2+2? Answer briefly.")
    print(f"Response: {response}")