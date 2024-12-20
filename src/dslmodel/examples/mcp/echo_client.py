import asyncio
from mcp import ClientSession, StdioServerParameters, ListToolsResult
from mcp.client.stdio import stdio_client


async def main():
    server_path = "/Users/sac/dev/dslmodel/src/dslmodel/examples/mcp/echo_server.py"
    python_path = "/Users/sac/Library/Caches/pypoetry/virtualenvs/pydantic-all-in-one-1QljSpBF-py3.12/bin/python"

    async with stdio_client(
            StdioServerParameters(command=python_path, args=[server_path])
    ) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            # # List available resources
            # resources = await session.list_resources()
            #
            # # List available prompts
            # prompts = await session.list_prompts()

            # List available tools
            # tools: ListToolsResult = await session.list_tools()
            #
            # print(tools.model_dump())

            result = await session.call_tool("echo", arguments={"text": "value"})
            print(result)

            # # Read a resource
            # resource = await session.read_resource("file://some/path")
            #
            # # Call a tool
            # result = await session.call_tool("tool-name", arguments={"arg1": "value"})
            #
            # # Get a prompt
            # prompt = await session.get_prompt("prompt-name", arguments={"arg1": "value"})


if __name__ == "__main__":
    asyncio.run(main())
