"""Configuration support for ACPClient."""

__all__ = ["AgentConfig", "load_agent_config"]

import json
from pathlib import Path
from typing import Optional, Dict
from ..protocol.acp_pydantic_base import AcpPydanticBase, PYDANTIC_AVAILABLE

if PYDANTIC_AVAILABLE:
    from ..protocol.acp_pydantic_base import ConfigDict


class AgentConfig(AcpPydanticBase):
    """
    Configuration for connecting to an ACP agent.

    This matches the standard ACP agent configuration format used by
    editors like Zed, VSCode, etc.

    Example:
        ```json
        {
          "command": "kimi",
          "args": ["--acp"],
          "env": {
            "DEBUG": "true"
          }
        }
        ```
    """

    command: str
    """Command to run the agent (e.g., "python", "kimi", "node")"""

    args: list[str] = []
    """Arguments to pass to the command (e.g., ["agent.py", "--acp"])"""

    env: Dict[str, str] = {}
    """Environment variables to set for the agent process"""

    cwd: Optional[str] = None
    """Working directory for the agent process"""

    if PYDANTIC_AVAILABLE:
        model_config = ConfigDict(extra="allow")


def load_agent_config(path: str | Path) -> AgentConfig:
    """
    Load agent configuration from a JSON file.

    Args:
        path: Path to JSON configuration file

    Returns:
        AgentConfig instance

    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config file is not valid JSON
        KeyError: If required 'command' field is missing

    Example:
        ```python
        # Load from file
        config = load_agent_config("~/.config/my-app/agent.json")

        # Use with ACPClient
        async with ACPClient.from_config(config) as client:
            result = await client.send_prompt("Hello!")
        ```

    Example config file:
        ```json
        {
          "command": "python",
          "args": ["agent.py", "--verbose"],
          "env": {
            "DEBUG": "true",
            "LOG_LEVEL": "info"
          },
          "cwd": "/path/to/agent"
        }
        ```
    """
    config_path = Path(path).expanduser()
    with open(config_path) as f:
        config_dict = json.load(f)
    return AgentConfig(**config_dict)
