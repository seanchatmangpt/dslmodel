import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Union


class WorkflowInput(BaseModel):
    schema: dict = Field(...)

    model_config = ConfigDict(extra="allow")


class WorkflowOutput(BaseModel):
    schema: dict = Field(...)

    model_config = ConfigDict(extra="allow")


class WorkflowStep(BaseModel):
    stepId: str = Field(...)
    operationId: str = Field(...)
    description: Union[str, None] = Field(None)
    parameters: Union[dict, None] = Field(None)
    successCriteria: Union[List[dict], None] = Field(None)
    outputs: Union[dict, None] = Field(None)

    model_config = ConfigDict(extra="allow")


class Workflow(BaseModel):
    workflowId: str = Field(...)
    description: str = Field(...)
    inputs: WorkflowInput = Field(...)
    outputs: WorkflowOutput = Field(...)
    steps: Union[List[WorkflowStep], None] = Field(None)

    model_config = ConfigDict(extra="allow")


class MCPClient:
    def __init__(self, command: str, args: List[str] = None, env: Dict[str, str] = None):
        self.server_params = StdioServerParameters(
            command=command,
            args=args or [],
            env=env or {}
        )
        self.session = None
        self.read = None
        self.write = None
        self._stdio_context = None

    async def __aenter__(self):
        self._stdio_context = stdio_client(self.server_params)
        self.read, self.write = await self._stdio_context.__aenter__()
        self.session = ClientSession(self.read, self.write)
        await self.session.__aenter__()
        await self.session.initialize()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if self.session:
            try:
                await self.session.__aexit__(exc_type, exc_value, traceback)
            except Exception as e:
                print(f"Error during session cleanup: {e}")
        if self._stdio_context:
            await self._stdio_context.__aexit__(exc_type, exc_value, traceback)

    # async def list_workflows(self) -> List[Workflow]:
    #     try:
    #         workflows = await self.session.list_workflows()
    #         return [Workflow(**workflow) for workflow in workflows]
    #     except Exception as e:
    #         print(f"Error while listing workflows: {e}")
    #         return []
    #
    # async def execute_workflow(self, workflow_id: str, inputs: Dict) -> Dict:
    #     try:
    #         return await self.session.execute_workflow(workflow_id, inputs)
    #     except Exception as e:
    #         print(f"Error while executing workflow {workflow_id}: {e}")
    #         return {}


async def main():
    server_path = "/Users/sac/dev/dslmodel/src/dslmodel/examples/mcp/server.py"
    async with MCPClient(
            command="/Users/sac/Library/Caches/pypoetry/virtualenvs/pydantic-all-in-one-1QljSpBF-py3.12/bin/python",
            args=[server_path]
    ) as client:
        workflows = await client.list_workflows()
        print("Workflows:", workflows)

        workflow_inputs = {
            "pet_tags": "puppy, dalmatian",
            "coupon_code": "DISCOUNT2024"
        }
        result = await client.execute_workflow("apply-coupon", workflow_inputs)
        print("Workflow Result:", result)


if __name__ == "__main__":
    asyncio.run(main())
