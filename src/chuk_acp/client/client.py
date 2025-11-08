"""High-level ACPClient for simplified agent interaction."""

__all__ = ["ACPClient"]

import uuid
from typing import Any, Optional, Union
from pathlib import Path
import anyio
from anyio.streams.memory import (
    MemoryObjectReceiveStream,
    MemoryObjectSendStream,
)

from ..protocol import (
    create_request,
    METHOD_INITIALIZE,
    METHOD_SESSION_NEW,
    METHOD_SESSION_PROMPT,
    JSONRPCNotification,
    JSONRPCResponse,
    JSONRPCRequest,
    JSONRPCError,
)
from ..protocol.types import (
    AgentInfo,
    ClientInfo,
    TextContent,
    Content,
)
from ..transport.stdio import StdioTransport, StdioParameters
from .models import SessionInfo, SessionUpdate, PromptResult
from .config import AgentConfig


class ACPClient:
    """
    High-level client for ACP agents.

    This client handles all protocol ceremony automatically:
    - Initialization and capability negotiation
    - Session creation and management
    - Notification capture
    - Request/response handling

    Example:
        ```python
        async with ACPClient("python", ["agent.py"]) as client:
            result = await client.send_prompt("Hello!")
            print(f"Agent: {result.full_message}")
        ```
    """

    def __init__(
        self,
        command: str,
        args: Optional[list[str]] = None,
        env: Optional[dict[str, str]] = None,
        client_info: Optional[ClientInfo] = None,
        cwd: Optional[str | Path] = None,
    ) -> None:
        """
        Initialize the ACP client.

        Args:
            command: Command to run the agent (e.g., "python", "kimi")
            args: Arguments to pass to the command (e.g., ["agent.py", "--acp"])
            env: Environment variables for the agent process
            client_info: Optional client information for initialization
            cwd: Optional working directory for sessions (defaults to current directory)
        """
        self.command = command
        self.args = args or []
        self.env = env or {}
        self.client_info = client_info or ClientInfo(
            name="chuk-acp-client",
            version="0.1.0",
        )
        self.default_cwd = str(Path(cwd or Path.cwd()).absolute())

        # Will be set during context manager entry
        self._transport: Optional[StdioTransport] = None
        self._read_stream: Optional[
            MemoryObjectReceiveStream[Union[JSONRPCResponse, JSONRPCError, JSONRPCNotification]]
        ] = None
        self._write_stream: Optional[
            MemoryObjectSendStream[Union[JSONRPCRequest, JSONRPCNotification]]
        ] = None
        self._agent_info: Optional[AgentInfo] = None
        self._current_session: Optional[SessionInfo] = None

    @classmethod
    def from_config(
        cls,
        config: AgentConfig,
        client_info: Optional[ClientInfo] = None,
    ) -> "ACPClient":
        """
        Create an ACPClient from an AgentConfig.

        This matches the standard ACP configuration format used by editors.

        Args:
            config: Agent configuration (command, args, env, cwd)
            client_info: Optional client information

        Returns:
            ACPClient instance

        Example:
            ```python
            # From dictionary
            config = AgentConfig(
                command="kimi",
                args=["--acp"],
                env={"DEBUG": "true"}
            )
            async with ACPClient.from_config(config) as client:
                result = await client.send_prompt("Hello!")

            # From JSON file
            from chuk_acp.client import load_agent_config
            config = load_agent_config("~/.config/my-app/agent.json")
            async with ACPClient.from_config(config) as client:
                result = await client.send_prompt("Hello!")
            ```
        """
        return cls(
            command=config.command,
            args=config.args,
            env=config.env,
            client_info=client_info,
            cwd=config.cwd,
        )

    async def __aenter__(self) -> "ACPClient":
        """Start the agent and initialize the protocol."""
        # Create and start the transport
        params = StdioParameters(
            command=self.command,
            args=self.args,
            env=self.env if self.env else None,
        )
        self._transport = StdioTransport(params)
        await self._transport.__aenter__()

        # Get the streams
        self._read_stream, self._write_stream = await self._transport.get_streams()

        # Initialize the protocol
        init_request = create_request(
            method=METHOD_INITIALIZE,
            params={
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": self.client_info.model_dump(exclude_none=True),
            },
            id=str(uuid.uuid4()),
        )
        await self._write_stream.send(init_request)

        # Wait for initialize response
        response = await self._read_stream.receive()
        if isinstance(response, JSONRPCError):
            raise RuntimeError(f"Initialization failed: {response.error}")

        if not isinstance(response, JSONRPCResponse):
            raise RuntimeError(f"Expected JSONRPCResponse, got {type(response)}")

        # Parse agent info from result
        result = response.result or {}
        agent_info_dict = result.get("agentInfo", {})
        self._agent_info = AgentInfo(**agent_info_dict)

        # Create default session
        await self._create_session()

        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Clean up resources."""
        if self._transport:
            await self._transport.__aexit__(exc_type, exc_val, exc_tb)

    async def _create_session(self, cwd: Optional[str] = None) -> SessionInfo:
        """Create a new session."""
        if not self._write_stream or not self._read_stream:
            raise RuntimeError("Client not initialized")

        session_request = create_request(
            method=METHOD_SESSION_NEW,
            params={"cwd": cwd or self.default_cwd},
            id=str(uuid.uuid4()),
        )
        await self._write_stream.send(session_request)

        response = await self._read_stream.receive()
        if isinstance(response, JSONRPCError):
            raise RuntimeError(f"Session creation failed: {response.error}")

        if not isinstance(response, JSONRPCResponse):
            raise RuntimeError(f"Expected JSONRPCResponse, got {type(response)}")

        result = response.result or {}
        session_id = result.get("sessionId")
        if not session_id:
            raise RuntimeError("Session creation did not return sessionId")

        self._current_session = SessionInfo(sessionId=session_id)
        return self._current_session

    async def send_prompt(
        self,
        prompt: str | list[Content],
        timeout: float = 60.0,
    ) -> PromptResult:
        """
        Send a prompt to the agent and wait for the complete response.

        This method handles all the complexity of:
        - Creating the prompt request
        - Capturing session update notifications
        - Waiting for the final response
        - Extracting agent messages and stop reason

        Args:
            prompt: The prompt to send (string or list of Content objects)
            timeout: Maximum time to wait for response in seconds

        Returns:
            PromptResult containing the response and all notifications

        Raises:
            RuntimeError: If client not initialized or no active session
            TimeoutError: If response not received within timeout
        """
        if not self._current_session or not self._write_stream or not self._read_stream:
            raise RuntimeError("Client not initialized or no active session")

        # Convert string prompt to TextContent
        if isinstance(prompt, str):
            prompt_content = [TextContent(text=prompt).model_dump(exclude_none=True)]
        else:
            prompt_content = [c.model_dump(exclude_none=True) for c in prompt]

        # Send prompt request
        request = create_request(
            method=METHOD_SESSION_PROMPT,
            params={
                "sessionId": self._current_session.sessionId,
                "prompt": prompt_content,
            },
            id=str(uuid.uuid4()),
        )
        await self._write_stream.send(request)

        # Collect notifications and wait for response
        updates: list[SessionUpdate] = []
        response_result: Optional[dict[str, Any]] = None

        with anyio.fail_after(timeout):
            while response_result is None:
                message = await self._read_stream.receive()

                if isinstance(message, JSONRPCNotification):
                    # Capture session update
                    updates.append(SessionUpdate(message))
                elif isinstance(message, JSONRPCError):
                    # Error response
                    raise RuntimeError(f"Prompt failed: {message.error}")
                elif isinstance(message, JSONRPCResponse):
                    # Got final response
                    response_result = message.result or {}

        return PromptResult(response_result, updates)

    @property
    def agent_info(self) -> Optional[AgentInfo]:
        """Get information about the connected agent."""
        return self._agent_info

    @property
    def current_session(self) -> Optional[SessionInfo]:
        """Get the current session information."""
        return self._current_session

    async def new_session(self, cwd: Optional[str] = None) -> SessionInfo:
        """
        Create a new session.

        Note: The ACP protocol doesn't have an explicit session end method,
        so this just creates a new session. The old session will be
        implicitly abandoned.

        Args:
            cwd: Optional working directory for the new session

        Returns:
            The new session information
        """
        return await self._create_session(cwd)
