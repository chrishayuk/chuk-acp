"""Tests for client models."""

from chuk_acp.client.models import SessionInfo, SessionUpdate, PromptResult
from chuk_acp.protocol import create_notification, METHOD_SESSION_UPDATE


class TestSessionInfo:
    """Test SessionInfo model."""

    def test_creation(self):
        """Test creating SessionInfo."""
        session = SessionInfo(sessionId="session-123")
        assert session.sessionId == "session-123"

    def test_different_session_ids(self):
        """Test multiple sessions with different IDs."""
        session1 = SessionInfo(sessionId="session-1")
        session2 = SessionInfo(sessionId="session-2")
        assert session1.sessionId != session2.sessionId


class TestSessionUpdate:
    """Test SessionUpdate model."""

    def test_creation_with_agent_message(self):
        """Test creating SessionUpdate with agent message."""
        notification = create_notification(
            method=METHOD_SESSION_UPDATE,
            params={
                "sessionId": "session-123",
                "agentMessageChunk": {"text": "Hello from agent", "type": "text"},
            },
        )
        update = SessionUpdate(notification)
        assert update.session_id == "session-123"
        assert update.agent_message == "Hello from agent"
        assert update.stop_reason is None

    def test_creation_with_stop_reason(self):
        """Test creating SessionUpdate with stop reason."""
        notification = create_notification(
            method=METHOD_SESSION_UPDATE,
            params={
                "sessionId": "session-123",
                "stopReason": "end_turn",
            },
        )
        update = SessionUpdate(notification)
        assert update.session_id == "session-123"
        assert update.agent_message is None
        assert update.stop_reason == "end_turn"

    def test_creation_with_both(self):
        """Test creating SessionUpdate with both message and stop reason."""
        notification = create_notification(
            method=METHOD_SESSION_UPDATE,
            params={
                "sessionId": "session-123",
                "agentMessageChunk": {"text": "Done!", "type": "text"},
                "stopReason": "end_turn",
            },
        )
        update = SessionUpdate(notification)
        assert update.session_id == "session-123"
        assert update.agent_message == "Done!"
        assert update.stop_reason == "end_turn"

    def test_creation_without_params(self):
        """Test creating SessionUpdate with empty params."""
        notification = create_notification(
            method=METHOD_SESSION_UPDATE,
            params={},
        )
        update = SessionUpdate(notification)
        assert update.session_id is None
        assert update.agent_message is None
        assert update.stop_reason is None

    def test_chunk_without_text(self):
        """Test handling chunk without text field."""
        notification = create_notification(
            method=METHOD_SESSION_UPDATE,
            params={
                "sessionId": "session-123",
                "agentMessageChunk": {"type": "text"},  # No text field
            },
        )
        update = SessionUpdate(notification)
        assert update.session_id == "session-123"
        assert update.agent_message is None

    def test_chunk_as_non_dict(self):
        """Test handling chunk as non-dictionary."""
        notification = create_notification(
            method=METHOD_SESSION_UPDATE,
            params={
                "sessionId": "session-123",
                "agentMessageChunk": "not a dict",
            },
        )
        update = SessionUpdate(notification)
        assert update.agent_message is None


class TestPromptResult:
    """Test PromptResult model."""

    def test_creation(self):
        """Test creating PromptResult."""
        response = {"stopReason": "end_turn", "sessionId": "session-123"}
        updates = []
        result = PromptResult(response, updates)
        assert result.response == response
        assert result.updates == updates
        assert result.stop_reason == "end_turn"

    def test_agent_messages_property(self):
        """Test extracting agent messages."""
        notification1 = create_notification(
            method=METHOD_SESSION_UPDATE,
            params={
                "sessionId": "session-123",
                "agentMessageChunk": {"text": "Hello", "type": "text"},
            },
        )
        notification2 = create_notification(
            method=METHOD_SESSION_UPDATE,
            params={
                "sessionId": "session-123",
                "agentMessageChunk": {"text": " world!", "type": "text"},
            },
        )

        updates = [SessionUpdate(notification1), SessionUpdate(notification2)]
        response = {"stopReason": "end_turn"}
        result = PromptResult(response, updates)

        messages = result.agent_messages
        assert len(messages) == 2
        assert messages[0] == "Hello"
        assert messages[1] == " world!"

    def test_full_message_property(self):
        """Test concatenating full message."""
        notification1 = create_notification(
            method=METHOD_SESSION_UPDATE,
            params={
                "sessionId": "session-123",
                "agentMessageChunk": {"text": "Hello", "type": "text"},
            },
        )
        notification2 = create_notification(
            method=METHOD_SESSION_UPDATE,
            params={
                "sessionId": "session-123",
                "agentMessageChunk": {"text": " world!", "type": "text"},
            },
        )

        updates = [SessionUpdate(notification1), SessionUpdate(notification2)]
        response = {"stopReason": "end_turn"}
        result = PromptResult(response, updates)

        assert result.full_message == "Hello world!"

    def test_empty_updates(self):
        """Test with no updates."""
        response = {"stopReason": "end_turn"}
        result = PromptResult(response, [])

        assert result.agent_messages == []
        assert result.full_message == ""

    def test_mixed_updates(self):
        """Test with some updates having messages, some not."""
        notification1 = create_notification(
            method=METHOD_SESSION_UPDATE,
            params={
                "sessionId": "session-123",
                "agentMessageChunk": {"text": "Hello", "type": "text"},
            },
        )
        notification2 = create_notification(
            method=METHOD_SESSION_UPDATE,
            params={
                "sessionId": "session-123",
                "stopReason": "end_turn",  # No message
            },
        )
        notification3 = create_notification(
            method=METHOD_SESSION_UPDATE,
            params={
                "sessionId": "session-123",
                "agentMessageChunk": {"text": "!", "type": "text"},
            },
        )

        updates = [
            SessionUpdate(notification1),
            SessionUpdate(notification2),
            SessionUpdate(notification3),
        ]
        response = {"stopReason": "end_turn"}
        result = PromptResult(response, updates)

        assert result.agent_messages == ["Hello", "!"]
        assert result.full_message == "Hello!"

    def test_stop_reason_from_response(self):
        """Test stop reason is extracted from response."""
        response = {"stopReason": "max_tokens", "sessionId": "session-123"}
        result = PromptResult(response, [])
        assert result.stop_reason == "max_tokens"

    def test_no_stop_reason(self):
        """Test when response has no stop reason."""
        response = {"sessionId": "session-123"}
        result = PromptResult(response, [])
        assert result.stop_reason is None
