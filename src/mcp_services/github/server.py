import base64
import json
import logging
import os
from enum import Enum

import requests
from dotenv import load_dotenv
from mcp.server import Server
from mcp.types import Resource, TextContent, Tool
from schemas import GetFileContentsArgs, GetTreeArgs, GitHubContent, GitHubTreeResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("github-server")
logger.info("GitHub server started.")

load_dotenv()
app = Server("github")


class GitHubTools(str, Enum):
    """Tool box definitions."""

    GET_FILE_CONTENTS = "get_file_contents"
    LIST_REPO_TREE = "list_repo_tree"


def get_file_contents(args: GetFileContentsArgs) -> GitHubContent:
    """Get the contents of a file from a GitHub repository."""
    url = f"https://api.github.com/repos/{args.owner}/{args.repo}/contents/{args.path}"
    if args.branch:
        url += f"?ref={args.branch}"
    headers = {
        "Authorization": f"token {os.environ.get('GITHUB_PERSONAL_ACCESS_TOKEN')}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "github-mcp-server",
    }

    resp = requests.get(url, headers=headers)
    resp.raise_for_status()

    content = GitHubContent.model_validate(resp.json())

    if content.content:
        content.content = base64.b64decode(content.content).decode("utf-8")

    return content


def list_repo_tree(args: GetTreeArgs) -> str:
    """List the tree structure of a GitHub repository."""
    url = (
        f"https://api.github.com/repos/{args.owner}/{args.repo}/git/trees/"
        f"{args.branch}?recursive={args.recursive}"
    )
    logger.info(f"Listing tree for: {url}")
    headers = {
        "Authorization": f"token {os.environ.get('GITHUB_PERSONAL_ACCESS_TOKEN')}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "github-mcp-server",
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()

    # logger.info(resp.json())
    logger.info(GitHubTreeResponse.model_validate(resp.json()))

    content = GitHubTreeResponse.model_validate(resp.json())

    return json.dumps(content.model_dump(mode="json"))


@app.list_resources()
async def list_resources() -> list[Resource]:
    """List available resources."""
    return []


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available weather tools."""
    return [
        Tool(
            name="get_file_contents",
            description="Retrieve the file contents of a file from a github repository",
            inputSchema=GetFileContentsArgs.model_json_schema(),
        ),
        Tool(
            name="list_repo_tree",
            description="List the tree structure of a GitHub repository",
            inputSchema=GetTreeArgs.model_json_schema(),
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle the call_tool for the vector store service."""
    match name:
        case GitHubTools.GET_FILE_CONTENTS:
            args = GetFileContentsArgs(**arguments)
            file = get_file_contents(args)
            return [TextContent(type="text", text=file.content)]
        case GitHubTools.LIST_REPO_TREE:
            args = GetTreeArgs(**arguments)
            tree = list_repo_tree(args)
            return [TextContent(type="text", text=tree)]
        case _:
            raise ValueError(f"Unknown tool: {name}")


async def main() -> None:
    """Main entry point for server."""
    # Import here to avoid issues with event loops
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())
