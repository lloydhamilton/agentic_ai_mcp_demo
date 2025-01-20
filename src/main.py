import asyncio

import streamlit as st
from langchain_mcp.get_servers import LangChainMcp

from app.agent import AgenticInterface


@st.cache_data(show_spinner="Loading AI Tools...🔧")
def list_tools() -> dict:
    """List all available tools.

    Calls all list tools method for all configured MCP servers.
    """
    mcp = LangChainMcp()
    return asyncio.run(mcp.fetch_all_server_tools())


@st.cache_data(show_spinner="Loading Resources...🔧")
def list_resources() -> dict:
    """List all available resources.

    Calls all list resources method for all configured MCP servers.
    """
    mcp = LangChainMcp()
    return asyncio.run(mcp.list_all_server_resources())


if __name__ == "__main__":
    inner_claude = AgenticInterface(session_state=st.session_state)
    inner_claude.start(list_tools(), list_resources())
