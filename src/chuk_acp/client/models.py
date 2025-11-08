"""Data models for the ACP client."""

__all__ = ["SessionInfo", "SessionUpdate", "PromptResult"]

from typing import Any
from ..protocol import JSONRPCNotification


class SessionInfo:
    """Simple session information returned by session/new."""

    def __init__(self, sessionId: str) -> None:
        self.sessionId = sessionId


class SessionUpdate:
    """Represents a session update notification from the agent."""

    def __init__(self, notification: JSONRPCNotification) -> None:
        self.notification = notification
        params = notification.params or {}
        self.session_id = params.get("sessionId")

        # Extract agent message chunk
        chunk = params.get("agentMessageChunk")
        if chunk and isinstance(chunk, dict):
            self.agent_message = chunk.get("text")
        else:
            self.agent_message = None

        # Extract stop reason
        self.stop_reason = params.get("stopReason")


class PromptResult:
    """Result from sending a prompt, including response and all notifications."""

    def __init__(self, response: dict[str, Any], updates: list[SessionUpdate]) -> None:
        self.response = response
        self.updates = updates
        self.stop_reason = response.get("stopReason")

    @property
    def agent_messages(self) -> list[str]:
        """Extract all agent message texts from updates."""
        return [update.agent_message for update in self.updates if update.agent_message is not None]

    @property
    def full_message(self) -> str:
        """Concatenate all agent messages into a single string."""
        return "".join(self.agent_messages)
