"""ACP session types."""

from typing import Optional, Literal
from ..acp_pydantic_base import AcpPydanticBase, PYDANTIC_AVAILABLE

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
