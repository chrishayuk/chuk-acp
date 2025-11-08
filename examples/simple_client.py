"""Simple ACP client example.

This example shows how to connect to an ACP agent and send a prompt.
"""

import asyncio
import logging

from chuk_acp import (
    stdio_transport,
    send_initialize,
    send_session_new,
    send_session_prompt,
    ClientInfo,
    ClientCapabilities,
    TextContent,
)

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO)


async def main():
    """Connect to an agent and send a simple prompt."""

    # Connect to agent via stdio
    async with stdio_transport("python", ["echo_agent.py"]) as (read, write):
        print("Connected to agent")

        # Step 1: Initialize connection
        print("\n1. Initializing...")
        init_result = await send_initialize(
            read,
            write,
            protocol_version=1,  # Latest protocol version
            client_info=ClientInfo(
                name="simple-client",
                version="0.1.0",
                title="Simple ACP Client Example",
            ),
            capabilities=ClientCapabilities(),
        )

        print(f"   Agent: {init_result.agentInfo.name} v{init_result.agentInfo.version}")
        print(f"   Protocol version: {init_result.protocolVersion}")

        # Step 2: Create a new session
        print("\n2. Creating session...")
        session = await send_session_new(
            read,
            write,
            cwd="/tmp",  # Must be absolute path
        )

        print(f"   Session ID: {session.sessionId}")

        # Step 3: Send a prompt
        print("\n3. Sending prompt...")
        prompt = [
            TextContent(
                text="Hello! Can you help me write a Python function to calculate fibonacci numbers?"
            )
        ]

        result = await send_session_prompt(
            read,
            write,
            session_id=session.sessionId,
            prompt=prompt,
            timeout=60.0,
        )

        print(f"   Stop reason: {result.stopReason}")
        print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
