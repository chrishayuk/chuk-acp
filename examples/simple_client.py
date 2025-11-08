"""
Simple client example using the high-level ACPClient.

This example shows how easy it is to work with ACP agents using the
ACPClient class, which handles all protocol ceremony automatically.
"""

import anyio
from pathlib import Path
from chuk_acp import ACPClient


async def main() -> None:
    # Get the path to echo_agent.py
    script_dir = Path(__file__).parent
    echo_agent_path = script_dir / "echo_agent.py"

    # Create and use the client - handles initialization automatically
    async with ACPClient("python", [str(echo_agent_path)]) as client:
        # Show agent info
        print(f"Connected to: {client.agent_info.name} v{client.agent_info.version}")
        print(f"Session ID: {client.current_session.sessionId}\n")

        # Send a prompt - automatically captures all notifications
        result = await client.send_prompt("Hello from the simple client!")

        # Display the conversation
        print("=== Conversation ===")
        print("User: Hello from the simple client!")
        print(f"Agent: {result.full_message}")
        print(f"Stop reason: {result.stop_reason}")


if __name__ == "__main__":
    anyio.run(main)
