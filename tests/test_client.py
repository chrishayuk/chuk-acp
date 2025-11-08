"""Tests for ACPClient."""

import sys
import tempfile
import json
from pathlib import Path
import pytest

from chuk_acp.client import ACPClient, AgentConfig, load_agent_config
from chuk_acp.protocol.types import ClientInfo


@pytest.fixture
def echo_agent_path():
    """Get path to echo_agent.py example."""
    # Get the examples directory
    repo_root = Path(__file__).parent.parent
    agent_path = repo_root / "examples" / "echo_agent.py"
    if not agent_path.exists():
        pytest.skip(f"Echo agent not found at {agent_path}")
    return str(agent_path)


@pytest.fixture
def python_exe():
    """Get Python executable path."""
    return sys.executable


class TestACPClientBasic:
    """Test basic ACPClient functionality."""

    @pytest.mark.asyncio
    async def test_basic_connection(self, python_exe, echo_agent_path):
        """Test basic connection to agent."""
        async with ACPClient(python_exe, [echo_agent_path]) as client:
            assert client.agent_info is not None
            assert client.agent_info.name == "echo-agent"
            assert client.current_session is not None
            assert client.current_session.sessionId is not None

    @pytest.mark.asyncio
    async def test_send_prompt(self, python_exe, echo_agent_path):
        """Test sending a prompt."""
        async with ACPClient(python_exe, [echo_agent_path]) as client:
            result = await client.send_prompt("Test message")
            assert result is not None
            assert result.full_message is not None
            assert "Test message" in result.full_message
            assert result.stop_reason == "end_turn"

    @pytest.mark.asyncio
    async def test_multiple_prompts(self, python_exe, echo_agent_path):
        """Test sending multiple prompts in same session."""
        async with ACPClient(python_exe, [echo_agent_path]) as client:
            result1 = await client.send_prompt("First")
            result2 = await client.send_prompt("Second")

            assert "First" in result1.full_message
            assert "Second" in result2.full_message

    @pytest.mark.asyncio
    async def test_with_custom_client_info(self, python_exe, echo_agent_path):
        """Test with custom client info."""
        client_info = ClientInfo(name="test-client", version="1.0.0")
        async with ACPClient(python_exe, [echo_agent_path], client_info=client_info) as client:
            assert client.agent_info is not None

    @pytest.mark.asyncio
    async def test_with_cwd(self, python_exe, echo_agent_path):
        """Test with custom working directory."""
        import tempfile

        test_cwd = tempfile.gettempdir()
        async with ACPClient(python_exe, [echo_agent_path], cwd=test_cwd) as client:
            assert client.default_cwd == test_cwd

    @pytest.mark.asyncio
    async def test_with_env(self, python_exe, echo_agent_path):
        """Test with environment variables."""
        async with ACPClient(
            python_exe, [echo_agent_path], env={"TEST_VAR": "test_value"}
        ) as client:
            result = await client.send_prompt("Test")
            assert result is not None


class TestACPClientConfig:
    """Test ACPClient with configuration."""

    @pytest.mark.asyncio
    async def test_from_config_direct(self, python_exe, echo_agent_path):
        """Test creating client from config."""
        config = AgentConfig(command=python_exe, args=[echo_agent_path])
        async with ACPClient.from_config(config) as client:
            result = await client.send_prompt("Hello")
            assert "Hello" in result.full_message

    @pytest.mark.asyncio
    async def test_from_config_with_env(self, python_exe, echo_agent_path):
        """Test config with environment variables."""
        config = AgentConfig(command=python_exe, args=[echo_agent_path], env={"DEBUG": "true"})
        async with ACPClient.from_config(config) as client:
            result = await client.send_prompt("Hello")
            assert result is not None

    @pytest.mark.asyncio
    async def test_from_config_with_cwd(self, python_exe, echo_agent_path):
        """Test config with working directory."""
        import tempfile

        test_cwd = tempfile.gettempdir()
        config = AgentConfig(command=python_exe, args=[echo_agent_path], cwd=test_cwd)
        async with ACPClient.from_config(config) as client:
            assert client.default_cwd == test_cwd

    @pytest.mark.asyncio
    async def test_from_config_file(self, python_exe, echo_agent_path):
        """Test loading config from JSON file."""
        config_data = {
            "command": python_exe,
            "args": [echo_agent_path],
            "env": {},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name

        try:
            config = load_agent_config(temp_path)
            async with ACPClient.from_config(config) as client:
                result = await client.send_prompt("Hello")
                assert "Hello" in result.full_message
        finally:
            Path(temp_path).unlink()

    @pytest.mark.asyncio
    async def test_from_config_with_custom_client_info(self, python_exe, echo_agent_path):
        """Test from_config with custom client info."""
        config = AgentConfig(command=python_exe, args=[echo_agent_path])
        client_info = ClientInfo(name="custom-client", version="2.0.0")
        async with ACPClient.from_config(config, client_info=client_info) as client:
            result = await client.send_prompt("Hello")
            assert result is not None


class TestACPClientSessions:
    """Test ACPClient session management."""

    @pytest.mark.asyncio
    async def test_default_session_created(self, python_exe, echo_agent_path):
        """Test that default session is created."""
        async with ACPClient(python_exe, [echo_agent_path]) as client:
            assert client.current_session is not None
            session_id = client.current_session.sessionId
            assert session_id is not None

    @pytest.mark.asyncio
    async def test_new_session(self, python_exe, echo_agent_path):
        """Test creating a new session."""
        async with ACPClient(python_exe, [echo_agent_path]) as client:
            original_session = client.current_session.sessionId
            new_session = await client.new_session()
            assert new_session.sessionId != original_session
            assert client.current_session.sessionId == new_session.sessionId

    @pytest.mark.asyncio
    async def test_new_session_with_cwd(self, python_exe, echo_agent_path):
        """Test creating new session with custom cwd."""
        async with ACPClient(python_exe, [echo_agent_path]) as client:
            new_session = await client.new_session(cwd="/tmp")
            assert new_session.sessionId is not None


class TestACPClientPrompts:
    """Test ACPClient prompt handling."""

    @pytest.mark.asyncio
    async def test_string_prompt(self, python_exe, echo_agent_path):
        """Test sending string prompt."""
        async with ACPClient(python_exe, [echo_agent_path]) as client:
            result = await client.send_prompt("Simple string")
            assert "Simple string" in result.full_message

    @pytest.mark.asyncio
    async def test_prompt_result_properties(self, python_exe, echo_agent_path):
        """Test PromptResult properties."""
        async with ACPClient(python_exe, [echo_agent_path]) as client:
            result = await client.send_prompt("Test")
            assert result.response is not None
            assert result.updates is not None
            assert isinstance(result.updates, list)
            assert result.stop_reason is not None
            assert result.agent_messages is not None
            assert isinstance(result.agent_messages, list)
            assert result.full_message is not None

    @pytest.mark.asyncio
    async def test_prompt_timeout(self, python_exe, echo_agent_path):
        """Test prompt with custom timeout."""
        async with ACPClient(python_exe, [echo_agent_path]) as client:
            result = await client.send_prompt("Test", timeout=30.0)
            assert result is not None


class TestACPClientErrors:
    """Test ACPClient error handling."""

    @pytest.mark.asyncio
    async def test_invalid_command(self):
        """Test with invalid command."""
        with pytest.raises(Exception):
            async with ACPClient("nonexistent_command", ["arg"]):
                pass

    @pytest.mark.asyncio
    async def test_send_prompt_before_connection(self):
        """Test sending prompt without connection."""
        client = ACPClient(sys.executable, ["nonexistent.py"])
        with pytest.raises(RuntimeError):
            await client.send_prompt("Test")


class TestACPClientProperties:
    """Test ACPClient properties."""

    @pytest.mark.asyncio
    async def test_agent_info_property(self, python_exe, echo_agent_path):
        """Test accessing agent_info property."""
        async with ACPClient(python_exe, [echo_agent_path]) as client:
            agent_info = client.agent_info
            assert agent_info is not None
            assert agent_info.name == "echo-agent"
            assert agent_info.version == "0.1.0"

    @pytest.mark.asyncio
    async def test_current_session_property(self, python_exe, echo_agent_path):
        """Test accessing current_session property."""
        async with ACPClient(python_exe, [echo_agent_path]) as client:
            session = client.current_session
            assert session is not None
            assert session.sessionId is not None
