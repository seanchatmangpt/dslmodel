from typing import TypeVar
import os
import aiofiles

T = TypeVar("T", bound="BaseModel")


class FileHandlerMixin:
    """
    A mixin class that provides async file handling functionalities for saving and loading
    models to and from YAML, JSON, and TOML formats.
    """

    async def generate_filename(self, ext: str = "yaml", add_timestamp: bool = False) -> str:
        """
        Generates a safe filename based on the model's content.

        :param ext: The file extension (e.g., 'yaml', 'json', 'toml').
        :param add_timestamp: Whether to append a timestamp to the filename.
        :return: The generated filename.
        """
        from dslmodel.dspy_modules.file_name_module import file_name_call

        content = await self.to_yaml()  # Use the YAML representation to generate the filename
        filename = await file_name_call(file_content=content, ext=ext)
        return filename

    async def save(
            self, file_path: str | None = None, file_format: str = "yaml", add_timestamp: bool = False
    ) -> str:
        """
        Saves the model to a file in the specified format. Automatically generates a filename if not provided.

        :param file_path: The path to the file. If None, generates a filename.
        :param file_format: The format to save the file in ('yaml', 'json', 'toml').
        :param add_timestamp: Whether to append a timestamp to the filename.
        :return: The path to the saved file.
        """
        if file_path is None:
            file_path = await self.generate_filename(ext=file_format, add_timestamp=add_timestamp)

        if file_format == "yaml":
            content = await self.to_yaml()
        elif file_format == "json":
            content = await self.to_json()
        elif file_format == "toml":
            content = await self.to_toml()
        else:
            raise ValueError("Unsupported file format. Use 'yaml', 'json', or 'toml'.")

        async with aiofiles.open(file_path, "w") as file:
            await file.write(content)

        return file_path

    @classmethod
    async def load(cls: type[T], file_path: str) -> T:
        """
        Loads a model from a file, inferring the file format from its extension.

        :param file_path: The path to the file.
        :return: An instance of the model populated with data from the file.
        :raises ValueError: If the file format is unsupported.
        """
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        async with aiofiles.open(file_path, "r") as file:
            content = await file.read()

        if ext in [".yaml", ".yml"]:
            return await cls.from_yaml(content)
        elif ext == ".json":
            return await cls.from_json(content)
        elif ext == ".toml":
            return await cls.from_toml(content)
        else:
            raise ValueError(f"Unsupported file format '{ext}'. Supported formats are 'yaml', 'json', 'toml'.")
