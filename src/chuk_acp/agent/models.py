"""Agent models."""

from typing import Any, Dict, Optional


class AgentSession:
    """Represents an agent session.

    Attributes:
        session_id: Unique session identifier
        cwd: Working directory for this session
        context: Dictionary for storing session-specific data
    """

    def __init__(self, session_id: str, cwd: Optional[str] = None):
        """Initialize session.

        Args:
            session_id: Unique session identifier
            cwd: Working directory for this session
        """
        self.session_id = session_id
        self.cwd = cwd
        self.context: Dict[str, Any] = {}
