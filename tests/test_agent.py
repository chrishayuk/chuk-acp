"""Tests for agent API."""

import json
from io import StringIO
from typing import List
from unittest.mock import patch

import pytest

from chuk_acp.agent import ACPAgent, AgentSession
from chuk_acp.protocol.types import AgentInfo, Content, AgentCapabilities


class TestAgent(ACPAgent):
    """Test agent implementation."""

    def get_agent_info(self) -> AgentInfo:
        """Return test agent info."""
        return AgentInfo(name="test-agent", version="1.0.0", title="Test Agent")

    async def handle_prompt(self, session: AgentSession, prompt: List[Content]) -> str:
        """Handle test prompt."""
        text = prompt[0].get("text", "") if prompt else ""
        return f"Response: {text}"


class TestAgentWithCustomCapabilities(ACPAgent):
    """Test agent with custom capabilities."""

    def get_agent_info(self) -> AgentInfo:
        """Return test agent info."""
        return AgentInfo(name="capable-agent", version="2.0.0")

    def get_agent_capabilities(self) -> AgentCapabilities:
        """Return custom capabilities."""
        return AgentCapabilities(supportsResources=True, supportsPrompts=True)

    async def handle_prompt(self, session: AgentSession, prompt: List[Content]) -> str:
        """Handle test prompt."""
        return "Custom response"


class TestACPAgent:
    """Test ACPAgent base class."""

    def test_agent_initialization_without_log_file(self):
        """Test agent initialization without log file."""
        agent = TestAgent()

        assert agent.sessions == {}
        assert hasattr(agent, "sessions")

    def test_agent_initialization_with_log_file(self, tmp_path):
        """Test agent initialization with log file."""
        log_file = tmp_path / "test.log"
        agent = TestAgent(log_file=str(log_file))

        assert agent.sessions == {}
        assert hasattr(agent, "sessions")

    def test_get_agent_info(self):
        """Test get_agent_info returns correct info."""
        agent = TestAgent()
        info = agent.get_agent_info()

        assert info.name == "test-agent"
        assert info.version == "1.0.0"
        assert info.title == "Test Agent"

    def test_get_agent_capabilities_default(self):
        """Test default agent capabilities."""
        agent = TestAgent()
        caps = agent.get_agent_capabilities()

        assert isinstance(caps, AgentCapabilities)
        # Default capabilities should have default values
        assert caps.model_dump(exclude_none=True) == {}

    def test_get_agent_capabilities_custom(self):
        """Test custom agent capabilities."""
        agent = TestAgentWithCustomCapabilities()
        caps = agent.get_agent_capabilities()

        assert caps.supportsResources is True
        assert caps.supportsPrompts is True

    @pytest.mark.anyio
    async def test_handle_prompt(self):
        """Test handle_prompt implementation."""
        agent = TestAgent()
        session = AgentSession(session_id="test-session")
        prompt = [{"type": "text", "text": "Hello"}]

        response = await agent.handle_prompt(session, prompt)

        assert response == "Response: Hello"

    @pytest.mark.anyio
    async def test_handle_prompt_with_empty_prompt(self):
        """Test handle_prompt with empty prompt."""
        agent = TestAgent()
        session = AgentSession(session_id="test-session")
        prompt = []

        response = await agent.handle_prompt(session, prompt)

        assert response == "Response: "

    def test_send_message(self):
        """Test send_message sends correct notification."""
        agent = TestAgent()

        with patch.object(agent, "_write_message") as mock_write:
            agent.send_message("Test message", "session-123")

            mock_write.assert_called_once()
            call_args = mock_write.call_args[0][0]

            assert call_args["method"] == "session/update"
            assert call_args["params"]["sessionId"] == "session-123"
            assert call_args["params"]["agentMessageChunk"]["type"] == "text"
            assert call_args["params"]["agentMessageChunk"]["text"] == "Test message"

    def test_write_message(self):
        """Test _write_message writes to stdout."""
        agent = TestAgent()
        message = {"test": "data"}

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            agent._write_message(message)
            output = mock_stdout.getvalue()

            assert json.loads(output.strip()) == message

    def test_handle_initialize(self):
        """Test _handle_initialize returns correct response."""
        agent = TestAgent()
        params = {"protocolVersion": 1, "clientInfo": {"name": "test-client"}}

        result = agent._handle_initialize(params)

        assert result["protocolVersion"] == 1
        assert result["agentInfo"]["name"] == "test-agent"
        assert result["agentInfo"]["version"] == "1.0.0"
        assert "agentCapabilities" in result

    def test_handle_initialize_with_default_protocol_version(self):
        """Test _handle_initialize with missing protocolVersion."""
        agent = TestAgent()
        params = {}

        result = agent._handle_initialize(params)

        assert result["protocolVersion"] == 1

    def test_handle_session_new(self):
        """Test _handle_session_new creates session."""
        agent = TestAgent()
        params = {"cwd": "/tmp/test"}

        result = agent._handle_session_new(params)

        assert "sessionId" in result
        session_id = result["sessionId"]
        assert session_id.startswith("session_")
        assert session_id in agent.sessions
        assert agent.sessions[session_id].cwd == "/tmp/test"

    def test_handle_session_new_without_cwd(self):
        """Test _handle_session_new without cwd."""
        agent = TestAgent()
        params = {}

        result = agent._handle_session_new(params)

        session_id = result["sessionId"]
        assert agent.sessions[session_id].cwd is None

    @pytest.mark.anyio
    async def test_handle_session_prompt(self):
        """Test _handle_session_prompt processes prompt."""
        agent = TestAgent()

        # Create a session first
        session_result = agent._handle_session_new({"cwd": "/tmp"})
        session_id = session_result["sessionId"]

        params = {"sessionId": session_id, "prompt": [{"type": "text", "text": "Test prompt"}]}

        with patch.object(agent, "send_message") as mock_send:
            result = await agent._handle_session_prompt(params)

            assert result["stopReason"] == "end_turn"
            mock_send.assert_called_once_with("Response: Test prompt", session_id)

    @pytest.mark.anyio
    async def test_handle_session_prompt_unknown_session(self):
        """Test _handle_session_prompt with unknown session raises error."""
        agent = TestAgent()

        params = {"sessionId": "unknown-session", "prompt": [{"type": "text", "text": "Test"}]}

        with pytest.raises(Exception, match="Unknown session"):
            await agent._handle_session_prompt(params)

    @pytest.mark.anyio
    async def test_handle_message_initialize(self):
        """Test _handle_message routes initialize correctly."""
        agent = TestAgent()

        message = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "initialize",
            "params": {"protocolVersion": 1},
        }

        with patch.object(agent, "_write_message") as mock_write:
            await agent._handle_message(message)

            mock_write.assert_called_once()
            response = mock_write.call_args[0][0]

            assert response["jsonrpc"] == "2.0"
            assert response["id"] == "1"
            assert "result" in response
            assert response["result"]["agentInfo"]["name"] == "test-agent"

    @pytest.mark.anyio
    async def test_handle_message_session_new(self):
        """Test _handle_message routes session/new correctly."""
        agent = TestAgent()

        message = {"jsonrpc": "2.0", "id": "2", "method": "session/new", "params": {"cwd": "/tmp"}}

        with patch.object(agent, "_write_message") as mock_write:
            await agent._handle_message(message)

            mock_write.assert_called_once()
            response = mock_write.call_args[0][0]

            assert response["jsonrpc"] == "2.0"
            assert response["id"] == "2"
            assert "result" in response
            assert "sessionId" in response["result"]

    @pytest.mark.anyio
    async def test_handle_message_session_prompt(self):
        """Test _handle_message routes session/prompt correctly."""
        agent = TestAgent()

        # Create session first
        session_result = agent._handle_session_new({})
        session_id = session_result["sessionId"]

        message = {
            "jsonrpc": "2.0",
            "id": "3",
            "method": "session/prompt",
            "params": {"sessionId": session_id, "prompt": [{"type": "text", "text": "Hello"}]},
        }

        with patch.object(agent, "_write_message") as mock_write:
            with patch.object(agent, "send_message"):
                await agent._handle_message(message)

                # Should write response
                assert mock_write.called
                response = mock_write.call_args[0][0]
                assert response["result"]["stopReason"] == "end_turn"

    @pytest.mark.anyio
    async def test_handle_message_unknown_method(self):
        """Test _handle_message with unknown method sends error."""
        agent = TestAgent()

        message = {"jsonrpc": "2.0", "id": "4", "method": "unknown/method", "params": {}}

        with patch.object(agent, "_write_message") as mock_write:
            await agent._handle_message(message)

            mock_write.assert_called_once()
            response = mock_write.call_args[0][0]

            assert "error" in response
            assert "Unknown method" in response["error"]["message"]
            assert response["error"]["code"] == -32603

    @pytest.mark.anyio
    async def test_handle_message_error_handling(self):
        """Test _handle_message error handling."""
        agent = TestAgent()

        # Missing required params
        message = {
            "jsonrpc": "2.0",
            "id": "5",
            "method": "session/prompt",
            "params": {},  # Missing sessionId
        }

        with patch.object(agent, "_write_message") as mock_write:
            await agent._handle_message(message)

            mock_write.assert_called_once()
            response = mock_write.call_args[0][0]

            assert "error" in response
            assert response["error"]["code"] == -32603

    @pytest.mark.anyio
    async def test_run_async_processes_messages(self):
        """Test _run_async processes stdin messages."""
        agent = TestAgent()

        messages = [
            json.dumps({"jsonrpc": "2.0", "id": "1", "method": "initialize", "params": {}}),
            json.dumps({"jsonrpc": "2.0", "id": "2", "method": "session/new", "params": {}}),
            "",  # Empty line should be skipped
        ]

        with patch("sys.stdin", messages):
            with patch.object(agent, "_handle_message") as mock_handle:
                await agent._run_async()

                # Should handle 2 messages (skip empty line)
                assert mock_handle.call_count == 2

    @pytest.mark.anyio
    async def test_run_async_handles_json_decode_error(self):
        """Test _run_async handles JSON decode errors."""
        agent = TestAgent()

        messages = [
            "invalid json",
            json.dumps({"jsonrpc": "2.0", "id": "1", "method": "initialize", "params": {}}),
        ]

        with patch("sys.stdin", messages):
            with patch.object(agent, "_handle_message") as mock_handle:
                await agent._run_async()

                # Should handle only the valid message
                assert mock_handle.call_count == 1

    @pytest.mark.anyio
    async def test_run_async_handles_processing_error(self):
        """Test _run_async handles message processing errors."""
        agent = TestAgent()

        messages = [json.dumps({"jsonrpc": "2.0", "id": "1", "method": "initialize", "params": {}})]

        with patch("sys.stdin", messages):
            with patch.object(agent, "_handle_message", side_effect=Exception("Test error")):
                # Should not raise, just log the error
                await agent._run_async()

    def test_run_starts_agent(self):
        """Test run() starts the agent."""
        agent = TestAgent()

        messages = [json.dumps({"jsonrpc": "2.0", "id": "1", "method": "initialize", "params": {}})]

        with patch("sys.stdin", messages):
            with patch.object(agent, "_write_message"):
                # run() should complete without error
                agent.run()

    def test_run_handles_keyboard_interrupt(self):
        """Test run() handles KeyboardInterrupt."""
        agent = TestAgent()

        with patch("anyio.run", side_effect=KeyboardInterrupt):
            # Should not raise, just log and exit gracefully
            agent.run()

    def test_run_handles_general_exception(self):
        """Test run() handles general exceptions."""
        agent = TestAgent()

        with patch("anyio.run", side_effect=Exception("Test error")):
            # Should not raise, just log and exit gracefully
            agent.run()
