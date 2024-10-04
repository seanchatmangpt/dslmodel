from typing import Type, TypeVar
import yaml
import json
import toml
from pydantic import ValidationError

T = TypeVar("T", bound="DSLModel")


class ToFromDSLMixin:
    """
    A mixin class that provides serialization (to_*) and deserialization (from_*) functionalities
    for YAML, JSON, and TOML formats.
    """

    @classmethod
    def from_dict(cls: Type[T], data: dict) -> T:
        """
        Creates an instance of the model from a dictionary.

        :param data: A dictionary containing the data to populate the model.
        :return: An instance of the model populated with the given data.
        :raises ValidationError: If the data does not pass validation.
        """
        try:
            instance = cls.model_validate(data)
            return instance
        except ValidationError as ve:
            raise ValueError(f"Validation error while creating {cls.__name__} instance: {ve}")

    @classmethod
    def from_yaml(cls: Type[T], content: str) -> T:
        """
        Parses YAML content from a string and creates an instance of the model.

        :param content: A string containing the YAML data.
        :return: An instance of the model populated with data from the YAML string.
        :raises ValueError: If there is a parsing or validation error.
        """
        try:
            data = yaml.safe_load(content)
            return cls.from_dict(data)
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML content: {e}")

    @classmethod
    def from_json(cls: Type[T], content: str) -> T:
        """
        Parses JSON content from a string and creates an instance of the model.

        :param content: A string containing the JSON data.
        :return: An instance of the model populated with data from the JSON string.
        :raises ValueError: If there is a parsing or validation error.
        """
        try:
            data = json.loads(content)
            return cls.from_dict(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error parsing JSON content: {e}")

    @classmethod
    def from_toml(cls: Type[T], content: str) -> T:
        """
        Parses TOML content from a string and creates an instance of the model.

        :param content: A string containing the TOML data.
        :return: An instance of the model populated with data from the TOML string.
        :raises ValueError: If there is a parsing or validation error.
        """
        try:
            data = toml.loads(content)
            return cls.from_dict(data)
        except toml.TomlDecodeError as e:
            raise ValueError(f"Error parsing TOML content: {e}")

    def to_yaml(self) -> str:
        """
        Serializes the model instance into a YAML string.

        :return: The YAML representation of the model.
        :raises IOError: If serialization to YAML fails.
        """
        try:
            return yaml.dump(self.model_dump(), default_flow_style=False, width=1000)
        except Exception as e:
            raise IOError(f"Failed to serialize model to YAML: {e}")

    def to_json(self) -> str:
        """
        Serializes the model instance into a JSON string.

        :return: The JSON representation of the model.
        :raises IOError: If serialization to JSON fails.
        """
        try:
            return self.model_dump_json()
        except Exception as e:
            raise IOError(f"Failed to serialize model to JSON: {e}")

    def to_toml(self) -> str:
        """
        Serializes the model instance into a TOML string.

        :return: The TOML representation of the model.
        :raises IOError: If serialization to TOML fails.
        """
        try:
            return toml.dumps(self.model_dump())
        except Exception as e:
            raise IOError(f"Failed to serialize model to TOML: {e}")
