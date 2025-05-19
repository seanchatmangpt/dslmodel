import asyncio
from datetime import datetime, UTC
from functools import wraps
from typing import Any, Type, TypeVar

from pydantic import BaseModel, Field
from pydantic_ai import Agent

DEFAULT_MODEL = "groq:llama-3.2-90b-text-preview"

T = TypeVar('T', bound=BaseModel)

async def instance(model: Type[T], model_name: str = DEFAULT_MODEL) -> Agent[T]:
    """Create an agent that returns an instance of the given model.
    
    Args:
        model: The Pydantic model class to use for the output type
        model_name: The name of the model to use (default: DEFAULT_MODEL)
        
    Returns:
        An Agent configured to return an instance of the given model
    """
    return Agent(
        model_name,
        output_type=model,
        retries=2,
    )

async def run_agent(agent: Agent[T], prompt: str, **kwargs: Any) -> T:
    """Run an agent with the given prompt and return the result.
    
    Args:
        agent: The agent to run
        prompt: The prompt to send to the agent
        **kwargs: Additional arguments to pass to the agent's run method
        
    Returns:
        The result of running the agent
    """
    result = await agent.run(prompt, **kwargs)
    return result.output

class InstanceMixin:
    """Mixin for classes that need to create instances of Pydantic models using AI."""
    
    @classmethod
    async def from_prompt(cls, prompt: str, **kwargs) -> BaseModel:
        """Create an instance of this model using AI.
        
        Args:
            prompt: The prompt to send to the AI
            **kwargs: Additional arguments to pass to the agent
            
        Returns:
            An instance of this model
        """
        agent = await instance(cls)
        return await run_agent(agent, prompt, **kwargs)

class AgentModel(BaseModel, InstanceMixin):
    """A Pydantic model that uses an agent to generate instances."""

def elapsed_time(func):
    """A decorator to measure and print the elapsed time of a function in minutes:seconds format.
    
    Args:
        func (callable): The function to be wrapped.
        
    Returns:
        callable: The wrapped function.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = datetime.now(UTC)
        result = await func(*args, **kwargs)
        end = datetime.now(UTC)
        elapsed = end - start
        minutes, seconds = divmod(elapsed.total_seconds(), 60)
        print(f"Time taken: {int(minutes)}:{seconds:.2f}")
        return result
    return wrapper

class HelloWorldModel(BaseModel, InstanceMixin):
    """Example model that demonstrates the InstanceMixin functionality."""
    message: str = Field(..., title="The message to display from the user input.")

async def main():
    """Example usage of the HelloWorldModel."""
    model = await HelloWorldModel.from_prompt("Hello World!")
    print(model)

if __name__ == "__main__":
    asyncio.run(main())
