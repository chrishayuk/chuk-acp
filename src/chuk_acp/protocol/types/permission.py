"""ACP permission types."""

from typing import Optional, Dict, Any
from ..acp_pydantic_base import AcpPydanticBase, PYDANTIC_AVAILABLE

if PYDANTIC_AVAILABLE:
    from ..acp_pydantic_base import ConfigDict


class PermissionRequest(AcpPydanticBase):
    """Request for user permission to execute an action."""

    id: str
    """Unique permission request identifier."""

    action: str
    """Action requiring permission (e.g., 'execute_tool', 'write_file')."""

    description: str
    """Human-readable description of what will happen."""

    details: Optional[Dict[str, Any]] = None
    """Additional details about the action."""

    if PYDANTIC_AVAILABLE:
        model_config = ConfigDict(extra="allow")


class PermissionResponse(AcpPydanticBase):
    """Response to a permission request."""

    id: str
    """Permission request ID."""

    granted: bool
    """Whether permission was granted."""

    if PYDANTIC_AVAILABLE:
        model_config = ConfigDict(extra="allow")
