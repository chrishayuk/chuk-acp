#!/usr/bin/env python3
"""Quick Start - Minimal ACP example.

This example shows the minimal steps needed to:
1. Connect to an ACP agent via stdio
2. Perform the initialization handshake
3. Send a prompt and receive a response

Usage:
    python examples/quick_start.py
"""

import sys
import tempfile
from pathlib import Path

import anyio

from chuk_acp.protocol.types import ClientInfo, ClientCapabilities, TextContent
from chuk_acp.protocol.messages.initialize import send_initialize
from chuk_acp.protocol.messages.session import send_session_new, send_session_prompt
from chuk_acp.transport.stdio import stdio_transport


# Simple echo agent that responds to ACP protocol
SIMPLE_AGENT = '''
import sys
import json

def handle_message(msg):
    """Handle incoming messages."""
    method = msg.get("method")
    msg_id = msg.get("id")
    params = msg.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": 1,
                "agentInfo": {"name": "echo-agent", "version": "1.0.0"},
                "agentCapabilities": {}
            }
        }
    elif method == "session/new":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"sessionId": "session-1"}
        }
    elif method == "session/prompt":
        prompt = params.get("prompt", [])
        text = prompt[0].get("text", "") if prompt else ""
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "stopReason": "end_turn",
                "agentMessage": [{"type": "text", "text": f"Echo: {text}"}]
            }
        }
    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {"code": -32601, "message": "Method not found"}
    }

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
            session = await send_session_new(read, write, cwd="/tmp")
            print(f"   Session ID: {session.sessionId}")

            # Step 5: Send a prompt
            print("5. Sending prompt...")
            result = await send_session_prompt(
                read,
                write,
                session_id=session.sessionId,
                prompt=[TextContent(text="Hello, Agent!")],
            )

            # Step 6: Display the response
            print("\n✓ Success!")
            print(f"   Stop Reason: {result.stopReason}")
            print("   Response: Agent completed processing the prompt")

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
