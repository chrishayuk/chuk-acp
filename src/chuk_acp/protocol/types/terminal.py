"""ACP terminal types."""

from typing import Optional, List, Dict, Literal
from ..acp_pydantic_base import AcpPydanticBase, PYDANTIC_AVAILABLE

if PYDANTIC_AVAILABLE:
    from ..acp_pydantic_base import ConfigDict


class TerminalInfo(AcpPydanticBase):
    """Information about a terminal session."""

    id: str
    """Terminal session ID."""

    command: str
    """Command being executed."""

    args: Optional[List[str]] = None
    """Command arguments."""

    cwd: Optional[str] = None
    """Working directory (absolute path)."""

    env: Optional[Dict[str, str]] = None
    """Environment variables."""

    if PYDANTIC_AVAILABLE:
        model_config = ConfigDict(extra="allow")


class TerminalOutput(AcpPydanticBase):
    """Terminal output data."""

    id: str
    """Terminal session ID."""

    output: str
    """Output text."""

    stream: Literal["stdout", "stderr"] = "stdout"
    """Output stream."""

    if PYDANTIC_AVAILABLE:
        model_config = ConfigDict(extra="allow")


class TerminalExit(AcpPydanticBase):
    """Terminal exit information."""

    id: str
    """Terminal session ID."""

    exitCode: int
    """Process exit code."""

    if PYDANTIC_AVAILABLE:
        model_config = ConfigDict(extra="allow")
