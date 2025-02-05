<h1 align="center">
  Langchain Model Context Protocol Demo
</h1>

## Introduction
This project demonstrates how to use the `langchain-mcp_-connect` package to connect to Model Context Protocol (MCP) servers and access tools that can be made available to LangChain. 
The `langchain_mcp_connect` package allows developers to easily integrate their LLMs with a rich ecosystem of [pre-built](https://github.com/modelcontextprotocol/servers/tree/main) MCP servers.

### Pre-requisites

You will need your personal access tokens for GitHub and OpenAI to run this demo.

```bash
export GITHUB_PERSONAL_ACCESS_TOKEN=<your_github_personal_access_token>
export OPENAI_API_KEY=<your_openai_api_key>
```

Or you can create a `.env` file with the following content:

```bash
GITHUB_PERSONAL_ACCESS_TOKEN=<your_github_personal_access_token>
OPENAI_API_KEY=<your_openai_api_key>
```

### Installation

Pre-commit:

```bash
pre-commit install
```

Python env:
    
```bash
uv sync
```

### Running the streaming demo

```bash
uv run src/main.py
```

