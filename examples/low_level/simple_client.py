"""Simple ACP client example.

This example shows how to connect to an ACP agent and send a prompt.
It demonstrates how to:
- Establish a connection via stdio transport
- Initialize the protocol
- Create a session
- Send a prompt and capture the agent's response via session/update notifications
"""

import asyncio
import logging
import tempfile
import uuid

import anyio

from chuk_acp import (
    stdio_transport,
    send_initialize,
    send_session_new,
    ClientInfo,
    ClientCapabilities,
    TextContent,
)
from chuk_acp.protocol import (
    create_request,
    JSONRPCNotification,
    JSONRPCResponse,
    METHOD_SESSION_PROMPT,
    METHOD_SESSION_UPDATE,
    PROTOCOL_VERSION_CURRENT,
)

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO)


async def main():
    """Connect to an agent and send a simple prompt."""
    from pathlib import Path

    # Get the directory containing this script (go up one level to find echo_agent.py)
    script_dir = Path(__file__).parent.parent
    echo_agent_path = script_dir / "echo_agent.py"

    print("=== Simple ACP Client Demo ===\n")

    # Connect to agent via stdio
    async with stdio_transport("python", [str(echo_agent_path)]) as (read, write):
        print("✓ Connected to agent\n")

        # Step 1: Initialize connection
        print("1. Initializing protocol...")
        init_result = await send_initialize(
            read,
            write,
            protocol_version=PROTOCOL_VERSION_CURRENT,
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
            cwd=tempfile.gettempdir(),  # Must be absolute path
        )

        print(f"   Session ID: {session.sessionId}")

        # Step 3: Send a prompt and capture notifications
        print("\n3. Sending prompt...")
        prompt_text = (
            "Hello! Can you help me write a Python function to calculate fibonacci numbers?"
        )
        print(f"   User: {prompt_text}")

        prompt = [TextContent(text=prompt_text)]

        # Send the prompt request manually so we can capture session/update notifications
        # (send_session_prompt discards notifications, so we handle this manually here)
        request_id = str(uuid.uuid4())
        request = create_request(
            method=METHOD_SESSION_PROMPT,
            params={
                "sessionId": session.sessionId,
                "prompt": [p.model_dump(exclude_none=True) for p in prompt],
            },
            id=request_id,
        )

        await write.send(request)

        # Collect agent responses from session/update notifications
        agent_messages = []
        stop_reason = None

        # Wait for response and capture notifications
        with anyio.fail_after(60.0):
            while stop_reason is None:
                message = await read.receive()
                # Message is already parsed by the transport

                # Handle session/update notifications
                if isinstance(message, JSONRPCNotification):
                    if message.method == METHOD_SESSION_UPDATE:
                        params = message.params or {}
                        if "agentMessageChunk" in params:
                            chunk = params["agentMessageChunk"]
                            if isinstance(chunk, dict) and "text" in chunk:
                                agent_messages.append(chunk["text"])

                # Handle the response
                elif isinstance(message, JSONRPCResponse):
                    if message.id == request_id:
                        result = message.result
                        if isinstance(result, dict):
                            stop_reason = result.get("stopReason")

        # Display the conversation
        if agent_messages:
            print(f"   Agent: {''.join(agent_messages)}")

        print(f"   Stop reason: {stop_reason}")
        print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
