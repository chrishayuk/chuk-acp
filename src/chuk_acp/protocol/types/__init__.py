"""ACP protocol types."""

from .info import AgentInfo, ClientInfo
from .content import (
    Annotations,
    TextContent,
    ImageContent,
    AudioContent,
    TextResourceContents,
    BlobResourceContents,
    EmbeddedResource,
    ResourceLink,
    Content,
)
from .capabilities import (
    FileSystemCapability,
    TerminalCapability,
    ClientCapabilities,
    PromptCapability,
    MCPServersCapability,
    AgentCapabilities,
)
from .mcp_servers import StdioMCPServer, HttpMCPServer, SseMCPServer, MCPServer
from .session import SessionMode, StopReason, Location
from .tools import ToolCallStatus, ToolCall, ToolCallUpdate
from .plan import PlanEntryStatus, PlanEntryPriority, PlanEntry, Plan, Task, TaskStatus
from .permission import PermissionRequest, PermissionResponse
from .terminal import TerminalInfo, TerminalOutput, TerminalExit
from .commands import AvailableCommand, AvailableCommandInput

__all__ = [
    # Info
    "AgentInfo",
    "ClientInfo",
    # Content
    "Annotations",
    "TextContent",
    "ImageContent",
    "AudioContent",
    "TextResourceContents",
    "BlobResourceContents",
    "EmbeddedResource",
    "ResourceLink",
    "Content",
    # Capabilities
    "FileSystemCapability",
    "TerminalCapability",
    "ClientCapabilities",
    "PromptCapability",
    "MCPServersCapability",
    "AgentCapabilities",
    # MCP Servers
    "StdioMCPServer",
    "HttpMCPServer",
    "SseMCPServer",
    "MCPServer",
    # Session
    "SessionMode",
    "StopReason",
    "Location",
    # Tools
    "ToolCallStatus",
    "ToolCall",
    "ToolCallUpdate",
    # Plan
    "PlanEntryStatus",
    "PlanEntryPriority",
    "PlanEntry",
    "Plan",
    "Task",  # Legacy alias
    "TaskStatus",  # Legacy alias
    # Permission
    "PermissionRequest",
    "PermissionResponse",
    # Terminal
    "TerminalInfo",
    "TerminalOutput",
    "TerminalExit",
    # Commands
    "AvailableCommand",
    "AvailableCommandInput",
]
