"""ACP capability types for agents and clients."""

from typing import Optional, List, Literal
from ..acp_pydantic_base import AcpPydanticBase, PYDANTIC_AVAILABLE

if PYDANTIC_AVAILABLE:
    from ..acp_pydantic_base import ConfigDict


class FileSystemCapability(AcpPydanticBase):
    """Client capability for file system operations."""

    readTextFile: Optional[bool] = None
    """Can read text files."""

    writeTextFile: Optional[bool] = None
    """Can write text files."""

    if PYDANTIC_AVAILABLE:
        model_config = ConfigDict(extra="allow")


class TerminalCapability(AcpPydanticBase):
    """Client capability for terminal operations."""

    create: Optional[bool] = None
    """Can create terminal sessions."""

    output: Optional[bool] = None
    """Can send terminal output."""

    release: Optional[bool] = None
    """Can release terminal control."""

    waitForExit: Optional[bool] = None
    """Can wait for process exit."""

    kill: Optional[bool] = None
    """Can kill running processes."""

    if PYDANTIC_AVAILABLE:
        model_config = ConfigDict(extra="allow")


class ClientCapabilities(AcpPydanticBase):
    """Capabilities supported by the client (editor)."""

    fs: Optional[FileSystemCapability] = None
    """File system operations."""

    terminal: Optional[TerminalCapability] = None
    """Terminal command execution."""

    if PYDANTIC_AVAILABLE:
        model_config = ConfigDict(extra="allow")


class PromptCapability(AcpPydanticBase):
    """Agent capability for prompt content types."""

    image: Optional[bool] = None
    """Supports image content in prompts."""

    audio: Optional[bool] = None
    """Supports audio content in prompts."""

    embeddedContext: Optional[bool] = None
    """Supports embedded resource content."""

    if PYDANTIC_AVAILABLE:
        model_config = ConfigDict(extra="allow")


class MCPServersCapability(AcpPydanticBase):
    """Agent capability for MCP server transports."""

    http: Optional[bool] = None
    """Supports HTTP transport for MCP servers."""

    sse: Optional[bool] = None
    """Supports SSE transport for MCP servers (deprecated)."""

    if PYDANTIC_AVAILABLE:
        model_config = ConfigDict(extra="allow")


class AgentCapabilities(AcpPydanticBase):
    """Capabilities supported by the agent."""

    loadSession: Optional[bool] = None
    """Whether agent supports loading previous sessions."""

    modes: Optional[List[Literal["ask", "architect", "code"]]] = None
    """Supported session modes."""

    prompts: Optional[PromptCapability] = None
    """Prompt content type capabilities."""

    mcpServers: Optional[MCPServersCapability] = None
    """MCP server transport capabilities."""

    if PYDANTIC_AVAILABLE:
        model_config = ConfigDict(extra="allow")
