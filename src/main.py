import argparse
import asyncio
import logging
from functools import lru_cache

from langchain_mcp_connect.get_servers import LangChainMcp

from app.streaming_agent import MCPDemo

for logger_name in [
    "mcp_services.get_servers",
    "github-server",
    # "mcp.server.lowlevel.server",
    "langchain_mcp_connect",
    "mcp_services",
]:
    logging.getLogger(logger_name).setLevel(logging.ERROR)


@lru_cache
def list_tools() -> dict:
    """List all available tools.

    Calls all list tools method for all configured MCP servers.
    """
    mcp = LangChainMcp()
    return asyncio.run(mcp.fetch_all_server_tools())


@lru_cache
def list_resources() -> dict:
    """List all available resources.

    Calls all list resources method for all configured MCP servers.
    """
    mcp = LangChainMcp()
    return asyncio.run(mcp.list_all_server_resources())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Langchain Model Context Protocol demo"
    )
    parser.add_argument(
        "-q", "--query", type=str, help="Query to be executed", nargs="?"
    )
    args = parser.parse_args()

    tools = list_tools()
    resources = list_resources()
    agent = MCPDemo()

    if args.query:
        agent.start(tools, resources, args.query)
    else:
        print("Welcome to MCP Demo! Type 'exit' or 'quit' to end the session.")
        print("Enter your query:")

        while True:
            try:
                query = input("> ").strip()
                if query.lower() in ["exit", "quit"]:
                    print("Goodbye!")
                    break
                if query:  # Only process non-empty queries
                    agent.start(list_tools(), list_resources(), query)
                    print("\nEnter your next query:")
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
                print("Enter your next query:")
