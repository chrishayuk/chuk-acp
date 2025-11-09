"""ACP session types."""

from typing import Optional, Literal
from ..acp_pydantic_base import AcpPydanticBase, PYDANTIC_AVAILABLE
from .content import Content

if PYDANTIC_AVAILABLE:
    from ..acp_pydantic_base import ConfigDict


# Session mode enum
SessionMode = Literal["ask", "architect", "code"]


# Stop reason enum
StopReason = Literal[
    "end_turn",
    "max_tokens",
    "max_turn_requests",
    "refusal",
    "cancelled",
]


# Session update types
SessionUpdateType = Literal[
    "agent_message_chunk",
    "user_message_chunk",
    "plan",
    "thought",
    "tool_call",
    "tool_call_update",
    "available_commands_update",
]


class SessionUpdate(AcpPydanticBase):
    """Session update wrapper for all update types."""

    sessionUpdate: SessionUpdateType
    """Type of session update."""

    content: Optional[Content] = None
    """Content for message chunks (agent_message_chunk or user_message_chunk)."""

    if PYDANTIC_AVAILABLE:
        model_config = ConfigDict(extra="allow")


class Location(AcpPydanticBase):
    """File location for 'follow-along' features."""

    path: str
    """Absolute file path. All file paths in ACP MUST be absolute."""

    line: Optional[int] = None
    """Line number (1-indexed, as per ACP spec)."""

    column: Optional[int] = None
    """Column number."""

    if PYDANTIC_AVAILABLE:
        model_config = ConfigDict(extra="allow")
