"""Tests for ACP protocol types."""

from chuk_acp.protocol.types import (
    # Info types
    ClientInfo,
    AgentInfo,
    # Capability types
    ClientCapabilities,
    AgentCapabilities,
    # Content types
    TextContent,
    ImageContent,
    AudioContent,
    TextResourceContents,
    BlobResourceContents,
    # Permission types
    PermissionRequest,
    PermissionResponse,
    # Terminal types
    TerminalInfo,
    TerminalExit,
    TerminalOutput,
    # Command types
    AvailableCommand,
    # Plan types
    PlanEntry,
    Plan,
    # Tool types
    ToolCall,
    ToolCallUpdate,
    # MCP server types
    StdioMCPServer,
)


class TestInfoTypes:
    """Test info-related types."""

    def test_client_info_creation(self):
        """Test ClientInfo creation."""
        info = ClientInfo(name="test-client", version="1.0.0")
        assert info.name == "test-client"
        assert info.version == "1.0.0"

    def test_client_info_serialization(self):
        """Test ClientInfo serialization."""
        info = ClientInfo(name="test-client", version="1.0.0")
        data = info.model_dump()
        assert data["name"] == "test-client"
        assert data["version"] == "1.0.0"

    def test_agent_info_creation(self):
        """Test AgentInfo creation."""
        info = AgentInfo(name="test-agent", version="2.0.0")
        assert info.name == "test-agent"
        assert info.version == "2.0.0"

    def test_agent_info_serialization(self):
        """Test AgentInfo serialization."""
        info = AgentInfo(name="test-agent", version="2.0.0")
        data = info.model_dump()
        assert data["name"] == "test-agent"
        assert data["version"] == "2.0.0"


class TestCapabilityTypes:
    """Test capability-related types."""

    def test_client_capabilities_defaults(self):
        """Test ClientCapabilities with defaults."""
        caps = ClientCapabilities()
        data = caps.model_dump()
        assert isinstance(data, dict)

    def test_client_capabilities_with_values(self):
        """Test ClientCapabilities with custom values."""
        caps = ClientCapabilities(supportsInteractiveSessionMode=True)
        data = caps.model_dump()
        assert data.get("supportsInteractiveSessionMode") is True

    def test_agent_capabilities_defaults(self):
        """Test AgentCapabilities with defaults."""
        caps = AgentCapabilities()
        data = caps.model_dump()
        assert isinstance(data, dict)

    def test_agent_capabilities_with_values(self):
        """Test AgentCapabilities with custom values."""
        caps = AgentCapabilities(supportsCodeExecution=True)
        data = caps.model_dump()
        assert data.get("supportsCodeExecution") is True


class TestContentTypes:
    """Test content-related types."""

    def test_text_content_creation(self):
        """Test TextContent creation."""
        content = TextContent(text="Hello, world!")
        assert content.type == "text"
        assert content.text == "Hello, world!"

    def test_text_content_serialization(self):
        """Test TextContent serialization."""
        content = TextContent(text="Test")
        data = content.model_dump()
        assert data["type"] == "text"
        assert data["text"] == "Test"

    def test_image_content_creation(self):
        """Test ImageContent creation."""
        content = ImageContent(data="base64data", mimeType="image/png")
        assert content.type == "image"
        assert content.data == "base64data"
        assert content.mimeType == "image/png"

    def test_image_content_serialization(self):
        """Test ImageContent serialization."""
        content = ImageContent(data="abc123", mimeType="image/jpeg")
        data = content.model_dump()
        assert data["type"] == "image"
        assert data["data"] == "abc123"
        assert data["mimeType"] == "image/jpeg"

    def test_audio_content_creation(self):
        """Test AudioContent creation."""
        content = AudioContent(data="audiodata", mimeType="audio/mp3")
        assert content.type == "audio"
        assert content.data == "audiodata"
        assert content.mimeType == "audio/mp3"

    def test_text_resource_contents_creation(self):
        """Test TextResourceContents creation."""
        content = TextResourceContents(
            uri="file:///test.txt", mimeType="text/plain", text="contents"
        )
        assert content.uri == "file:///test.txt"
        assert content.text == "contents"
        assert content.mimeType == "text/plain"

    def test_blob_resource_contents_creation(self):
        """Test BlobResourceContents creation."""
        content = BlobResourceContents(
            uri="file:///image.png", mimeType="image/png", data="base64data"
        )
        assert content.uri == "file:///image.png"
        assert content.data == "base64data"
        assert content.mimeType == "image/png"


class TestPermissionTypes:
    """Test permission-related types."""

    def test_permission_request_creation(self):
        """Test PermissionRequest creation."""
        req = PermissionRequest(id="perm-test", action="read_file", description="Read config")
        assert req.action == "read_file"
        assert req.description == "Read config"

    def test_permission_request_serialization(self):
        """Test PermissionRequest serialization."""
        req = PermissionRequest(id="perm-test", action="write_file", description="Write log")
        data = req.model_dump()
        assert data["action"] == "write_file"
        assert data["description"] == "Write log"

    def test_permission_response_granted(self):
        """Test PermissionResponse with granted."""
        resp = PermissionResponse(id="perm-1", granted=True)
        assert resp.id == "perm-1"
        assert resp.granted is True

    def test_permission_response_denied(self):
        """Test PermissionResponse with denied."""
        resp = PermissionResponse(id="perm-2", granted=False)
        assert resp.granted is False

    def test_permission_response_serialization(self):
        """Test PermissionResponse serialization."""
        resp = PermissionResponse(id="p1", granted=True)
        data = resp.model_dump()
        assert data["id"] == "p1"
        assert data["granted"] is True


class TestTerminalTypes:
    """Test terminal-related types."""

    def test_terminal_info_creation(self):
        """Test TerminalInfo creation."""
        info = TerminalInfo(id="term-1", command="bash")
        assert info.id == "term-1"

    def test_terminal_info_serialization(self):
        """Test TerminalInfo serialization."""
        info = TerminalInfo(id="term-2", command="bash")
        data = info.model_dump()
        assert data["id"] == "term-2"

    def test_terminal_exit_creation(self):
        """Test TerminalExit creation."""
        exit_info = TerminalExit(id="term-1", exitCode=0)
        assert exit_info.exitCode == 0

    def test_terminal_exit_non_zero(self):
        """Test TerminalExit with non-zero code."""
        exit_info = TerminalExit(id="term-1", exitCode=1)
        data = exit_info.model_dump()
        assert data["exitCode"] == 1

    def test_terminal_output_creation(self):
        """Test TerminalOutput creation."""
        output = TerminalOutput(id="term-1", output="output text")
        assert output.id == "term-1"
        assert output.output == "output text"


class TestCommandTypes:
    """Test command-related types."""

    def test_available_command_creation(self):
        """Test AvailableCommand creation."""
        cmd = AvailableCommand(name="test", description="Test command")
        assert cmd.name == "test"
        assert cmd.description == "Test command"

    def test_available_command_serialization(self):
        """Test AvailableCommand serialization."""
        cmd = AvailableCommand(name="build", description="Build project")
        data = cmd.model_dump()
        assert data["name"] == "build"
        assert data["description"] == "Build project"


class TestPlanTypes:
    """Test plan-related types."""

    def test_plan_entry_creation(self):
        """Test PlanEntry creation."""
        entry = PlanEntry(content="Implement feature", status="pending", priority="medium")
        assert entry.content == "Implement feature"
        assert entry.status == "pending"

    def test_plan_entry_completed(self):
        """Test PlanEntry with completed status."""
        entry = PlanEntry(content="Fix bug", status="completed", priority="medium")
        data = entry.model_dump()
        assert data["status"] == "completed"

    def test_plan_entry_serialization(self):
        """Test PlanEntry serialization."""
        entry = PlanEntry(content="Write tests", status="in_progress", priority="medium")
        data = entry.model_dump()
        assert data["content"] == "Write tests"
        assert data["status"] == "in_progress"

    def test_plan_creation(self):
        """Test Plan creation."""
        plan = Plan(
            entries=[
                PlanEntry(content="Task 1", status="pending", priority="medium"),
                PlanEntry(content="Task 2", status="completed", priority="medium"),
            ]
        )
        assert len(plan.entries) == 2

    def test_plan_serialization(self):
        """Test Plan serialization."""
        plan = Plan(entries=[PlanEntry(content="Task", status="pending", priority="medium")])
        data = plan.model_dump()
        assert "entries" in data
        assert len(data["entries"]) == 1


class TestToolTypes:
    """Test tool-related types."""

    def test_tool_call_creation(self):
        """Test ToolCall creation."""
        call = ToolCall(id="call-1", name="test_tool", status="pending", arguments={"arg": "value"})
        assert call.id == "call-1"
        assert call.name == "test_tool"
        assert call.status == "pending"

    def test_tool_call_serialization(self):
        """Test ToolCall serialization."""
        call = ToolCall(id="c1", name="tool", status="completed", arguments={})
        data = call.model_dump()
        assert data["id"] == "c1"
        assert data["status"] == "completed"

    def test_tool_call_update_creation(self):
        """Test ToolCallUpdate creation."""
        update = ToolCallUpdate(id="call-1", status="in_progress")
        assert update.id == "call-1"
        assert update.status == "in_progress"


class TestMcpServerTypes:
    """Test MCP server-related types."""

    def test_stdio_mcp_server_creation(self):
        """Test StdioMCPServer creation."""
        server = StdioMCPServer(name="test-server", command="python", args=["server.py"])
        assert server.name == "test-server"
        assert server.command == "python"
        assert server.args == ["server.py"]

    def test_stdio_mcp_server_with_env(self):
        """Test StdioMCPServer with environment."""
        server = StdioMCPServer(
            name="server", command="node", args=["index.js"], env={"NODE_ENV": "production"}
        )
        data = server.model_dump()
        assert data["env"]["NODE_ENV"] == "production"

    def test_stdio_mcp_server_serialization(self):
        """Test StdioMCPServer serialization."""
        server = StdioMCPServer(name="mcp", command="./mcp-server", args=[])
        data = server.model_dump()
        assert data["name"] == "mcp"
        assert data["command"] == "./mcp-server"

    def test_mcp_server_base(self):
        """Test MCPServer base type."""
        # MCPServer is a union type, test with StdioMCPServer
        server = StdioMCPServer(name="test", command="cmd", args=[])
        assert server.name == "test"


class TestTypesIntegration:
    """Integration tests for types working together."""

    def test_multiple_content_types(self):
        """Test multiple content types together."""
        contents = [
            TextContent(text="Hello"),
            ImageContent(data="img123", mimeType="image/png"),
            AudioContent(data="audio123", mimeType="audio/mp3"),
        ]
        assert len(contents) == 3
        assert contents[0].type == "text"
        assert contents[1].type == "image"
        assert contents[2].type == "audio"

    def test_model_dump_exclude_none(self):
        """Test model_dump with exclude_none across types."""
        content = TextContent(text="Test")
        data = content.model_dump(exclude_none=True)
        assert "type" in data
        assert "text" in data

    def test_plan_with_multiple_entries(self):
        """Test Plan with multiple entries."""
        plan = Plan(
            entries=[
                PlanEntry(content="Task 1", status="completed", priority="medium"),
                PlanEntry(content="Task 2", status="in_progress", priority="medium"),
                PlanEntry(content="Task 3", status="pending", priority="medium"),
            ]
        )
        assert len(plan.entries) == 3
        assert plan.entries[0].status == "completed"
        assert plan.entries[2].status == "pending"
