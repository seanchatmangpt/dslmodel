import json
from abc import abstractmethod, ABC

import toml
import yaml
from typing import TypeVar, Union, Optional
from pathlib import Path
from pydantic import ValidationError
import aiofiles

T = TypeVar("T", bound="DSLModel")


class ToFromMixin(ABC):
    """
    A mixin class that provides async serialization (to_*) and deserialization (from_*)
    functionalities for YAML, JSON, and TOML formats, with the ability to optionally
    read from and write to disk.
    """

    @abstractmethod
    def model_dump(self) -> dict:
        """
        Must be implemented: Serializes the model instance to a dictionary.
        """
        pass

    @abstractmethod
    def model_validate(cls: type[T], data: dict) -> T:
        """
        Must be implemented: Validates and creates an instance from a dictionary.
        """
        pass

    @abstractmethod
    def model_dump_json(self, indent: int = 4) -> str:
        """
        Must be implemented: Serializes the model instance to a JSON string.
        """
        pass

    @classmethod
    async def from_dict(cls: type[T], data: dict) -> T:
        """
        Creates an instance of the model from a dictionary.
        """
        try:
            instance = cls.model_validate(data)
            return instance
        except ValidationError as ve:
            raise ValueError(f"Validation error while creating {cls.__name__} instance: {ve}")

    @classmethod
    async def from_yaml(
            cls: type[T], content: str = "", file_path: Optional[Union[str, Path]] = None
    ) -> T:
        """
        Parses YAML content from a string or file path and creates an instance of the model.
        """
        if file_path:
            async with aiofiles.open(file_path, 'r') as f:
                content = await f.read()
        if not content:
            raise ValueError("Either content or file_path must be provided")
        try:
            data = yaml.safe_load(content)
            return await cls.from_dict(data)
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML content: {e}")

    @classmethod
    async def from_json(
            cls: type[T], content: str = "", file_path: Optional[Union[str, Path]] = None
    ) -> T:
        """
        Parses JSON content from a string or file path and creates an instance of the model.
        """
        if file_path:
            async with aiofiles.open(file_path, 'r') as f:
                content = await f.read()
        if not content:
            raise ValueError("Either content or file_path must be provided")
        try:
            data = json.loads(content)
            return await cls.from_dict(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error parsing JSON content: {e}")

    @classmethod
    async def from_toml(
            cls: type[T], content: str = "", file_path: Optional[Union[str, Path]] = None
    ) -> T:
        """
        Parses TOML content from a string or file path and creates an instance of the model.
        """
        if file_path:
            async with aiofiles.open(file_path, 'r') as f:
                content = await f.read()
        if not content:
            raise ValueError("Either content or file_path must be provided")
        try:
            data = toml.loads(content)
            return await cls.from_dict(data)
        except Exception as e:
            raise ValueError(f"Error parsing TOML content: {e}")

    async def to_yaml(self, file_path: Optional[Union[str, Path]] = None) -> str:
        """
        Serializes the model instance into a YAML string. Optionally, writes to a file if file_path is provided.
        """
        try:
            yaml_content = yaml.dump(self.model_dump(), default_flow_style=False, width=1000)
            if file_path:
                async with aiofiles.open(file_path, 'w') as f:
                    await f.write(yaml_content)
            return yaml_content
        except Exception as e:
            raise OSError(f"Failed to serialize model to YAML: {e}")

    async def to_json(self, file_path: Optional[Union[str, Path]] = None, indent: int = 2) -> str:
        """
        Serializes the model instance into a JSON string. Optionally, writes to a file if file_path is provided.
        """
        try:
            json_content = self.model_dump_json(indent=indent)
            if file_path:
                async with aiofiles.open(file_path, 'w') as f:
                    await f.write(json_content)
            return json_content
        except Exception as e:
            raise OSError(f"Failed to serialize model to JSON: {e}")

    async def to_toml(self, file_path: Optional[Union[str, Path]] = None) -> str:
        """
        Serializes the model instance into a TOML string. Optionally, writes to a file if file_path is provided.
        """
        try:
            toml_content = toml.dumps(self.model_dump())
            if file_path:
                async with aiofiles.open(file_path, 'w') as f:
                    await f.write(toml_content)
            return toml_content
        except Exception as e:
            raise OSError(f"Failed to serialize model to TOML: {e}")
