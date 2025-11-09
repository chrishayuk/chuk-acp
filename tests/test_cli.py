"""Tests for CLI."""

import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
import pytest

from chuk_acp.cli import (
    create_parser,
    parse_env_vars,
    interactive_mode,
    single_prompt_mode,
    main,
    cli_entry,
)
from chuk_acp.client import ACPClient
from chuk_acp.client.models import PromptResult


@pytest.fixture
def echo_agent_path():
    """Get path to echo_agent.py example."""
    repo_root = Path(__file__).parent.parent
    agent_path = repo_root / "examples" / "echo_agent.py"
    if not agent_path.exists():
        pytest.skip(f"Echo agent not found at {agent_path}")
    return str(agent_path)


@pytest.fixture
def python_exe():
    """Get Python executable path."""
    return sys.executable


class TestParseEnvVars:
    """Test environment variable parsing."""

    def test_parse_empty(self):
        """Test parsing empty list."""
        result = parse_env_vars(None)
        assert result == {}

    def test_parse_single(self):
        """Test parsing single env var."""
        result = parse_env_vars(["KEY=value"])
        assert result == {"KEY": "value"}

    def test_parse_multiple(self):
        """Test parsing multiple env vars."""
        result = parse_env_vars(["KEY1=value1", "KEY2=value2"])
        assert result == {"KEY1": "value1", "KEY2": "value2"}

    def test_parse_with_equals_in_value(self):
        """Test parsing env var with equals sign in value."""
        result = parse_env_vars(["KEY=value=with=equals"])
        assert result == {"KEY": "value=with=equals"}

    def test_parse_invalid_format(self, capsys):
        """Test parsing invalid format (no equals sign)."""
        result = parse_env_vars(["INVALID"])
        assert result == {}
        captured = capsys.readouterr()
        assert "Invalid env format" in captured.err


class TestCreateParser:
    """Test argument parser creation."""

    def test_parser_creation(self):
        """Test parser can be created."""
        parser = create_parser()
        assert parser is not None

    def test_parser_help(self):
        """Test parser has help."""
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["--help"])

    def test_parser_command(self):
        """Test parsing command."""
        parser = create_parser()
        args = parser.parse_args(["python", "agent.py"])
        assert args.mode_or_command == "python"
        assert args.args == ["agent.py"]

    def test_parser_config(self):
        """Test parsing config file."""
        parser = create_parser()
        args = parser.parse_args(["--config", "config.json"])
        assert args.config == "config.json"

    def test_parser_prompt(self):
        """Test parsing prompt."""
        parser = create_parser()
        args = parser.parse_args(["python", "agent.py", "--prompt", "Hello"])
        assert args.prompt == "Hello"

    def test_parser_verbose(self):
        """Test parsing verbose flag."""
        parser = create_parser()
        args = parser.parse_args(["python", "agent.py", "--verbose"])
        assert args.verbose is True

    def test_parser_env(self):
        """Test parsing environment variables."""
        parser = create_parser()
        args = parser.parse_args(["python", "agent.py", "--env", "KEY=value"])
        assert args.env == ["KEY=value"]

    def test_parser_cwd(self):
        """Test parsing working directory."""
        parser = create_parser()
        args = parser.parse_args(["python", "agent.py", "--cwd", "/tmp"])
        assert args.cwd == "/tmp"


class TestSinglePromptMode:
    """Test single prompt mode."""

    @pytest.mark.asyncio
    async def test_single_prompt_basic(self, python_exe, echo_agent_path, capsys):
        """Test basic single prompt."""
        async with ACPClient(python_exe, [echo_agent_path]) as client:
            await single_prompt_mode(client, "Test message", verbose=False)
            captured = capsys.readouterr()
            assert "Test message" in captured.out

    @pytest.mark.asyncio
    async def test_single_prompt_verbose(self, python_exe, echo_agent_path, capsys):
        """Test single prompt with verbose output."""
        async with ACPClient(python_exe, [echo_agent_path]) as client:
            await single_prompt_mode(client, "Test message", verbose=True)
            captured = capsys.readouterr()
            assert "Connected to:" in captured.out
            assert "echo-agent" in captured.out
            assert "Stop reason:" in captured.out

    @pytest.mark.asyncio
    async def test_single_prompt_no_response(self, capsys):
        """Test single prompt with no response."""
        mock_client = MagicMock(spec=ACPClient)
        mock_client.agent_info = None
        mock_client.send_prompt = AsyncMock(return_value=PromptResult(response={}, updates=[]))

        with pytest.raises(SystemExit):
            await single_prompt_mode(mock_client, "Test", verbose=False)
        captured = capsys.readouterr()
        assert "No response" in captured.err


class TestInteractiveMode:
    """Test interactive mode."""

    @pytest.mark.asyncio
    async def test_quit_command(self, python_exe, echo_agent_path, capsys, monkeypatch):
        """Test /quit command."""
        inputs = iter(["/quit"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        async with ACPClient(python_exe, [echo_agent_path]) as client:
            await interactive_mode(client, verbose=False)
            captured = capsys.readouterr()
            assert "Goodbye!" in captured.out

    @pytest.mark.asyncio
    async def test_exit_command(self, python_exe, echo_agent_path, capsys, monkeypatch):
        """Test /exit command."""
        inputs = iter(["/exit"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        async with ACPClient(python_exe, [echo_agent_path]) as client:
            await interactive_mode(client, verbose=False)
            captured = capsys.readouterr()
            assert "Goodbye!" in captured.out

    @pytest.mark.asyncio
    async def test_info_command(self, python_exe, echo_agent_path, capsys, monkeypatch):
        """Test /info command."""
        inputs = iter(["/info", "/quit"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        async with ACPClient(python_exe, [echo_agent_path]) as client:
            await interactive_mode(client, verbose=False)
            captured = capsys.readouterr()
            assert "echo-agent" in captured.out

    @pytest.mark.asyncio
    async def test_new_session_command(self, python_exe, echo_agent_path, capsys, monkeypatch):
        """Test /new command."""
        inputs = iter(["/new", "/quit"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        async with ACPClient(python_exe, [echo_agent_path]) as client:
            await interactive_mode(client, verbose=False)
            captured = capsys.readouterr()
            assert "Started new session" in captured.out

    @pytest.mark.asyncio
    async def test_send_message(self, python_exe, echo_agent_path, capsys, monkeypatch):
        """Test sending a regular message."""
        inputs = iter(["Hello agent", "/quit"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        async with ACPClient(python_exe, [echo_agent_path]) as client:
            await interactive_mode(client, verbose=False)
            captured = capsys.readouterr()
            assert "Hello agent" in captured.out

    @pytest.mark.asyncio
    async def test_verbose_mode(self, python_exe, echo_agent_path, capsys, monkeypatch):
        """Test interactive mode with verbose output."""
        inputs = iter(["/quit"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        async with ACPClient(python_exe, [echo_agent_path]) as client:
            await interactive_mode(client, verbose=True)
            captured = capsys.readouterr()
            assert "Connected to:" in captured.out
            assert "echo-agent" in captured.out

    @pytest.mark.asyncio
    async def test_empty_input(self, python_exe, echo_agent_path, monkeypatch):
        """Test empty input is ignored."""
        inputs = iter(["", "/quit"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        async with ACPClient(python_exe, [echo_agent_path]) as client:
            await interactive_mode(client, verbose=False)

    @pytest.mark.asyncio
    async def test_eof_error(self, python_exe, echo_agent_path, capsys, monkeypatch):
        """Test handling of EOFError (Ctrl+D)."""

        def raise_eof(_):
            raise EOFError()

        monkeypatch.setattr("builtins.input", raise_eof)

        async with ACPClient(python_exe, [echo_agent_path]) as client:
            await interactive_mode(client, verbose=False)
            captured = capsys.readouterr()
            assert "Goodbye!" in captured.out

    @pytest.mark.asyncio
    async def test_keyboard_interrupt(self, python_exe, echo_agent_path, capsys, monkeypatch):
        """Test handling of KeyboardInterrupt (Ctrl+C)."""

        def raise_keyboard_interrupt_then_quit(_):
            if not hasattr(raise_keyboard_interrupt_then_quit, "called"):
                raise_keyboard_interrupt_then_quit.called = True
                raise KeyboardInterrupt()
            return "/quit"

        monkeypatch.setattr("builtins.input", raise_keyboard_interrupt_then_quit)

        async with ACPClient(python_exe, [echo_agent_path]) as client:
            await interactive_mode(client, verbose=False)
            captured = capsys.readouterr()
            assert "Use /quit" in captured.out


class TestMain:
    """Test main CLI entry point."""

    @pytest.mark.asyncio
    async def test_main_with_command(self, python_exe, echo_agent_path, monkeypatch):
        """Test main with direct command."""
        monkeypatch.setattr(
            "sys.argv",
            ["chuk-acp", "client", python_exe, echo_agent_path, "--prompt", "Test"],
        )
        await main()

    @pytest.mark.asyncio
    async def test_main_with_config(self, python_exe, echo_agent_path, monkeypatch):
        """Test main with config file."""
        config_data = {"command": python_exe, "args": [echo_agent_path]}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name

        try:
            monkeypatch.setattr(
                "sys.argv",
                ["chuk-acp", "--interactive", "--config", temp_path, "--prompt", "Test"],
            )
            await main()
        finally:
            Path(temp_path).unlink()

    @pytest.mark.asyncio
    async def test_main_missing_config_file(self, monkeypatch, capsys):
        """Test main with non-existent config file."""
        monkeypatch.setattr(
            "sys.argv",
            ["chuk-acp", "--config", "/nonexistent/config.json"],
        )
        with pytest.raises(SystemExit):
            await main()
        captured = capsys.readouterr()
        assert "Config file not found" in captured.err

    @pytest.mark.asyncio
    async def test_main_invalid_config(self, monkeypatch, capsys):
        """Test main with invalid config file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("not valid json {")
            temp_path = f.name

        try:
            monkeypatch.setattr(
                "sys.argv",
                ["chuk-acp", "--config", temp_path],
            )
            with pytest.raises(SystemExit):
                await main()
            captured = capsys.readouterr()
            assert "Error loading config" in captured.err
        finally:
            Path(temp_path).unlink()

    @pytest.mark.asyncio
    async def test_main_no_command_or_config(self, monkeypatch, capsys):
        """Test main without command or config."""
        monkeypatch.setattr("sys.argv", ["chuk-acp"])
        with pytest.raises(SystemExit):
            await main()
        captured = capsys.readouterr()
        assert "Either --config or command must be specified" in captured.err

    @pytest.mark.asyncio
    async def test_main_with_env_vars(self, python_exe, echo_agent_path, monkeypatch):
        """Test main with environment variables."""
        monkeypatch.setattr(
            "sys.argv",
            [
                "chuk-acp",
                "client",
                python_exe,
                echo_agent_path,
                "--env",
                "DEBUG=true",
                "--prompt",
                "Test",
            ],
        )
        await main()

    @pytest.mark.asyncio
    async def test_main_with_cwd(self, python_exe, echo_agent_path, monkeypatch):
        """Test main with working directory."""
        monkeypatch.setattr(
            "sys.argv",
            [
                "chuk-acp",
                "client",
                python_exe,
                echo_agent_path,
                "--cwd",
                "/tmp",
                "--prompt",
                "Test",
            ],
        )
        await main()

    @pytest.mark.asyncio
    async def test_main_invalid_agent_command(self, monkeypatch, capsys):
        """Test main with invalid agent command."""
        monkeypatch.setattr(
            "sys.argv",
            ["chuk-acp", "client", "nonexistent_command", "--prompt", "Test"],
        )
        with pytest.raises(SystemExit):
            await main()
        captured = capsys.readouterr()
        assert "Agent command not found" in captured.err

    @pytest.mark.asyncio
    async def test_main_verbose_error(self, monkeypatch, capsys):
        """Test main with verbose flag on error."""
        monkeypatch.setattr(
            "sys.argv",
            ["chuk-acp", "client", "nonexistent_command", "--verbose"],
        )
        with pytest.raises(SystemExit):
            await main()
        # Verbose mode should be available but not necessarily shown in this error path


class TestCLIIntegration:
    """Integration tests for full CLI workflow."""

    @pytest.mark.asyncio
    async def test_full_interactive_session(self, python_exe, echo_agent_path, capsys, monkeypatch):
        """Test full interactive session with multiple interactions."""
        inputs = iter(
            [
                "First message",
                "Second message",
                "/info",
                "/new",
                "Message in new session",
                "/quit",
            ]
        )
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        async with ACPClient(python_exe, [echo_agent_path]) as client:
            await interactive_mode(client, verbose=True)
            captured = capsys.readouterr()
            assert "First message" in captured.out
            assert "Second message" in captured.out
            assert "Started new session" in captured.out

    @pytest.mark.asyncio
    async def test_config_with_env(self, python_exe, echo_agent_path, monkeypatch):
        """Test config file with environment variables."""
        config_data = {
            "command": python_exe,
            "args": [echo_agent_path],
            "env": {"DEBUG": "true"},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name

        try:
            monkeypatch.setattr(
                "sys.argv",
                ["chuk-acp", "--interactive", "--config", temp_path, "--prompt", "Test"],
            )
            await main()
        finally:
            Path(temp_path).unlink()

    @pytest.mark.asyncio
    async def test_custom_client_info(self, python_exe, echo_agent_path, monkeypatch):
        """Test with custom client info."""
        monkeypatch.setattr(
            "sys.argv",
            [
                "chuk-acp",
                "client",
                python_exe,
                echo_agent_path,
                "--client-name",
                "test-client",
                "--client-version",
                "1.0.0",
                "--prompt",
                "Test",
            ],
        )
        await main()


class TestErrorHandling:
    """Test error handling scenarios."""

    @pytest.mark.asyncio
    async def test_interactive_mode_empty_response(
        self, python_exe, echo_agent_path, capsys, monkeypatch
    ):
        """Test interactive mode with empty response."""
        mock_result = PromptResult(response={"stopReason": "end_turn"}, updates=[])

        inputs = iter(["Test", "/quit"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        async with ACPClient(python_exe, [echo_agent_path]) as client:
            # Mock send_prompt to return empty result
            async def mock_send(prompt, **kwargs):
                return mock_result

            client.send_prompt = mock_send
            await interactive_mode(client, verbose=False)
            captured = capsys.readouterr()
            assert "(No response from agent)" in captured.out

    @pytest.mark.asyncio
    async def test_interactive_mode_exception(
        self, python_exe, echo_agent_path, capsys, monkeypatch
    ):
        """Test interactive mode with exception during interaction."""
        inputs = iter(["Test", "/quit"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))

        async with ACPClient(python_exe, [echo_agent_path]) as client:
            # Mock send_prompt to raise exception
            async def mock_send(prompt, **kwargs):
                raise RuntimeError("Test error")

            client.send_prompt = mock_send

            with pytest.raises(RuntimeError):
                await interactive_mode(client, verbose=False)
            captured = capsys.readouterr()
            assert "Error during interaction" in captured.err

    @pytest.mark.asyncio
    async def test_main_verbose_traceback(self, python_exe, echo_agent_path, capsys, monkeypatch):
        """Test main with verbose error showing traceback."""
        monkeypatch.setattr(
            "sys.argv",
            [
                "chuk-acp",
                "nonexistent_command",
                "--verbose",
                "--prompt",
                "Test",
            ],
        )
        with pytest.raises(SystemExit):
            await main()
        # Verbose should trigger traceback printing
        capsys.readouterr()  # Clear output


class TestCLIEntry:
    """Test CLI entry point."""

    def test_cli_entry_success(self, python_exe, echo_agent_path, monkeypatch):
        """Test successful CLI entry."""
        monkeypatch.setattr(
            "sys.argv",
            ["chuk-acp", "client", python_exe, echo_agent_path, "--prompt", "Test"],
        )
        cli_entry()

    def test_cli_entry_keyboard_interrupt(self, monkeypatch, capsys):
        """Test CLI entry with keyboard interrupt."""

        def mock_run(coro):
            raise KeyboardInterrupt()

        monkeypatch.setattr("chuk_acp.cli.asyncio.run", mock_run)
        monkeypatch.setattr("sys.argv", ["chuk-acp", "client", "python", "test.py"])

        with pytest.raises(SystemExit) as exc_info:
            cli_entry()
        assert exc_info.value.code == 130
        captured = capsys.readouterr()
        assert "Interrupted by user" in captured.out
