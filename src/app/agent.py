import argparse
import asyncio
import logging

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_mcp_connect import MspToolPrompt, call_tool
from langchain_mcp_connect.get_servers import LangChainMcp
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

load_dotenv()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("LangChainMcp")


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


async def invoke_agent(
    model: ChatOpenAI, query: str, tools: dict, resources: dict
) -> dict:
    """Invoke the agent with the given query."""
    agent_executor = create_react_agent(model, [call_tool])

    # Create a system prompt and a human message
    system_prompt = MspToolPrompt(tools=tools, resources=resources).get_prompt()
    human_message = HumanMessage(content=query)

    # Invoke the agent
    r = await agent_executor.ainvoke(
        input=dict(messages=[system_prompt, human_message])
    )

    return r


if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Langchain Model Context Protocol demo"
    )
    parser.add_argument("-q", "--query", type=str, help="Query to be executed")
    args = parser.parse_args()

    # Define the llm
    llm = ChatOpenAI(
        model="gpt-4o",
        model_kwargs={
            "max_tokens": 4096,
            "temperature": 0.0,
        },
    )

    # Invoke the agent
    response = asyncio.run(
        invoke_agent(llm, args.query, list_tools(), list_resources())
    )

    log.info(response)
