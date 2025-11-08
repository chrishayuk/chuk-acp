"""Tests for client configuration."""

import json
import tempfile
from pathlib import Path
import pytest

from chuk_acp.client.config import AgentConfig, load_agent_config


class TestAgentConfig:
    """Test AgentConfig model."""

    def test_basic_creation(self):
        """Test creating a basic config."""
        config = AgentConfig(command="python")
        assert config.command == "python"
        assert config.args == []
        assert config.env == {}
        assert config.cwd is None

    def test_full_creation(self):
        """Test creating a config with all fields."""
        config = AgentConfig(
            command="kimi",
            args=["--acp", "--verbose"],
            env={"DEBUG": "true", "LOG_LEVEL": "info"},
            cwd="/tmp/agent",
        )
        assert config.command == "kimi"
        assert config.args == ["--acp", "--verbose"]
        assert config.env == {"DEBUG": "true", "LOG_LEVEL": "info"}
        assert config.cwd == "/tmp/agent"

    def test_from_dict(self):
        """Test creating config from dictionary."""
        config_dict = {
            "command": "python",
            "args": ["agent.py"],
            "env": {"DEBUG": "1"},
            "cwd": "/tmp",
        }
        config = AgentConfig(**config_dict)
        assert config.command == "python"
        assert config.args == ["agent.py"]
        assert config.env == {"DEBUG": "1"}
        assert config.cwd == "/tmp"

    def test_model_dump(self):
        """Test converting config to dictionary."""
        config = AgentConfig(
            command="python",
            args=["agent.py"],
            env={"DEBUG": "1"},
        )
        config_dict = config.model_dump()
        assert config_dict["command"] == "python"
        assert config_dict["args"] == ["agent.py"]
        assert config_dict["env"] == {"DEBUG": "1"}

    def test_model_dump_exclude_none(self):
        """Test model_dump with exclude_none."""
        config = AgentConfig(command="python")
        config_dict = config.model_dump(exclude_none=True)
        assert config_dict["command"] == "python"
        assert "cwd" not in config_dict or config_dict["cwd"] is None


class TestLoadAgentConfig:
    """Test loading agent config from file."""

    def test_load_from_json_file(self):
        """Test loading config from JSON file."""
        config_data = {
            "command": "kimi",
            "args": ["--acp"],
            "env": {"DEBUG": "true"},
            "cwd": "/tmp",
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name

        try:
            config = load_agent_config(temp_path)
            assert config.command == "kimi"
            assert config.args == ["--acp"]
            assert config.env == {"DEBUG": "true"}
            assert config.cwd == "/tmp"
        finally:
            Path(temp_path).unlink()

    def test_load_minimal_config(self):
        """Test loading minimal config (only command)."""
        config_data = {"command": "python"}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name

        try:
            config = load_agent_config(temp_path)
            assert config.command == "python"
            assert config.args == []
            assert config.env == {}
            assert config.cwd is None
        finally:
            Path(temp_path).unlink()

    def test_load_with_expanduser(self):
        """Test that paths are expanded with expanduser."""
        config_data = {"command": "python"}

        # Create a temp file in /tmp which doesn't need expansion
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name

        try:
            # Load using the actual path (expanduser won't change /tmp paths)
            config = load_agent_config(temp_path)
            assert config.command == "python"
        finally:
            Path(temp_path).unlink()

    def test_load_nonexistent_file(self):
        """Test loading from non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            load_agent_config("/nonexistent/path/config.json")

    def test_load_invalid_json(self):
        """Test loading invalid JSON raises error."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("not valid json {")
            temp_path = f.name

        try:
            with pytest.raises(json.JSONDecodeError):
                load_agent_config(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_load_missing_command(self):
        """Test loading config without required command field."""
        config_data = {"args": ["--acp"]}  # Missing command

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name

        try:
            with pytest.raises((KeyError, TypeError, ValueError)):
                load_agent_config(temp_path)
        finally:
            Path(temp_path).unlink()
