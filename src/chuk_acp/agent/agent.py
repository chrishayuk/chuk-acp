"""High-level API for building ACP agents."""

import json
import logging
import sys
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from chuk_acp.agent.models import AgentSession
from chuk_acp.protocol import (
    create_error_response,
    create_notification,
    create_response,
    METHOD_INITIALIZE,
    METHOD_SESSION_NEW,
    METHOD_SESSION_PROMPT,
    METHOD_SESSION_UPDATE,
    PROTOCOL_VERSION_CURRENT,
)
from chuk_acp.protocol.types import (
    AgentCapabilities,
    AgentInfo,
    Content,
    TextContent,
)

logger = logging.getLogger(__name__)


class ACPAgent(ABC):
    """Base class for building ACP agents.

    This provides a high-level API that handles all the protocol details,
    allowing you to focus on implementing your agent logic.

    Example:
        ```python
        from chuk_acp.agent import ACPAgent

        class MyAgent(ACPAgent):
            def get_agent_info(self) -> AgentInfo:
                return AgentInfo(
                    name="my-agent",
                    version="1.0.0",
                    title="My Agent"
                )

            async def handle_prompt(self, session: AgentSession, prompt: List[Content]) -> str:
                # Extract text from prompt
                text = prompt[0].get("text", "") if prompt else ""
                # Process and return response
                return f"You said: {text}"

        if __name__ == "__main__":
            agent = MyAgent()
            agent.run()
        ```
    """

    def __init__(self, log_file: Optional[str] = None):
        """Initialize the agent.

        Args:
            log_file: Optional log file path. If None, logs to stderr.
        """
        self.sessions: Dict[str, AgentSession] = {}
        self._setup_logging(log_file)

    def _setup_logging(self, log_file: Optional[str]) -> None:
        """Set up logging configuration."""
        if log_file:
            logging.basicConfig(
                level=logging.DEBUG,
                filename=log_file,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )
        else:
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )

    @abstractmethod
    def get_agent_info(self) -> AgentInfo:
        """Return agent information.

        Returns:
            AgentInfo with name, version, and optional title/description
        """
        pass

    def get_agent_capabilities(self) -> AgentCapabilities:
        """Return agent capabilities.

        Override to specify what your agent supports.

        Returns:
            AgentCapabilities describing what the agent can do
        """
        return AgentCapabilities()

    @abstractmethod
    async def handle_prompt(self, session: AgentSession, prompt: List[Content]) -> str:
        """Handle a prompt from the user.

        This is the main method you implement for your agent logic.

        Args:
            session: The current session
            prompt: List of content items (usually text)

        Returns:
            Response text to send back to the user
        """
        pass

    def send_message(self, text: str, session_id: str) -> None:
        """Send a message chunk to the client.

        Args:
            text: Text to send
            session_id: Session to send to
        """
        text_content = TextContent(text=text)
        # Build the update dict manually to ensure proper serialization
        update_dict = {
            "sessionUpdate": "agent_message_chunk",
            "content": text_content.model_dump(exclude_none=True),
        }
        update_notification = create_notification(
            method=METHOD_SESSION_UPDATE,
            params={
                "sessionId": session_id,
                "update": update_dict,
            },
        )
        self._write_message(update_notification.model_dump(exclude_none=True))

    def _write_message(self, message: Dict[str, Any]) -> None:
        """Write a message to stdout."""
        json_str = json.dumps(message)
        logger.debug(f"Writing to stdout: {json_str}")
        sys.stdout.write(json_str + "\n")
        sys.stdout.flush()
        logger.debug("Flushed stdout")

    def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize request."""
        logger.info(f"Initialize: {params}")

        agent_info = self.get_agent_info()
        agent_capabilities = self.get_agent_capabilities()

        # Get protocol version from params, handling both int and string formats
        client_protocol_version = params.get("protocolVersion", PROTOCOL_VERSION_CURRENT)

        # Validate and convert protocol version to integer
        # Some implementations incorrectly send date strings (like "2024-11-05") instead of integers
        try:
            if isinstance(client_protocol_version, str):
                logger.warning(
                    f"Client sent protocol version as string '{client_protocol_version}', "
                    f"defaulting to {PROTOCOL_VERSION_CURRENT}"
                )
                protocol_version = PROTOCOL_VERSION_CURRENT
            else:
                # Use the minimum of client and agent versions (version negotiation)
                protocol_version = min(int(client_protocol_version), PROTOCOL_VERSION_CURRENT)
        except (ValueError, TypeError) as e:
            logger.warning(
                f"Invalid protocol version '{client_protocol_version}': {e}, "
                f"defaulting to {PROTOCOL_VERSION_CURRENT}"
            )
            protocol_version = PROTOCOL_VERSION_CURRENT

        return {
            "protocolVersion": protocol_version,
            "agentInfo": agent_info.model_dump(exclude_none=True),
            "agentCapabilities": agent_capabilities.model_dump(exclude_none=True),
        }

    def _handle_session_new(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle session/new request."""
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        session = AgentSession(session_id=session_id, cwd=params.get("cwd"))
        self.sessions[session_id] = session

        logger.info(f"Created session: {session_id}")

        return {"sessionId": session_id}

    async def _handle_session_prompt(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle session/prompt request."""
        session_id = params["sessionId"]
        prompt = params["prompt"]

        logger.info(f"Prompt for {session_id}")

        if session_id not in self.sessions:
            raise Exception(f"Unknown session: {session_id}")

        session = self.sessions[session_id]

        # Call the user's handler
        response_text = await self.handle_prompt(session, prompt)

        # Send the response as a message chunk (if not empty)
        if response_text:
            self.send_message(response_text, session_id)

        # Return stop reason
        return {"stopReason": "end_turn"}

    async def _handle_message(self, message: Dict[str, Any]) -> None:
        """Handle incoming JSON-RPC message."""
        logger.debug(f"Received: {message}")

        method = message.get("method")
        params = message.get("params", {})
        msg_id = message.get("id", "")

        try:
            # Route to handler
            if method == METHOD_INITIALIZE:
                result = self._handle_initialize(params)
            elif method == METHOD_SESSION_NEW:
                result = self._handle_session_new(params)
            elif method == METHOD_SESSION_PROMPT:
                result = await self._handle_session_prompt(params)
            else:
                raise Exception(f"Unknown method: {method}")

            # Send response
            response = create_response(id=msg_id, result=result)
            self._write_message(response.model_dump(exclude_none=True))

        except Exception as e:
            logger.error(f"Error handling {method}: {e}", exc_info=True)

            # Send error response
            error_response = create_error_response(
                id=msg_id,
                code=-32603,
                message=str(e),
            )
            self._write_message(error_response.model_dump(exclude_none=True))

    def run(self) -> None:
        """Run the agent (read stdin, write stdout).

        This is the main entry point for your agent.
        Call this from __main__ to start the agent.
        """
        logger.info(f"{self.get_agent_info().name} started")

        try:
            # Use anyio to run async code
            import anyio

            anyio.run(self._run_async)

        except KeyboardInterrupt:
            logger.info("Agent interrupted")
        except Exception as e:
            logger.error(f"Agent error: {e}", exc_info=True)

        logger.info(f"{self.get_agent_info().name} stopped")

    async def _run_async(self) -> None:
        """Async run loop."""
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                message = json.loads(line)
                await self._handle_message(message)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)
