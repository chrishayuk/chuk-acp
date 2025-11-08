"""ACP plan types."""

from typing import List, Literal
from ..acp_pydantic_base import AcpPydanticBase, PYDANTIC_AVAILABLE

if PYDANTIC_AVAILABLE:
    from ..acp_pydantic_base import ConfigDict


# Plan entry status enum
PlanEntryStatus = Literal["pending", "in_progress", "completed"]

# Plan entry priority enum
PlanEntryPriority = Literal["high", "medium", "low"]


class PlanEntry(AcpPydanticBase):
    """A single entry in an agent's execution plan."""

    content: str
    """Human-readable description of what this task aims to accomplish."""

    status: PlanEntryStatus
    """Current execution status of this task."""

    priority: PlanEntryPriority
    """The relative importance of this task."""

    if PYDANTIC_AVAILABLE:
        model_config = ConfigDict(extra="allow")


class Plan(AcpPydanticBase):
    """Agent's execution plan communicated via session/update.

    The plan shows how the agent intends to tackle multi-step tasks.
    Agents must send the complete list of all plan entries in each update.
    """

    entries: List[PlanEntry]
    """The list of tasks to be accomplished."""

    if PYDANTIC_AVAILABLE:
        model_config = ConfigDict(extra="allow")


# Legacy aliases for backward compatibility
Task = PlanEntry
TaskStatus = PlanEntryStatus
