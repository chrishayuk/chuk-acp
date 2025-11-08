"""
Example showing how to use AgentConfig to connect to agents.

This matches the standard ACP configuration format used by editors like Zed, VSCode, etc.
"""

import anyio
import sys
from pathlib import Path
from chuk_acp import ACPClient, AgentConfig


async def main() -> None:
    print("=== ACP Configuration Example ===\n")

    # Get the Python executable being used
    python_exe = sys.executable
    echo_agent_path = str(Path(__file__).parent / "echo_agent.py")

    # Method 1: Create config directly
    print("Method 1: Direct configuration")
    config = AgentConfig(
        command=python_exe,
        args=[echo_agent_path],
        env={"DEBUG": "false"},  # Optional environment variables
    )

    async with ACPClient.from_config(config) as client:
        result = await client.send_prompt("Hello from config!")
        print(f"Agent: {result.full_message}\n")

    # Method 2: Create config from dictionary (like editor configs)
    print("Method 2: From dictionary (like ~/.config/zed/settings.json)")
    config_dict = {"command": python_exe, "args": [echo_agent_path], "env": {}}
    config = AgentConfig(**config_dict)

    async with ACPClient.from_config(config) as client:
        result = await client.send_prompt("Hello from dict config!")
        print(f"Agent: {result.full_message}\n")

    # Method 3: Standard approach (for comparison)
    print("Method 3: Standard approach (no config object)")
    async with ACPClient(command=python_exe, args=[echo_agent_path]) as client:
        result = await client.send_prompt("Hello standard way!")
        print(f"Agent: {result.full_message}\n")

    print("✓ All methods work!")


if __name__ == "__main__":
    anyio.run(main)
