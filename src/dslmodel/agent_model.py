from pydantic import BaseModel, Field

from dslmodel.mixins.file_handler_mixin import FileHandlerMixin
from dslmodel.mixins.instance_mixin import InstanceMixin
from dslmodel.mixins.to_from_mixin import ToFromMixin


class AgentModel(BaseModel, InstanceMixin, ToFromMixin, FileHandlerMixin):
    """A Pydantic model that uses an agent to generate instances."""


async def main():
    class ConfigModel(AgentModel):
        """
        A configuration model that dynamically generates and validates a configuration
        using user input and supports async serialization to various formats.
        """
        app_name: str = Field(..., title="The name of the application.")
        version: str = Field(..., title="The version of the application.")
        settings: dict = Field(..., title="Additional settings for the application.")

    # Generate the ConfigModel dynamically from user input
    config = await ConfigModel.from_prompt(
        "Set up a configuration for my app named 'AwesomeApp' version '1.0'. Add debug, db, MS API keys settings.",
    )

    # Serialize the config to TOML format
    toml_content = await config.to_toml()

    # Print the TOML content
    print("TOML Configuration:")
    print(toml_content)

    # Optionally save to a file (demonstrating async file handling)
    await config.to_toml("config.toml")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
