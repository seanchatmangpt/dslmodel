import asyncio

from types import NoneType

from pydantic import BaseModel, Field
from pydantic_ai.dependencies import AgentDeps
from typing import Sequence, Type, Optional

from pydantic_ai import Agent, RunContext
from pydantic_ai.models import Model, KnownModelName
from pydantic_ai.result import ResultData

# DEFAULT_MODEL = "groq:llama-3.2-3b-preview"
# DEFAULT_MODEL = "groq:llama-3.1-70b-versatile"
# DEFAULT_MODEL = "groq:gemma2-9b-it"
DEFAULT_MODEL = "groq:llama-3.1-8b-instant"


# DEFAULT_MODEL = "groq:llama3-groq-8b-8192-tool-use-preview"

def get_agent(
        model: Model | KnownModelName | None = DEFAULT_MODEL,
        *,
        result_type: type[ResultData] = str,
        system_prompt: str | Sequence[str] = (),
        deps_type: type[AgentDeps] = NoneType,
        retries: int = 1,
        result_tool_name: str = 'final_result',
        result_tool_description: str | None = None,
        result_retries: int | None = None,
        defer_model_check: bool = False,
):
    return Agent(
        model=model,
        deps_type=deps_type,
        result_type=result_type,
        system_prompt=system_prompt,
        retries=retries,
        result_tool_name=result_tool_name,
        result_tool_description=result_tool_description,
        result_retries=result_retries,
        defer_model_check=defer_model_check

    )


async def instance(
        base_model: Type[BaseModel],
        prompt: str,
        *,
        agent: Optional[Agent] = None,
        model: str = DEFAULT_MODEL,
        result_type: Type[BaseModel] = None,
        system_prompt: str | Sequence[str] = (),
        deps_type: Optional[Type] = None,
        retries: int = 1,
        result_tool_name: str = 'final_result',
        result_tool_description: Optional[str] = None,
        result_retries: Optional[int] = None,
        defer_model_check: bool = False,
) -> BaseModel:
    """
    Creates an instance of a given Pydantic model using the output from an agent.
    If no agent is provided, a default one is created using the specified parameters.

    Args:
        base_model (Type[BaseModel]): The Pydantic BaseModel type to instantiate.
        prompt (str): The system prompt for the agent if one needs to be created.
        agent (Optional[Agent]): An existing Agent instance to use. If None, a new one is created.
        result_type (Type[BaseModel]): Result type for the Agent, defaults to the `model`.
        system_prompt (str | Sequence[str]): The system prompt or prompts for the agent.
        deps_type (Optional[Type]): The type of dependencies for the agent.
        retries (int): Number of retries for the agent.
        result_tool_name (str): Name of the tool that returns the result.
        result_tool_description (Optional[str]): Description of the result tool.
        result_retries (Optional[int]): Number of retries for the result tool.
        defer_model_check (bool): Whether to defer the model check.

    Returns:
        BaseModel: An instance of the specified model.
    """
    # Use the provided agent or create one with `get_agent`
    if agent is None:
        agent = get_agent(
            model=model,
            result_type=result_type or base_model,
            system_prompt=base_model.__doc__ or system_prompt,
            deps_type=deps_type,
            retries=retries,
            result_tool_name=result_tool_name,
            result_tool_description=result_tool_description,
            result_retries=result_retries,
            defer_model_check=defer_model_check,
        )

    # Run the agent and parse the result into the specified model
    result = await agent.run(prompt)
    return base_model.model_validate(result.data)


class InstanceMixin:
    @classmethod
    async def from_prompt(cls, prompt: str, **kwargs) -> BaseModel:
        return await instance(cls, prompt, **kwargs)


class AgentModel(BaseModel, InstanceMixin):
    """A Pydantic model that uses an agent to generate instances."""


import datetime
from functools import wraps


def elapsed_time(func):
    """
    A decorator to measure and print the elapsed time of a function in minutes:seconds format.

    Args:
        func (callable): The function to be wrapped.

    Returns:
        callable: The wrapped function.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = datetime.datetime.now(datetime.UTC)

        # Call the wrapped function
        result = await func(*args, **kwargs)

        end = datetime.datetime.now(datetime.UTC)
        elapsed = end - start
        minutes, seconds = divmod(elapsed.total_seconds(), 60)
        print(f"Time taken: {int(minutes)}:{seconds:.2f}")

        return result

    return wrapper


class HelloWorldModel(BaseModel, InstanceMixin):
    message: str = Field(..., title="The message to display from the user input.")


async def main():
    model = await HelloWorldModel.from_prompt("Hello World!")  # await instance(HelloWorldModel, "Hello, world!")
    print(model)

    # agent = get_agent()

    # result_sync = agent.run_sync('What is the capital of Italy?')
    # print(result_sync.data)
    # > Rome

    # result = await agent.run('What is the capital of France?')
    # print(result.data)
    # #> Paris
    #
    # async with agent.run_stream('What is the capital of the UK?') as response:
    #     print(await response.get_data())
    #     #> London
    #


if __name__ == "__main__":
    asyncio.run(main())
