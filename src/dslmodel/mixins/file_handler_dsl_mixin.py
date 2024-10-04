from typing import Type, TypeVar, Optional

T = TypeVar("T", bound="DSLModel")


class FileHandlerDSLMixin:
    """
    A mixin class that provides file handling functionalities for saving and loading
    models to and from YAML, JSON, and TOML formats.
    """

    def generate_filename(self, extension: str = "yaml", add_timestamp: bool = False) -> str:
        """
        Generates a safe filename based on the model's content.

        :param extension: The file extension (e.g., 'yaml', 'json', 'toml').
        :param add_timestamp: Whether to append a timestamp to the filename.
        :return: The generated filename.
        """
        from dslmodel.dspy_modules.file_name_module import file_name_call

        content = self.to_yaml()  # Use the YAML representation to generate the filename
        filename = file_name_call(file_content=content, extension=extension)
        return filename

    def save(self, file_path: Optional[str] = None, file_format: str = "yaml", add_timestamp: bool = False) -> str:
        """
        Saves the model to a file in the specified format. Automatically generates a filename if not provided.

        :param file_path: The path to the file. If None, generates a filename.
        :param file_format: The format to save the file in ('yaml', 'json', 'toml').
        :param add_timestamp: Whether to append a timestamp to the filename.
        :return: The path to the saved file.
        """
        if file_path is None:
            file_path = self.generate_filename(extension=file_format, add_timestamp=add_timestamp)

        if file_format == "yaml":
            content = self.to_yaml()
        elif file_format == "json":
            content = self.to_json()
        elif file_format == "toml":
            content = self.to_toml()
        else:
            raise ValueError("Unsupported file format. Use 'yaml', 'json', or 'toml'.")

        with open(file_path, "w") as file:
            file.write(content)

        return file_path

    @classmethod
    def load(cls: Type[T], file_path: str, file_format: str = "yaml") -> T:
        """
        Loads a model from a file in the specified format.

        :param file_path: The path to the file.
        :param file_format: The format of the file ('yaml', 'json', 'toml').
        :return: An instance of the model populated with data from the file.
        """
        with open(file_path, "r") as file:
            content = file.read()

        if file_format == "yaml":
            return cls.from_yaml(content)
        elif file_format == "json":
            return cls.from_json(content)
        elif file_format == "toml":
            return cls.from_toml(content)
        else:
            raise ValueError("Unsupported file format. Use 'yaml', 'json', or 'toml'.")
