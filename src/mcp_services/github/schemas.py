from pydantic import BaseModel, Field


class GetFileContentsArgs(BaseModel):
    """Data model for method get_file_contents arguments."""

    owner: str = Field(..., description="The owner of the GitHub repository.")
    repo: str = Field(..., description="The repository name.")
    path: str = Field(..., description="The path to the file.")
    branch: str | None = Field(None, description="The branch name.")


class GitHubContent(BaseModel):
    """Data model for the GitHub API response content."""

    url: str | None = Field(
        None, description="The URL that was called to fetch the content."
    )
    content: str | None = Field(
        None, description="The content of the file in base64 encoding."
    )
    message: str | None = Field(
        None, description="The message returned when request is not 200."
    )
    status: int | None = Field(None, description="The status code of the response.")


class GetTreeArgs(BaseModel):
    """Data model for method get_file_contents arguments."""

    owner: str = Field(..., description="The owner of the GitHub repository.")
    repo: str = Field(..., description="The repository name.")
    branch: str = Field("main", description="The branch name. Defaults to main.")
    recursive: int = Field(1, description="The depth of recursion. Defaults to 1.")


class TreeItem(BaseModel):
    """Data model for a GitHub tree item."""

    path: str = Field(..., description="The path of the item in the repository.")
    mode: str = Field(..., description="The mode of the item.")
    type: str = Field(..., description="The type of the item (blob or tree).")
    sha: str = Field(..., description="The SHA hash of the item.")
    size: int | None = Field(None, description="The size of the item, if applicable.")
    url: str = Field(..., description="The URL to access the item.")


class GitHubTreeResponse(BaseModel):
    """Data model for the GitHub API response for a tree."""

    sha: str = Field(..., description="The SHA hash of the tree.")
    url: str = Field(..., description="The URL to access the tree.")
    tree: list[TreeItem] = Field(..., description="The list of items in the tree.")
    truncated: bool = Field(..., description="Indicates if the tree is truncated.")
