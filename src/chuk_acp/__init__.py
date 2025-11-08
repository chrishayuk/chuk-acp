"""Agent Client Protocol (ACP) implementation for Python.

A pure protocol library implementing the Agent Client Protocol (ACP) specification.
ACP standardizes communication between code editors and AI coding agents.
"""

# Protocol types
from .protocol.types import (
    # Info
    AgentInfo,
    ClientInfo,
    # Content
    TextContent,
    ImageContent,
    AudioContent,
    EmbeddedResource,
    ResourceLink,
    Content,
    Annotations,
    # Capabilities
    AgentCapabilities,
    ClientCapabilities,
    # Session
    SessionMode,
    StopReason,
    Location,
    # Tools
    ToolCall,
    ToolCallUpdate,
    # Plan
    Plan,
    PlanEntry,
    PlanEntryStatus,
    PlanEntryPriority,
    Task,  # Legacy alias
    TaskStatus,  # Legacy alias
    # MCP Servers
    StdioMCPServer,
    HttpMCPServer,
    MCPServer,
    # Commands
    AvailableCommand,
    AvailableCommandInput,
)

# Protocol messages
from .protocol.messages import (
    # Core
    send_message,
    send_notification,
    CancellationToken,
    # Initialize
    send_initialize,
    send_authenticate,
    # Session
    send_session_new,
    send_session_load,
    send_session_prompt,
    send_session_set_mode,
    send_session_update,
    send_session_cancel,
    send_session_request_permission,
    # File system
    send_fs_read_text_file,
    send_fs_write_text_file,
    # Terminal
    send_terminal_create,
    send_terminal_output,
    send_terminal_release,
    send_terminal_wait_for_exit,
    send_terminal_kill,
)

# Transport
from .transport import (
    Transport,
    StdioTransport,
    StdioParameters,
    stdio_transport,
)

# High-level client
from .client import (
    ACPClient,
    PromptResult,
    SessionUpdate,
    SessionInfo,
    AgentConfig,
    load_agent_config,
)

# High-level agent
from .agent import (
    ACPAgent,
    AgentSession,
)

__version__ = "0.1.0"

__all__ = [
    # Types - Info
    "AgentInfo",
    "ClientInfo",
    # Types - Content
    "TextContent",
    "ImageContent",
    "AudioContent",
    "EmbeddedResource",
    "ResourceLink",
    "Content",
    "Annotations",
    # Types - Capabilities
    "AgentCapabilities",
    "ClientCapabilities",
    # Types - Session
    "SessionMode",
    "StopReason",
    "Location",
    # Types - Tools
    "ToolCall",
    "ToolCallUpdate",
    # Types - Plan
    "Plan",
    "PlanEntry",
    "PlanEntryStatus",
    "PlanEntryPriority",
    "Task",  # Legacy alias
    "TaskStatus",  # Legacy alias
    # Types - MCP Servers
    "StdioMCPServer",
    "HttpMCPServer",
    "MCPServer",
    # Types - Commands
    "AvailableCommand",
    "AvailableCommandInput",
    # Messages - Core
    "send_message",
    "send_notification",
    "CancellationToken",
    # Messages - Initialize
    "send_initialize",
    "send_authenticate",
    # Messages - Session
    "send_session_new",
    "send_session_load",
    "send_session_prompt",
    "send_session_set_mode",
    "send_session_update",
    "send_session_cancel",
    "send_session_request_permission",
    # Messages - File system
    "send_fs_read_text_file",
    "send_fs_write_text_file",
    # Messages - Terminal
    "send_terminal_create",
    "send_terminal_output",
    "send_terminal_release",
    "send_terminal_wait_for_exit",
    "send_terminal_kill",
    # Transport
    "Transport",
    "StdioTransport",
    "StdioParameters",
    "stdio_transport",
    # Client
    "ACPClient",
    "PromptResult",
    "SessionUpdate",
    "SessionInfo",
    "AgentConfig",
    "load_agent_config",
    # Agent
    "ACPAgent",
    "AgentSession",
]
