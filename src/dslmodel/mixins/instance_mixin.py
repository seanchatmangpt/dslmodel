from pydantic import BaseModel

from dslmodel.utils.pydantic_ai_tools import instance


class InstanceMixin:
    @classmethod
    async def from_prompt(cls, prompt: str, **kwargs) -> BaseModel:
        return await instance(cls, prompt, **kwargs)
