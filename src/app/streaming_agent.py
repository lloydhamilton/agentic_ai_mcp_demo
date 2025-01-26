import asyncio
import logging
from collections.abc import AsyncIterator

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import BaseTool
from langchain_mcp_connect import LangChainMcp
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

load_dotenv()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("LangChainMcp")


class MCPDemo:
    """InnerClaude class."""

    def __init__(self) -> None:
        """Initialise the MCPDemo class.

        Initialise the MCP parameters from the `claude_mcp_config.json` file.
        """
        self.conversation = []
        self._llm = None
        self.mcp = LangChainMcp()

    @property
    def llm(self) -> ChatOpenAI:
        """Get the language model."""
        if self._llm is None:
            self._llm = ChatOpenAI(
                model="gpt-4o",
                temperature=0.0,
                max_tokens=4096,
            )
        return self._llm

    async def process_open_ai_stream(self, stream: AsyncIterator) -> None:
        """Custom stream processor for Open AI.

        Args:
            stream: The stream to process.

        Returns:
            AsyncGenerator: An async generator object containing the chunk of data.
        """
        if stream:
            output = ""
            async for chunk in stream:
                if chunk.get("event") == "on_chat_model_stream":
                    content = chunk["data"]["chunk"].content
                    output += content
                    print(content, end="", flush=True)
            self.conversation.append(AIMessage(content=output))

    async def agent(self, tools: list[BaseTool]) -> None:
        """Create the React agent with tools.

        Args:
            tools (list[BaseTool]): The tools to be attached to langchain agent.
        """
        agent_executor = create_react_agent(self.llm, tools)
        stream = agent_executor.astream_events(
            dict(messages=self.conversation), version="v2"
        )
        await self.process_open_ai_stream(stream)

    def start(self, tools: list[BaseTool], query: str) -> None:
        """Initialise the agent with the MCP server tools.

        Args:
            tools (list[BaseTool]): The tools to be attached to langchain agent.
            query (str): The query to start the agent with.
        """
        self.conversation.append(HumanMessage(content=query))
        asyncio.run(self.agent(tools))
