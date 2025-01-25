import asyncio
import logging
from collections.abc import AsyncIterator

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_mcp_connect import MspToolPrompt, call_tool
from langchain_mcp_connect.get_servers import LangChainMcp
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

    async def agent(self) -> None:
        """Create the React agent with tools."""
        # Initialise the agent executor with the call tools
        agent_executor = create_react_agent(self.llm, [call_tool])
        stream = agent_executor.astream_events(
            dict(messages=self.conversation), version="v2"
        )
        await self.process_open_ai_stream(stream)

    def create_system_prompt(self, tools: dict, resources: dict) -> None:
        """Add a system prompt if the conversation is not initialised.

        Args:
            tools (dict): The tools to be used in the system prompt.
            resources (dict): The resources to be used in the system prompt.

        Returns:
            dict: The system prompt.
        """
        if not self.conversation:
            system_prompt = MspToolPrompt(tools=tools, resources=resources).get_prompt()
            self.conversation.append(system_prompt)

    def start(self, tools: dict, resources: dict, query: str) -> None:
        """Start the agent with the tools and resources.

        Args:
            tools (dict): The tools to be used in the system prompt.
            resources (dict): The resources to be used in the system prompt.
            query (str): The query to start the agent with.
        """
        self.create_system_prompt(tools, resources)
        self.conversation.append(HumanMessage(content=query))
        asyncio.run(self.agent())
