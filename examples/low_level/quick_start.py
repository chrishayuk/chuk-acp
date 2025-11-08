#!/usr/bin/env python3
"""Quick Start - Minimal ACP example.

This example shows the minimal steps needed to:
1. Connect to an ACP agent via stdio
2. Perform the initialization handshake
3. Send a prompt and receive a response
4. Capture the agent's response via session/update notifications

Usage:
    python examples/quick_start.py
"""

import sys
import tempfile
import uuid
from pathlib import Path

import anyio

from chuk_acp.protocol.types import ClientInfo, ClientCapabilities, TextContent
from chuk_acp.protocol.messages.initialize import send_initialize
from chuk_acp.protocol.messages.session import send_session_new
from chuk_acp.protocol import (
    create_request,
    JSONRPCNotification,
    JSONRPCResponse,
    METHOD_SESSION_PROMPT,
    METHOD_SESSION_UPDATE,
)
from chuk_acp.transport.stdio import stdio_transport


# Simple echo agent that demonstrates using chuk-acp library
SIMPLE_AGENT = '''
import sys
import json

# Import chuk-acp library components
from chuk_acp.protocol import (
    create_response,
    create_error_response,
    create_notification,
    METHOD_INITIALIZE,
    METHOD_SESSION_NEW,
    METHOD_SESSION_PROMPT,
    METHOD_SESSION_UPDATE,
)
from chuk_acp.protocol.types import AgentInfo, AgentCapabilities, TextContent

def handle_message(msg):
    """Handle incoming messages using chuk-acp library."""
    method = msg.get("method")
    msg_id = msg.get("id")
    params = msg.get("params", {})

    try:
        if method == METHOD_INITIALIZE:
            # Use library types for structured data
            agent_info = AgentInfo(name="echo-agent", version="1.0.0")
            agent_capabilities = AgentCapabilities()

            result = {
                "protocolVersion": 1,
                "agentInfo": agent_info.model_dump(exclude_none=True),
                "agentCapabilities": agent_capabilities.model_dump(exclude_none=True)
            }
            response = create_response(id=msg_id, result=result)

        elif method == METHOD_SESSION_NEW:
            result = {"sessionId": "session-1"}
            response = create_response(id=msg_id, result=result)

        elif method == METHOD_SESSION_PROMPT:
            # Extract the prompt text
            session_id = params.get("sessionId")
            prompt = params.get("prompt", [])
            prompt_text = prompt[0].get("text", "") if prompt else ""

            # Send a session/update notification with the echo
            notification = create_notification(
                method=METHOD_SESSION_UPDATE,
                params={
                    "sessionId": session_id,
                    "agentMessageChunk": TextContent(
                        text=f"Echo: {prompt_text}"
                    ).model_dump(exclude_none=True)
                }
            )
            sys.stdout.write(json.dumps(notification.model_dump(exclude_none=True)) + "\\n")
            sys.stdout.flush()

            # Send the response
            result = {"stopReason": "end_turn"}
            response = create_response(id=msg_id, result=result)

        else:
            # Use library helper for errors
            response = create_error_response(
                id=msg_id,
                code=-32601,
                message="Method not found"
            )

        return response.model_dump(exclude_none=True)

    except Exception as e:
        response = create_error_response(id=msg_id, code=-32603, message=str(e))
        return response.model_dump(exclude_none=True)

while True:
    line = sys.stdin.readline()
    if not line:
        break
    try:
        msg = json.loads(line)
        response = handle_message(msg)
        sys.stdout.write(json.dumps(response) + "\\n")
        sys.stdout.flush()
    except Exception:
        pass
'''


async def main():
    """Run the quick start example."""
    print("=== ACP Quick Start ===\n")

    # Step 1: Create a temporary agent server
    print("1. Creating agent server...")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(SIMPLE_AGENT)
        agent_path = f.name

    try:
        # Step 2: Connect via stdio transport
        print("2. Connecting to agent...")
        async with stdio_transport(sys.executable, [agent_path]) as (read, write):
            # Step 3: Initialize the connection
            print("3. Initializing protocol...")
            init_result = await send_initialize(
                read,
                write,
                protocol_version=1,
                client_info=ClientInfo(name="quick-start", version="1.0.0"),
                capabilities=ClientCapabilities(),
            )
            print(f"   Connected to: {init_result.agentInfo.name}")

            # Step 4: Create a session
            print("4. Creating session...")
            session = await send_session_new(read, write, cwd=tempfile.gettempdir())
            print(f"   Session ID: {session.sessionId}")

            # Step 5: Send a prompt and capture the agent's response
            print("5. Sending prompt...")
            prompt_text = "Hello, Agent!"
            print(f"   User: {prompt_text}")

            # Send the request manually to capture session/update notifications
            request_id = str(uuid.uuid4())
            request = create_request(
                method=METHOD_SESSION_PROMPT,
                params={
                    "sessionId": session.sessionId,
                    "prompt": [TextContent(text=prompt_text).model_dump(exclude_none=True)],
                },
                id=request_id,
            )
            await write.send(request)

            # Collect agent responses from notifications
            agent_messages = []
            stop_reason = None

            with anyio.fail_after(60.0):
                while stop_reason is None:
                    message = await read.receive()

                    # Capture session/update notifications
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

            # Step 6: Display the response
            if agent_messages:
                print(f"   Agent: {''.join(agent_messages)}")

            print("\n✓ Success!")
            print(f"   Stop Reason: {stop_reason}")

    finally:
        # Cleanup
        Path(agent_path).unlink()
        print("\n✓ Cleanup complete")


if __name__ == "__main__":
    try:
        anyio.run(main)
    except KeyboardInterrupt:
        print("\n\nInterrupted")
        sys.exit(0)
