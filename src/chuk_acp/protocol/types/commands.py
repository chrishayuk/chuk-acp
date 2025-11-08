"""ACP slash command types (optional feature)."""

from typing import Optional
from ..acp_pydantic_base import AcpPydanticBase, PYDANTIC_AVAILABLE

if PYDANTIC_AVAILABLE:
    from ..acp_pydantic_base import ConfigDict


class AvailableCommandInput(AcpPydanticBase):
    """Input specification for a command.

    Currently supports only text input - all text typed after the command name
    is provided as input to the command.
    """

    hint: str
    """A hint to display when the input hasn't been provided yet."""

    if PYDANTIC_AVAILABLE:
        model_config = ConfigDict(extra="allow")


class AvailableCommand(AcpPydanticBase):
    """Information about an available slash command.

    Slash commands allow agents to advertise special commands that users can invoke
    by typing "/" followed by the command name (e.g., /web, /create_plan).
    """

    name: str
    """Command name (e.g., 'create_plan', 'research_codebase')."""

    description: str
    """Human-readable description of what the command does."""

    input: Optional[AvailableCommandInput] = None
    """Optional input specification if the command accepts arguments."""

    if PYDANTIC_AVAILABLE:
        model_config = ConfigDict(extra="allow")
