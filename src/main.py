import argparse
import asyncio

from langchain_mcp_connect.get_servers import LangChainMcp

from app.streaming_agent import MCPDemo


def list_tools() -> dict:
    """List all available tools.

    Calls all list tools method for all configured MCP servers.
    """
    mcp = LangChainMcp()
    return asyncio.run(mcp.fetch_all_server_tools())


def list_resources() -> dict:
    """List all available resources.

    Calls all list resources method for all configured MCP servers.
    """
    mcp = LangChainMcp()
    return asyncio.run(mcp.list_all_server_resources())


if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Langchain Model Context Protocol demo"
    )
    parser.add_argument("-q", "--query", type=str, help="Query to be executed")
    args = parser.parse_args()

    agent = MCPDemo()
    agent.start(list_tools(), list_resources(), args.query)
