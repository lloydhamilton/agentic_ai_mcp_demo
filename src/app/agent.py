import asyncio
import logging
from collections.abc import AsyncGenerator, AsyncIterator
from typing import Any

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_mcp import MspToolPrompt, call_tool, load_mcp_params
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

load_dotenv()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("InnerClaude")


class AgenticInterface:
    """InnerClaude class."""

    def __init__(self, session_state: st.session_state) -> None:
        """Initialise the InnerClaude class.

        Args:
            session_state: The session state of the current streamlit app.

        """
        self.session_state = self.initialise_session_state(session_state)
        self.mcp = load_mcp_params()

    @property
    def llm(self) -> ChatOpenAI:
        """Get the language model."""
        if self.session_state.llm is None:
            self.session_state.llm = ChatOpenAI(
                model="gpt-4o",
                model_kwargs={
                    "max_tokens": 4096,
                    "temperature": 0.0,
                },
            )
        return self.session_state.llm

    @staticmethod
    def initialise_session_state(session_state: st.session_state) -> st.session_state:
        """Check the session state.

        If the session state does not contain the messages key, initialise it.

        Args:
            session_state: The session state of the current streamlit app.
        """
        if "llm" not in session_state:
            session_state["llm"] = None
        if "conversation" not in session_state:
            session_state["conversation"] = []
        return session_state

    @staticmethod
    def to_sync_generator(async_gen: AsyncGenerator) -> None:
        """Convert an async generator to a synchronous generator.

        This is required because there is no way to use async for loops in Streamlit
        write_stream method.

        Args:
            async_gen: The async generator to convert to a synchronous generator.
        """
        if async_gen:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                while True:
                    try:
                        yield loop.run_until_complete(anext(async_gen))
                    except StopAsyncIteration:
                        break
            finally:
                loop.close()

    @staticmethod
    def trim_context_window(message: list[dict], window: int = 10) -> list[dict]:
        """Trim the context window of the message.

        Args:
            message (list[dict]): The message to be trimmed.
            window (int): The window size to trim the message.

        Returns:
            list[dict]: The trimmed message.
        """
        msg = None

        # return only the first element if there is only one element
        if len(message) <= window:
            msg = message

        # return the last five elements if there are more than five elements
        if len(message) > window:
            msg = message[-window:]

        # if the first element is an assistant message, remove it
        message_type = [item["role"] for item in msg]
        if message_type[0] == "assistant":
            msg = msg[1:]

        return msg

    @staticmethod
    def title(title: str) -> None:
        """Set the title of the app.

        Args:
            title: The title of the app.
        """
        st.title(title)
        st.subheader(
            "Powered by Open AI:GPT-4o"
        )

    def update_chat_window(self) -> None:
        """Update the chat context.

        This method updates the chat context with the messages from the session state.
        It hides the system messages from the chat and only displays the human and
        assistant messages.
        """
        messages = self.session_state.conversation
        messages = [msg for msg in messages if not isinstance(msg, SystemMessage)]
        for msg in messages:
            if isinstance(msg, HumanMessage):
                st.chat_message("human").write(msg.content)
            elif isinstance(msg, AIMessage):
                st.chat_message("assistant").write(msg.content)

    async def process_open_ai_stream(self, stream: AsyncIterator) -> AsyncGenerator:
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
                    output += chunk["data"]["chunk"].content
                    yield chunk["data"]["chunk"].content
            self.session_state.conversation.append(AIMessage(content=output))

    async def agent(self, tools: dict, resources: dict) -> AsyncIterator[dict[str, Any] | Any]:
        """Create the agent with the proper tools.

        Args:
            tools (dict): A dict object returning a list of callable tool
                that can be made to MSP servers.
            resources (dict): A dict object returning a list of callable resources
                that can be made to MSP servers.

        Returns:
            AsyncIterator: An async iterator object containing the agent response as
                a data stream.
        """
        # TODO: Add error handling
        if query := st.chat_input():
            # Write prompt to chat and append to session state
            st.chat_message("user").write(query)

            # Create a system prompt if the conversation is not initialised
            self.create_system_prompt(tools, resources)

            # Append the user message to the conversation
            self.session_state.conversation.append(HumanMessage(content=query))

            # Initialise the agent executor with the call tools
            agent_executor = create_react_agent(self.llm, [call_tool])
            # log.info(self.session_state.conversation)
            return agent_executor.astream_events(
                dict(messages=self.session_state.conversation), version="v2"
            )

    def chat_agent(self, tools: dict, resources: dict) -> None:
        """Chat agent that writes stream to chat_message window.

        Args:
            tools (dict): The tools to be used in the system prompt.
            resources (dict): The resources to be used in the system prompt.
        """
        stream = asyncio.run(self.agent(tools, resources))
        if stream:
            st.chat_message("assistant").write_stream(
                self.to_sync_generator(self.process_open_ai_stream(stream))
            )
            # log.info(self.session_state.conversation)

    def create_system_prompt(self, tools: dict, resources: dict) -> None:
        """Add a system prompt if the conversation is not initialised.

        Args:
            tools (dict): The tools to be used in the system prompt.
            resources (dict): The resources to be used in the system prompt.

        Returns:
            dict: The system prompt.
        """
        if not self.session_state.conversation:
            system_prompt = MspToolPrompt(tools=tools, resources=resources).get_prompt()
            self.session_state.conversation.append(system_prompt)

    def start(self, tools: dict, resources: dict) -> None:
        """Start the app."""
        self.title("💬 Model Context Protocol Demo")
        st.chat_message("assistant").write("How can I help you?")
        self.update_chat_window()
        self.chat_agent(tools, resources)
