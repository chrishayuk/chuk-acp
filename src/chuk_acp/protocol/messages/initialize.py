"""ACP initialization messages."""

from typing import Optional, Dict, Any
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream

from .send_message import send_message
from ..constants import METHOD_INITIALIZE, METHOD_AUTHENTICATE
from ..types import AgentInfo, ClientInfo, AgentCapabilities, ClientCapabilities


class InitializeResult:
    """Result of initialize request."""

    def __init__(
        self,
        protocolVersion: int,
        agentInfo: AgentInfo,
        capabilities: AgentCapabilities,
    ):
        self.protocolVersion = protocolVersion
        self.agentInfo = agentInfo
        self.capabilities = capabilities


async def send_initialize(
    read_stream: MemoryObjectReceiveStream[Any],
    write_stream: MemoryObjectSendStream[Any],
    protocol_version: int,
    client_info: ClientInfo,
    capabilities: ClientCapabilities,
    *,
    timeout: float = 60.0,
) -> InitializeResult:
    """Send initialize request to agent.

    Args:
        read_stream: Stream to receive messages.
        write_stream: Stream to send messages.
        protocol_version: Protocol version client supports (latest).
        client_info: Information about the client.
        capabilities: Client capabilities.
        timeout: Request timeout in seconds.

    Returns:
        InitializeResult with negotiated protocol version, agent info, and capabilities.

    Raises:
        Exception: If initialization fails.
    """
    params = {
        "protocolVersion": protocol_version,
        "clientInfo": client_info.model_dump(exclude_none=True),
        "clientCapabilities": capabilities.model_dump(exclude_none=True),
    }

    result = await send_message(
        read_stream,
        write_stream,
        method=METHOD_INITIALIZE,
        params=params,
        timeout=timeout,
    )

    # Parse result
    agent_info = AgentInfo.model_validate(result["agentInfo"])
    agent_capabilities = AgentCapabilities.model_validate(result.get("agentCapabilities", {}))

    return InitializeResult(
        protocolVersion=result["protocolVersion"],
        agentInfo=agent_info,
        capabilities=agent_capabilities,
    )


async def send_authenticate(
    read_stream: MemoryObjectReceiveStream[Any],
    write_stream: MemoryObjectSendStream[Any],
    token: Optional[str] = None,
    credentials: Optional[Dict[str, Any]] = None,
    *,
    timeout: float = 60.0,
) -> Dict[str, Any]:
    """Send authenticate request to agent (optional).

    Args:
        read_stream: Stream to receive messages.
        write_stream: Stream to send messages.
        token: Authentication token.
        credentials: Authentication credentials.
        timeout: Request timeout in seconds.

    Returns:
        Authentication result.

    Raises:
        Exception: If authentication fails.
    """
    params: Dict[str, Any] = {}
    if token:
        params["token"] = token
    if credentials:
        params["credentials"] = credentials

    return await send_message(
        read_stream,
        write_stream,
        method=METHOD_AUTHENTICATE,
        params=params,
        timeout=timeout,
    )
