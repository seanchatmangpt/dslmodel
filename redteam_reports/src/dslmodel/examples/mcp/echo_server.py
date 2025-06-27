import asyncio
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, CallToolResult
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions

# Create a minimal server instance
server = Server("simple-server")


@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="echo",
            description="Echoes the input text.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to echo"}
                },
                "required": ["text"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name, arguments):
    if name == "echo":
        text = arguments.get("text", "")
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Operation successful: {text}"
                )
            ]
        )
    return CallToolResult(
        isError=True,
        content=[
            TextContent(type="text", text=f"Tool '{name}' not found.").model_dump()
        ]
    )


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="example",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
