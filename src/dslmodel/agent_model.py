from typing import Any, Dict, Optional, TypeVar, Generic
from pydantic import BaseModel, Field, ConfigDict

from dslmodel.mixins.file_handler_mixin import FileHandlerMixin
from dslmodel.mixins.instance_mixin import InstanceMixin
from dslmodel.mixins.to_from_mixin import ToFromMixin

T = TypeVar('T', bound=BaseModel)

class AgentResult(BaseModel):
    """Represents the result of an agent's operation."""
    success: bool = Field(..., description="Whether the operation was successful")
    data: Optional[Dict[str, Any]] = Field(None, description="The result data")
    error: Optional[str] = Field(None, description="Error message if operation failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class AgentModel(BaseModel, InstanceMixin, ToFromMixin, FileHandlerMixin, Generic[T]):
    """A Pydantic model that uses an agent to generate instances with proper result handling."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    result: Optional[AgentResult] = Field(None, description="The result of the last operation")
    
    async def process_result(self, data: Dict[str, Any], success: bool = True, error: Optional[str] = None) -> AgentResult:
        """Process and store the result of an operation."""
        self.result = AgentResult(
            success=success,
            data=data if success else None,
            error=error if not success else None,
            metadata={"timestamp": "current_timestamp"}  # You can add more metadata as needed
        )
        return self.result

    async def clear_result(self) -> None:
        """Clear the current result."""
        self.result = None

    async def get_last_result(self) -> Optional[AgentResult]:
        """Get the last operation result."""
        return self.result

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

    # Process and store the result
    result = await config.process_result(
        data={"status": "success", "message": "Configuration generated successfully"},
        success=True
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
