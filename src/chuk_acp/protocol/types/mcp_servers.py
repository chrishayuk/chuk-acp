"""MCP server configuration types."""

from typing import Optional, List, Dict, Union
from ..acp_pydantic_base import AcpPydanticBase, PYDANTIC_AVAILABLE

if PYDANTIC_AVAILABLE:
    from ..acp_pydantic_base import ConfigDict


class StdioMCPServer(AcpPydanticBase):
    """MCP server connection via stdio (mandatory support)."""

    command: str
    """Command to execute."""

    args: Optional[List[str]] = None
    """Command arguments."""

    env: Optional[Dict[str, str]] = None
    """Environment variables."""

    if PYDANTIC_AVAILABLE:
        model_config = ConfigDict(extra="allow")


class HttpMCPServer(AcpPydanticBase):
    """MCP server connection via HTTP (optional capability)."""

    url: str
    """HTTP endpoint URL."""

    headers: Optional[Dict[str, str]] = None
    """Custom HTTP headers."""

    if PYDANTIC_AVAILABLE:
        model_config = ConfigDict(extra="allow")


class SseMCPServer(AcpPydanticBase):
    """MCP server connection via SSE (deprecated, optional capability)."""

    url: str
    """SSE endpoint URL."""

    headers: Optional[Dict[str, str]] = None
    """Custom HTTP headers."""

    if PYDANTIC_AVAILABLE:
        model_config = ConfigDict(extra="allow")


# Union type for any MCP server configuration
MCPServer = Union[StdioMCPServer, HttpMCPServer, SseMCPServer]
