"""ACP agent and client information types."""

from typing import Optional
from ..acp_pydantic_base import AcpPydanticBase, PYDANTIC_AVAILABLE

if PYDANTIC_AVAILABLE:
    from ..acp_pydantic_base import ConfigDict


class AgentInfo(AcpPydanticBase):
    """Information about the agent implementation."""

    name: str
    """The programmatic name of the agent."""

    version: str
    """Version of the agent implementation."""

    title: Optional[str] = None
    """
    Human-readable title for UI contexts.
    If not provided, the name should be used for display.
    """

    if PYDANTIC_AVAILABLE:
        model_config = ConfigDict(extra="allow")


class ClientInfo(AcpPydanticBase):
    """Information about the client (editor) implementation."""

    name: str
    """The programmatic name of the client."""

    version: str
    """Version of the client implementation."""

    title: Optional[str] = None
    """
    Human-readable title for UI contexts.
    If not provided, the name should be used for display.
    """

    if PYDANTIC_AVAILABLE:
        model_config = ConfigDict(extra="allow")
