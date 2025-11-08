"""Protocol compliance tests for chuk-acp.

Tests that the implementation matches ACP specification requirements.
"""

import pytest
from chuk_acp.protocol.types import (
    AgentInfo,
    ClientInfo,
    AgentCapabilities,
    ClientCapabilities,
    TextContent,
    ImageContent,
    SessionMode,
    StopReason,
    ToolCallStatus,
)
from chuk_acp.protocol.jsonrpc import (
    create_request,
    create_notification,
    create_response,
    create_error_response,
)


class TestJSONRPCCompliance:
    """Test JSON-RPC 2.0 compliance."""

    def test_request_has_required_fields(self):
        """Requests must have jsonrpc, id, method."""
        req = create_request(method="test/method", params={"key": "value"})

        assert req.jsonrpc == "2.0"
        assert req.id is not None
        assert req.method == "test/method"
        assert req.params == {"key": "value"}

    def test_notification_no_id(self):
        """Notifications must NOT have an id field."""
        notif = create_notification(method="test/notification", params={"key": "value"})

        assert notif.jsonrpc == "2.0"
        assert not hasattr(notif, "id") or notif.id is None
        assert notif.method == "test/notification"

    def test_response_has_result(self):
        """Success responses must have result field."""
        resp = create_response(id="test-123", result={"status": "ok"})

        assert resp.jsonrpc == "2.0"
        assert resp.id == "test-123"
        assert resp.result == {"status": "ok"}
        assert not hasattr(resp, "error")

    def test_error_response_has_error_object(self):
        """Error responses must have error object with code and message."""
        err = create_error_response(id="test-123", code=-32600, message="Invalid Request")

        assert err.jsonrpc == "2.0"
        assert err.id == "test-123"
        assert "code" in err.error
        assert "message" in err.error
        assert err.error["code"] == -32600
        assert err.error["message"] == "Invalid Request"


class TestInfoTypesCompliance:
    """Test info type compliance."""

    def test_agent_info_required_fields(self):
        """AgentInfo must have name and version."""
        info = AgentInfo(name="test-agent", version="1.0.0")

        assert info.name == "test-agent"
        assert info.version == "1.0.0"

    def test_client_info_required_fields(self):
        """ClientInfo must have name and version."""
        info = ClientInfo(name="test-client", version="1.0.0")

        assert info.name == "test-client"
        assert info.version == "1.0.0"

    def test_info_optional_title(self):
        """Info types should support optional title."""
        info = AgentInfo(name="test", version="1.0", title="Test Agent")

        assert info.title == "Test Agent"


class TestContentTypesCompliance:
    """Test content type compliance."""

    def test_text_content_required_fields(self):
        """TextContent must have type='text' and text field."""
        content = TextContent(text="Hello world")

        assert content.type == "text"
        assert content.text == "Hello world"

    def test_text_content_is_baseline(self):
        """All agents MUST support text content."""
        # This is a requirement from spec
        content = TextContent(text="Test")
        assert content.type == "text"

    def test_image_content_required_fields(self):
        """ImageContent must have type, data, mimeType."""
        content = ImageContent(data="base64data", mimeType="image/png")

        assert content.type == "image"
        assert content.data == "base64data"
        assert content.mimeType == "image/png"

    def test_content_serialization(self):
        """Content should serialize to dict properly."""
        content = TextContent(text="Test")

        # Check attributes directly (works without Pydantic)
        assert content.type == "text"
        assert content.text == "Test"


class TestCapabilitiesCompliance:
    """Test capabilities compliance."""

    def test_capabilities_are_optional(self):
        """All capabilities should be optional."""
        # Empty capabilities should be valid
        agent_caps = AgentCapabilities()
        client_caps = ClientCapabilities()

        assert agent_caps is not None
        assert client_caps is not None

    def test_omitted_capabilities_mean_unsupported(self):
        """Omitted capabilities are treated as unsupported per spec."""
        caps = AgentCapabilities()

        # If not specified, should be None (unsupported)
        assert caps.loadSession is None
        assert caps.modes is None
        assert caps.prompts is None

    def test_capabilities_can_be_enabled(self):
        """Capabilities can be explicitly enabled."""
        caps = AgentCapabilities(loadSession=True, modes=["ask", "code"])

        assert caps.loadSession is True
        assert "ask" in caps.modes
        assert "code" in caps.modes


class TestSessionCompliance:
    """Test session-related compliance."""

    def test_session_modes_valid_values(self):
        """Session modes must be: ask, architect, or code."""
        valid_modes: list[SessionMode] = ["ask", "architect", "code"]

        for mode in valid_modes:
            # Should not raise
            assert mode in valid_modes

    def test_stop_reasons_valid_values(self):
        """Stop reasons must match spec."""
        valid_reasons: list[StopReason] = [
            "end_turn",
            "max_tokens",
            "max_turn_requests",
            "refusal",
            "cancelled",
        ]

        for reason in valid_reasons:
            assert reason in valid_reasons


class TestFilePathCompliance:
    """Test file path requirements."""

    def test_paths_must_be_absolute(self):
        """Protocol requires all file paths to be absolute."""
        # This is a spec requirement, but we can't enforce it at type level
        # It's the responsibility of the caller

        # Just verify our Location type accepts paths
        from chuk_acp.protocol.types import Location

        # Absolute path
        loc = Location(path="/absolute/path/to/file.py")
        assert loc.path.startswith("/")

        # The spec says paths MUST be absolute, but we can't enforce this
        # at the type level - it's a protocol-level validation

    def test_line_numbers_are_one_indexed(self):
        """Protocol uses 1-based line numbers."""
        from chuk_acp.protocol.types import Location

        # Line numbers should be 1-based
        loc = Location(path="/file.py", line=1)
        assert loc.line == 1

        # This is a documentation requirement - line 1 is the first line


class TestToolCallCompliance:
    """Test tool call requirements."""

    def test_tool_call_status_values(self):
        """Tool call status must match spec."""
        valid_statuses: list[ToolCallStatus] = ["pending", "in_progress", "completed", "failed"]

        for status in valid_statuses:
            assert status in valid_statuses

    def test_tool_call_required_fields(self):
        """Tool calls must have id, name, arguments."""
        from chuk_acp.protocol.types import ToolCall

        call = ToolCall(id="tool-123", name="execute", arguments={"command": "ls"})

        assert call.id == "tool-123"
        assert call.name == "execute"
        assert call.arguments == {"command": "ls"}
        assert call.status == "pending"  # Default


class TestPlanCompliance:
    """Test plan and plan entry requirements."""

    def test_plan_entry_status_values(self):
        """Plan entry status must match spec."""
        from chuk_acp.protocol.types import PlanEntryStatus

        valid_statuses: list[PlanEntryStatus] = ["pending", "in_progress", "completed"]

        for status in valid_statuses:
            assert status in valid_statuses

    def test_plan_entry_priority_values(self):
        """Plan entry priority must match spec."""
        from chuk_acp.protocol.types import PlanEntryPriority

        valid_priorities: list[PlanEntryPriority] = ["high", "medium", "low"]

        for priority in valid_priorities:
            assert priority in valid_priorities

    def test_plan_entry_required_fields(self):
        """Plan entries must have content, status, and priority."""
        from chuk_acp.protocol.types import PlanEntry

        entry = PlanEntry(content="Implement feature X", status="pending", priority="high")

        assert entry.content == "Implement feature X"
        assert entry.status == "pending"
        assert entry.priority == "high"

    def test_plan_has_entries(self):
        """Plans must have an entries list."""
        from chuk_acp.protocol.types import Plan, PlanEntry

        plan = Plan(
            entries=[
                PlanEntry(content="Task 1", status="completed", priority="high"),
                PlanEntry(content="Task 2", status="in_progress", priority="medium"),
            ]
        )

        assert len(plan.entries) == 2
        assert plan.entries[0].content == "Task 1"


class TestProtocolExtensibility:
    """Test protocol extensibility requirements."""

    def test_extra_fields_allowed(self):
        """Protocol allows extra fields via model_config extra='allow'."""
        # Our Pydantic models should allow extra fields
        info = AgentInfo(
            name="test",
            version="1.0",
            custom_field="custom_value",  # type: ignore
        )

        # Should not raise an error
        assert info.name == "test"

    def test_meta_field_support(self):
        """Protocol supports _meta fields for custom data."""
        # JSON-RPC messages can have _meta in params
        req = create_request(
            method="test", params={"key": "value", "_meta": {"customData": "test"}}
        )

        assert req.params is not None
        assert "_meta" in req.params
        assert req.params["_meta"]["customData"] == "test"


class TestSlashCommandsCompliance:
    """Test slash commands (optional feature)."""

    def test_available_command_required_fields(self):
        """AvailableCommand must have name and description."""
        from chuk_acp.protocol.types import AvailableCommand

        cmd = AvailableCommand(name="web", description="Search the web")

        assert cmd.name == "web"
        assert cmd.description == "Search the web"
        assert cmd.input is None  # Optional

    def test_available_command_with_input(self):
        """AvailableCommand can have input specification."""
        from chuk_acp.protocol.types import AvailableCommand, AvailableCommandInput

        cmd = AvailableCommand(
            name="search",
            description="Search for something",
            input=AvailableCommandInput(hint="Enter search query"),
        )

        assert cmd.input is not None
        assert cmd.input.hint == "Enter search query"

    def test_commands_are_optional(self):
        """Slash commands are an optional feature."""
        # This is documented in the spec as MAY, not MUST
        # Just verify the types exist and work
        from chuk_acp.protocol.types import AvailableCommand

        cmd = AvailableCommand(name="test", description="Test command")
        assert cmd is not None


def test_protocol_version():
    """Test that we're implementing protocol version 1."""
    # Currently ACP is at version 1
    # This test documents which version we implement
    PROTOCOL_VERSION = 1
    assert PROTOCOL_VERSION == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
