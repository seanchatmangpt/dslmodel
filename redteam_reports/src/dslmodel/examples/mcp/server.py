# /// script
# dependencies = [
#   "mcp"
# ]
# ///

import asyncio
from typing import List, Dict, Union
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Prompt,
    PromptArgument,
    GetPromptResult,
    PromptMessage,
    TextContent,
    Resource,
)

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional


class WorkflowInput(BaseModel):
    """
    Represents the input schema for a workflow.
    """
    schema: dict = Field(..., description="JSON Schema for the workflow input parameters.")

    model_config = ConfigDict(extra="allow")


class WorkflowOutput(BaseModel):
    """
    Represents the output schema for a workflow.
    """
    schema: dict = Field(..., description="JSON Schema for the workflow output parameters.")

    model_config = ConfigDict(extra="allow")


class WorkflowStep(BaseModel):
    """
    Represents a single step in a workflow.
    """
    stepId: str = Field(..., description="Unique identifier for the step.")
    operationId: str = Field(..., description="Operation or action to execute in this step.")
    description: Optional[str] = Field(None, description="Description of the step.")
    parameters: Optional[dict] = Field(
        None, description="Parameters to pass to this step's operation."
    )
    successCriteria: Optional[List[dict]] = Field(
        None, description="Conditions to consider the step successful."
    )
    outputs: Optional[dict] = Field(
        None, description="Mapping of outputs produced by this step."
    )

    model_config = ConfigDict(extra="allow")


class Workflow(BaseModel):
    """
    Represents a workflow with inputs, outputs, and steps.
    """
    workflowId: str = Field(..., description="Unique identifier for the workflow.")
    description: str = Field(..., description="Description of the workflow.")
    inputs: WorkflowInput = Field(..., description="Input schema for the workflow.")
    outputs: WorkflowOutput = Field(..., description="Output schema for the workflow.")
    steps: Optional[List[WorkflowStep]] = Field(
        None, description="Ordered list of steps that define the workflow."
    )

    model_config = ConfigDict(extra="allow")


class PetstoreServer:
    def __init__(self, server_name: str, server_version: str):
        self.server = Server(server_name)
        self.server_name = server_name
        self.server_version = server_version
        self._register_handlers()

    def _register_handlers(self):
        """
        Register handlers for MCP capabilities like prompts, resources, and workflows.
        """

        @self.server.list_prompts()
        async def list_prompts() -> List[Prompt]:
            return self._handle_list_prompts()

        @self.server.get_prompt()
        async def get_prompt(name: str, arguments: Union[Dict[str, str], None]) -> GetPromptResult:
            return self._handle_get_prompt(name, arguments)

        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            return self._handle_list_resources()

        # @self.server.list_workflows()
        # async def list_workflows() -> List[Workflow]:
        #     return self._handle_list_workflows()
        #
        # @self.server.execute_workflow()
        # async def execute_workflow(workflow_id: str, inputs: Dict) -> WorkflowOutput:
        #     return self._handle_execute_workflow(workflow_id, inputs)

    def _handle_list_prompts(self) -> List[Prompt]:
        """
        Define the prompts available on the server.
        """
        return [
            Prompt(
                name="find-pet",
                description="Find a pet based on its tags.",
                arguments=[
                    PromptArgument(
                        name="tags",
                        description="Comma-separated tags to filter pets.",
                        required=True
                    )
                ]
            )
        ]

    def _handle_get_prompt(self, name: str, arguments: Union[Dict[str, str], None]) -> GetPromptResult:
        """
        Handle retrieving a specific prompt based on its name.
        """
        if name == "find-pet":
            tags = arguments.get("tags", "unknown")
            return GetPromptResult(
                description="Find a pet prompt",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(
                            type="text",
                            text=f"Searching for pets with tags: {tags}"
                        )
                    )
                ]
            )
        raise ValueError(f"Unknown prompt: {name}")

    def _handle_list_resources(self) -> List[Resource]:
        """
        List the available resources in the Petstore server.
        """
        return [
            Resource(
                uri="petstore://pets",
                name="Petstore Pets",
                description="List of pets in the store.",
                mimeType="application/json"
            ),
            Resource(
                uri="petstore://coupons",
                name="Pet Coupons",
                description="Available coupons for pets.",
                mimeType="application/json"
            )
        ]

    async def run(self):
        """
        Run the server with the configured handlers and capabilities.
        """
        capabilities = self.server.get_capabilities(
            notification_options=NotificationOptions(),
            experimental_capabilities={}
        )
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name=self.server_name,
                    server_version=self.server_version,
                    capabilities=capabilities,
                )
            )


# -------------------------
# Main Entry Point
# -------------------------
if __name__ == "__main__":
    async def main():
        server = PetstoreServer(server_name="petstore", server_version="1.0.0")
        await server.run()


    asyncio.run(main())
