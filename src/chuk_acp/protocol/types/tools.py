"""ACP tool call types."""

from typing import Optional, List, Dict, Any, Literal
from ..acp_pydantic_base import AcpPydanticBase, PYDANTIC_AVAILABLE
from .session import Location
from .content import Content

if PYDANTIC_AVAILABLE:
    from ..acp_pydantic_base import ConfigDict


# Tool call status enum
ToolCallStatus = Literal["pending", "in_progress", "completed", "failed"]


class ToolCall(AcpPydanticBase):
    """Tool call information sent in session/update notifications."""

    id: str
    """Unique tool call identifier."""

    name: str
    """Tool name."""

    arguments: Dict[str, Any]
    """Tool arguments."""

    status: ToolCallStatus = "pending"
    """Current status."""

    location: Optional[Location] = None
    """File location being modified (for 'follow-along' features)."""

    if PYDANTIC_AVAILABLE:
        model_config = ConfigDict(extra="allow")


class ToolCallUpdate(AcpPydanticBase):
    """Update to an existing tool call."""

    id: str
    """Tool call ID to update."""

    status: Optional[ToolCallStatus] = None
    """New status."""

    result: Optional[List[Content]] = None
    """Tool execution result."""

    error: Optional[str] = None
    """Error message if failed."""

    location: Optional[Location] = None
    """Updated location."""

    if PYDANTIC_AVAILABLE:
        model_config = ConfigDict(extra="allow")
