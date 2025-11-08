"""ACP session messages."""

from typing import Optional, List, Dict, Any
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream

from .send_message import send_message, send_notification, CancellationToken
from ..constants import (
    METHOD_SESSION_NEW,
    METHOD_SESSION_LOAD,
    METHOD_SESSION_PROMPT,
    METHOD_SESSION_UPDATE,
    METHOD_SESSION_SET_MODE,
    METHOD_SESSION_CANCEL,
    METHOD_SESSION_REQUEST_PERMISSION,
)
from ..types import (
    Content,
    MCPServer,
    SessionMode,
    StopReason,
    Plan,
    ToolCall,
    ToolCallUpdate,
    PermissionRequest,
    PermissionResponse,
    AvailableCommand,
)


class SessionNewResult:
    """Result of session/new request."""

    def __init__(self, sessionId: str):
        self.sessionId = sessionId


async def send_session_new(
    read_stream: MemoryObjectReceiveStream[Any],
    write_stream: MemoryObjectSendStream[Any],
    cwd: str,
    mcp_servers: Optional[List[MCPServer]] = None,
    mode: Optional[SessionMode] = None,
    *,
    timeout: float = 60.0,
) -> SessionNewResult:
    """Create a new session.

    Args:
        read_stream: Stream to receive messages.
        write_stream: Stream to send messages.
        cwd: Working directory for the session. Must be an absolute path.
        mcp_servers: List of MCP server configurations.
        mode: Initial session mode (ask, architect, code).
        timeout: Request timeout in seconds.

    Returns:
        SessionNewResult with session ID.

    Raises:
        Exception: If session creation fails.
    """
    params: Dict[str, Any] = {
        "cwd": cwd,
    }

    if mcp_servers:
        params["mcpServers"] = [server.model_dump(exclude_none=True) for server in mcp_servers]

    if mode:
        params["mode"] = mode

    result = await send_message(
        read_stream,
        write_stream,
        method=METHOD_SESSION_NEW,
        params=params,
        timeout=timeout,
    )

    return SessionNewResult(sessionId=result["sessionId"])


async def send_session_load(
    read_stream: MemoryObjectReceiveStream[Any],
    write_stream: MemoryObjectSendStream[Any],
    session_id: str,
    cwd: str,
    mcp_servers: Optional[List[MCPServer]] = None,
    *,
    timeout: float = 120.0,
) -> Dict[str, Any]:
    """Load an existing session (requires loadSession capability).

    The agent will replay the conversation history via session/update notifications.

    Args:
        read_stream: Stream to receive messages.
        write_stream: Stream to send messages.
        session_id: Session ID to load.
        cwd: Working directory for the session. Must be an absolute path.
        mcp_servers: List of MCP server configurations.
        timeout: Request timeout in seconds (longer for history replay).

    Returns:
        Load result.

    Raises:
        Exception: If session loading fails.
    """
    params: Dict[str, Any] = {
        "sessionId": session_id,
        "cwd": cwd,
    }

    if mcp_servers:
        params["mcpServers"] = [server.model_dump(exclude_none=True) for server in mcp_servers]

    return await send_message(
        read_stream,
        write_stream,
        method=METHOD_SESSION_LOAD,
        params=params,
        timeout=timeout,
    )


class PromptResult:
    """Result of session/prompt request."""

    def __init__(self, stopReason: StopReason):
        self.stopReason = stopReason


async def send_session_prompt(
    read_stream: MemoryObjectReceiveStream[Any],
    write_stream: MemoryObjectSendStream[Any],
    session_id: str,
    prompt: List[Content],
    *,
    timeout: float = 300.0,
    cancellation_token: Optional[CancellationToken] = None,
) -> PromptResult:
    """Send a prompt to the agent.

    The agent will send session/update notifications during processing.

    Args:
        read_stream: Stream to receive messages.
        write_stream: Stream to send messages.
        session_id: Session ID.
        prompt: List of content blocks forming the prompt.
        timeout: Request timeout in seconds (longer for AI processing).
        cancellation_token: Token to cancel the request.

    Returns:
        PromptResult with stop reason.

    Raises:
        Exception: If prompt fails.
    """
    params = {
        "sessionId": session_id,
        "prompt": [content.model_dump(exclude_none=True) for content in prompt],
    }

    result = await send_message(
        read_stream,
        write_stream,
        method=METHOD_SESSION_PROMPT,
        params=params,
        timeout=timeout,
        cancellation_token=cancellation_token,
    )

    return PromptResult(stopReason=result["stopReason"])


async def send_session_set_mode(
    read_stream: MemoryObjectReceiveStream[Any],
    write_stream: MemoryObjectSendStream[Any],
    session_id: str,
    mode: SessionMode,
    *,
    timeout: float = 60.0,
) -> Dict[str, Any]:
    """Set the session mode (requires modes capability).

    Args:
        read_stream: Stream to receive messages.
        write_stream: Stream to send messages.
        session_id: Session ID.
        mode: New mode (ask, architect, code).
        timeout: Request timeout in seconds.

    Returns:
        Set mode result.

    Raises:
        Exception: If setting mode fails.
    """
    params = {
        "sessionId": session_id,
        "mode": mode,
    }

    return await send_message(
        read_stream,
        write_stream,
        method=METHOD_SESSION_SET_MODE,
        params=params,
        timeout=timeout,
    )


async def send_session_cancel(
    write_stream: MemoryObjectSendStream[Any],
    session_id: str,
) -> None:
    """Cancel an ongoing prompt turn (notification).

    Args:
        write_stream: Stream to send messages.
        session_id: Session ID.
    """
    params = {"sessionId": session_id}

    await send_notification(
        write_stream,
        method=METHOD_SESSION_CANCEL,
        params=params,
    )


async def send_session_update(
    write_stream: MemoryObjectSendStream[Any],
    session_id: str,
    *,
    plan: Optional[Plan] = None,
    agent_message_chunk: Optional[Content] = None,
    user_message_chunk: Optional[Content] = None,
    thought: Optional[str] = None,
    tool_call: Optional[ToolCall] = None,
    tool_call_update: Optional[ToolCallUpdate] = None,
    available_commands_update: Optional[List[AvailableCommand]] = None,
) -> None:
    """Send session update notification from agent to client.

    Args:
        write_stream: Stream to send messages.
        session_id: Session ID.
        plan: Task plan.
        agent_message_chunk: Chunk of agent message.
        user_message_chunk: Chunk of user message (for history replay).
        thought: Agent thought process.
        tool_call: New tool call.
        tool_call_update: Update to existing tool call.
        available_commands_update: Update to available slash commands (optional).
    """
    params: Dict[str, Any] = {"sessionId": session_id}

    if plan:
        params["plan"] = plan.model_dump(exclude_none=True)
    if agent_message_chunk:
        params["agentMessageChunk"] = agent_message_chunk.model_dump(exclude_none=True)
    if user_message_chunk:
        params["userMessageChunk"] = user_message_chunk.model_dump(exclude_none=True)
    if thought:
        params["thought"] = thought
    if tool_call:
        params["toolCall"] = tool_call.model_dump(exclude_none=True)
    if tool_call_update:
        params["toolCallUpdate"] = tool_call_update.model_dump(exclude_none=True)
    if available_commands_update:
        params["availableCommandsUpdate"] = [
            cmd.model_dump(exclude_none=True) for cmd in available_commands_update
        ]

    await send_notification(
        write_stream,
        method=METHOD_SESSION_UPDATE,
        params=params,
    )


async def send_session_request_permission(
    read_stream: MemoryObjectReceiveStream[Any],
    write_stream: MemoryObjectSendStream[Any],
    session_id: str,
    request: PermissionRequest,
    *,
    timeout: float = 300.0,
) -> PermissionResponse:
    """Request permission from user (client method called by agent).

    Args:
        read_stream: Stream to receive messages.
        write_stream: Stream to send messages.
        session_id: Session ID.
        request: Permission request details.
        timeout: Request timeout in seconds (user interaction).

    Returns:
        PermissionResponse with granted status.

    Raises:
        Exception: If permission request fails.
    """
    params = {
        "sessionId": session_id,
        **request.model_dump(exclude_none=True),
    }

    result = await send_message(
        read_stream,
        write_stream,
        method=METHOD_SESSION_REQUEST_PERMISSION,
        params=params,
        timeout=timeout,
    )

    return PermissionResponse(
        id=result["id"],
        granted=result["granted"],
    )
