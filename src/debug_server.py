from langchain_mcp_connect.data_models import StdioServerParameters
from mcp import ClientSession
from mcp.client.stdio import stdio_client

# Create server parameters for stdio connection
server_params = StdioServerParameters(
    command="python",
    args=["src/mcp_services/github"],
    env={"GITHUB_PERSONAL_ACCESS_TOKEN": "ENV_GITHUB_PERSONAL_ACCESS_TOKEN"},
)


async def run() -> None:
    """Run the client."""
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            # Initialize the connection
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            print(tools)

            # Call a tool
            call_result = await session.call_tool(
                "get_file_contents",
                arguments={
                    "owner": "modelcontextprotocol",
                    "repo": "python-sdk",
                    "path": "LICENSE",
                },
            )
            print(call_result)


if __name__ == "__main__":
    import asyncio

    asyncio.run(run())
