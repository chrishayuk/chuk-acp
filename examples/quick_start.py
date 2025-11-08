"""
Quick start example using the high-level ACPClient.

This is the simplest way to use chuk-acp - the ACPClient handles all protocol
details automatically.
"""

import anyio
from pathlib import Path
from chuk_acp import ACPClient


async def main() -> None:
    # Get the path to echo_agent.py
    script_dir = Path(__file__).parent
    echo_agent_path = script_dir / "echo_agent.py"

    print("Starting echo agent...\n")

    # The ACPClient handles all protocol ceremony:
    # - Initialization
    # - Session creation
    # - Notification capture
    # - Request/response handling
    async with ACPClient("python", [str(echo_agent_path)]) as client:
        print(f"Connected to: {client.agent_info.name} v{client.agent_info.version}")
        print(f"Session ID: {client.current_session.sessionId}\n")

        # Send prompts and get full responses automatically
        result = await client.send_prompt("Hello, Agent!")
        print("User: Hello, Agent!")
        print(f"Agent: {result.full_message}")
        print(f"Stop reason: {result.stop_reason}\n")

        # Send another prompt
        result = await client.send_prompt("How are you today?")
        print("User: How are you today?")
        print(f"Agent: {result.full_message}")
        print(f"Stop reason: {result.stop_reason}")


if __name__ == "__main__":
    anyio.run(main)
