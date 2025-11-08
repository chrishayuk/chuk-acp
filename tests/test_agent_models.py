"""Tests for agent models."""

from chuk_acp.agent.models import AgentSession


class TestAgentSession:
    """Test AgentSession model."""

    def test_session_creation_with_session_id_only(self):
        """Test creating session with just session_id."""
        session = AgentSession(session_id="test-session-123")

        assert session.session_id == "test-session-123"
        assert session.cwd is None
        assert session.context == {}

    def test_session_creation_with_cwd(self):
        """Test creating session with cwd."""
        session = AgentSession(session_id="test-session-456", cwd="/tmp/test")

        assert session.session_id == "test-session-456"
        assert session.cwd == "/tmp/test"
        assert session.context == {}

    def test_session_context_is_mutable_dict(self):
        """Test that context can store arbitrary data."""
        session = AgentSession(session_id="test-session-789")

        # Context should start empty
        assert session.context == {}

        # Should be able to add data
        session.context["user_data"] = {"name": "Alice"}
        session.context["counter"] = 42

        assert session.context["user_data"] == {"name": "Alice"}
        assert session.context["counter"] == 42

    def test_multiple_sessions_have_independent_context(self):
        """Test that different sessions have independent contexts."""
        session1 = AgentSession(session_id="session-1")
        session2 = AgentSession(session_id="session-2")

        session1.context["data"] = "session1-data"
        session2.context["data"] = "session2-data"

        assert session1.context["data"] == "session1-data"
        assert session2.context["data"] == "session2-data"

    def test_session_attributes_are_accessible(self):
        """Test that all session attributes are accessible."""
        session = AgentSession(session_id="test-session", cwd="/home/user/project")

        # All attributes should be accessible
        assert hasattr(session, "session_id")
        assert hasattr(session, "cwd")
        assert hasattr(session, "context")

        # And have correct values
        assert session.session_id == "test-session"
        assert session.cwd == "/home/user/project"
        assert isinstance(session.context, dict)
