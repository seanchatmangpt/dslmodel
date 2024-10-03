
import os
from contextlib import contextmanager, asynccontextmanager
from typing import Any, Optional, TypeVar, Union, Type, Dict

import aiofiles
import yaml
import json
from pydantic import BaseModel, ValidationError, ConfigDict

from dslmodel.dspy_modules.file_name_module import file_name_call
from dslmodel.dspy_modules.gen_pydantic_instance import gen_instance
from dslmodel.template import render_native, render

T = TypeVar("T", bound="DSLModel")


class DSLModel(BaseModel):
    """
    A base model class that provides serialization and deserialization capabilities
    between Pydantic models and YAML and JSON formats. It facilitates saving model instances
    to files and loading data from files into model objects.
    Includes support for asynchronous file operations, versioning, enhanced context managers,
    automatic documentation generation, and enhanced error handling.
    """

    def __init__(self, **data):
        # Render any default template values using Jinja2 before instantiation
        data = self.render_defaults(data)
        super().__init__(**data)

    @classmethod
    def render_defaults(cls, data: dict) -> dict:
        """
        Renders default values that are defined as Jinja2 templates.
        """
        for field_name, field_value in cls.model_fields.items():
            if field_name in data:
                continue

            if "{{" in field_value.default:
                # Render the template if it contains a Jinja2 expression
                rendered_value = render_native(field_value.default)
                # Only set the value if not already provided by user input
                if field_name not in data:
                    data[field_name] = rendered_value

        return data

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        populate_by_name=True
    )

    def generate_filename(self, extension: str = "yaml", add_timestamp: bool = False) -> str:
        """Generates a safe filename based on the model's content."""
        content = self.to_yaml()

        # Generate the filename
        filename = file_name_call(file_content=content, extension=extension)
        return filename

    def save(self, file_path: Optional[str] = None, file_format: str = "yaml", add_timestamp: bool = False) -> str:
        """
        Saves the model to a file in the specified format. Automatically generates a filename if not provided.

        :param file_path: The path to the file. If None, generates a filename.
        :param file_format: The format to save the file in ('yaml' or 'json').
        :param add_timestamp: Whether to append a timestamp to the filename.

        :return: The path to the saved file.
        """
        if file_path is None:
            file_path = self.generate_filename(extension=file_format, add_timestamp=add_timestamp)

        if file_format == "yaml":
            self.to_yaml(file_path)
        elif file_format == "json":
            self.to_json(file_path)
        else:
            raise ValueError("Unsupported file format. Use 'yaml' or 'json'.")

        return file_path


    def to_yaml(self, file_path: Optional[str] = None) -> str:
        """
        Serializes the Pydantic model instance into a YAML string and optionally writes it to a file.

        :param file_path: The file path to write the YAML content to.
                          If None, only the YAML string is returned.
        :return: The YAML representation of the model.
        :raises IOError: If serialization to YAML fails.
        """
        try:
            yaml_content = yaml.dump(
                self.model_dump(),
                default_flow_style=False,
                width=1000
            )
            if file_path:
                with open(file_path, "w") as yaml_file:
                    yaml_file.write(yaml_content)
            return yaml_content
        except Exception as e:
            raise IOError(f"Failed to serialize model to YAML: {e}")

    @classmethod
    def from_yaml(cls: Type[T], file_path: str) -> T:
        """
        Reads YAML content from a file and creates an instance of the Pydantic model.

        :param file_path: The path to the YAML file.
        :return: An instance of the Pydantic model populated with data from the YAML file.
        :raises FileNotFoundError: If the YAML file is not found.
        :raises ValueError: If there is a parsing or validation error.
        """
        try:
            with open(file_path) as yaml_file:
                data = yaml.safe_load(yaml_file)
            instance = cls.model_validate(data)
            return instance
        except FileNotFoundError:
            raise FileNotFoundError(f"YAML file not found at {file_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML file at {file_path}: {e}")
        except ValidationError as ve:
            raise ValueError(f"Validation error while creating {cls.__name__} instance: {ve}")

    def to_json(self, file_path: Optional[str] = None, **kwargs) -> str:
        """
        Serializes the Pydantic model instance into a JSON string and optionally writes it to a file.

        :param file_path: The file path to write the JSON content to.
                          If None, only the JSON string is returned.
        :param kwargs: Additional keyword arguments to pass to json.dumps.
        :return: The JSON representation of the model.
        :raises IOError: If serialization to JSON fails.
        """
        try:
            json_content = self.model_dump_json(**kwargs)
            if file_path:
                with open(file_path, "w") as json_file:
                    json_file.write(json_content)
            return json_content
        except Exception as e:
            raise IOError(f"Failed to serialize model to JSON: {e}")

    @classmethod
    def from_json(cls: Type[T], file_path: str) -> T:
        """
        Reads JSON content from a file and creates an instance of the Pydantic model.

        :param file_path: The path to the JSON file.
        :return: An instance of the Pydantic model populated with data from the JSON file.
        :raises FileNotFoundError: If the JSON file is not found.
        :raises ValueError: If there is a parsing or validation error.
        """
        try:
            with open(file_path, "r") as json_file:
                data = json.load(json_file)
            instance = cls.model_validate(data)
            return instance
        except FileNotFoundError:
            raise FileNotFoundError(f"JSON file not found at {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Error parsing JSON file at {file_path}: {e}")
        except ValidationError as ve:
            raise ValueError(f"Validation error while creating {cls.__name__} instance: {ve}")

    @classmethod
    def from_prompt(cls: Type[T], prompt: str, verbose=False, **kwargs) -> T:
        """
        Creates an instance of the Pydantic model from a user prompt.

        :param prompt: The user prompt.
        :param verbose: Whether to print verbose output and debug information.
        :return: An instance of the Pydantic model.
        """
        prompt = render(prompt, **kwargs)
        return gen_instance(cls, prompt, verbose)
