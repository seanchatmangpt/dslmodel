from typing import Any, Type, TypeVar

from pydantic import BaseModel
from pydantic_ai import Agent

from dslmodel.utils.pydantic_ai_tools import instance, run_agent

T = TypeVar('T', bound=BaseModel)

class InstanceMixin:
    """Mixin for classes that need to create instances of Pydantic models using AI."""
    
    async def create_instance(self, model: Type[T], prompt: str, **kwargs: Any) -> T:
        """Create an instance of the given model using AI.
        
        Args:
            model: The Pydantic model class to create an instance of
            prompt: The prompt to send to the AI
            **kwargs: Additional arguments to pass to the agent
            
        Returns:
            An instance of the given model
        """
        agent = await instance(model)
        return await run_agent(agent, prompt, **kwargs)
