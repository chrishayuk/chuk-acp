#!/usr/bin/env python3
"""Comprehensive ACP Demo - Complete walkthrough of chuk-acp capabilities.

This demo showcases:
1. Creating a simple ACP agent server
2. Connecting to it via stdio transport
3. Performing the full ACP handshake
4. Executing various ACP operations (session, filesystem, terminal)
5. Proper error handling and cleanup

Usage:
    python examples/comprehensive_demo.py
"""

import asyncio
import sys
import tempfile
from pathlib import Path

import anyio

# Import ACP protocol components
from chuk_acp.protocol.types import (
    ClientInfo,
    ClientCapabilities,
    AgentInfo,
    AgentCapabilities,
    TextContent,
)
from chuk_acp.protocol.messages.initialize import send_initialize
from chuk_acp.protocol.messages.session import (
    send_session_new,
    send_session_prompt,
)
from chuk_acp.protocol.messages.filesystem import (
    send_fs_read_text_file,
    send_fs_write_text_file,
)
from chuk_acp.protocol.messages.terminal import (
    send_terminal_create,
)
from chuk_acp.transport.stdio import stdio_transport


# First, create a simple ACP agent server script
AGENT_SERVER_CODE = '''
"""Simple ACP agent that responds to protocol messages."""

import sys
import json
import os
import tempfile

def handle_request(request):
    """Handle incoming JSON-RPC requests."""
    method = request.get("method")
    params = request.get("params", {})
    req_id = request.get("id")

    # Initialize
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": 1,
                "agentInfo": {
                    "name": "demo-agent",
                    "version": "1.0.0"
                },
                "agentCapabilities": {
                    "supportsFilesystem": True,
                    "supportsTerminal": True
                }
            }
        }

    # Session new
    elif method == "session/new":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "sessionId": "demo-session-123"
            }
        }

    # Session prompt
    elif method == "session/prompt":
        prompt_content = params.get("prompt", [])
        prompt_text = prompt_content[0].get("text", "") if prompt_content else ""

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "stopReason": "end_turn",
                "agentMessage": [{
                    "type": "text",
                    "text": f"Agent received: {prompt_text}. Processing complete!"
                }]
            }
        }

    # Filesystem read
    elif method == "fs/read_text_file":
        path = params.get("path", "")
        try:
            with open(path, "r") as f:
                contents = f.read()
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"contents": contents}
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32603,
                    "message": f"Read error: {e}"
                }
            }

    # Filesystem write
    elif method == "fs/write_text_file":
        path = params.get("path", "")
        contents = params.get("contents", "")
        try:
            with open(path, "w") as f:
                f.write(contents)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {}
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32603,
                    "message": f"Write error: {e}"
                }
            }

    # Terminal create
    elif method == "terminal/create":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "id": "term-123"
            }
        }

    # Default: method not found
    else:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            }
        }

def main():
    """Main server loop."""
    sys.stderr.write("ACP Demo Agent starting...\\n")
    sys.stderr.flush()

    try:
        while True:
            line = sys.stdin.readline()
            if not line:
                break

            try:
                request = json.loads(line)
                response = handle_request(request)
                sys.stdout.write(json.dumps(response) + "\\n")
                sys.stdout.flush()
            except json.JSONDecodeError as e:
                sys.stderr.write(f"JSON decode error: {e}\\n")
                sys.stderr.flush()
            except Exception as e:
                sys.stderr.write(f"Error handling request: {e}\\n")
                sys.stderr.flush()

    except KeyboardInterrupt:
        sys.stderr.write("Agent shutting down...\\n")
        sys.stderr.flush()

if __name__ == "__main__":
    main()
'''


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


async def run_demo() -> None:
    """Run the comprehensive ACP demo."""
    print_section("CHUK-ACP COMPREHENSIVE DEMO")

    print("This demo showcases the Agent Client Protocol (ACP) implementation.")
    print("We'll start a simple agent server and demonstrate the protocol flow.\n")

    # Step 1: Create temporary agent server file
    print_section("Step 1: Creating Agent Server")

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False
    ) as agent_file:
        agent_file.write(AGENT_SERVER_CODE)
        agent_path = agent_file.name

    print(f"✓ Created temporary agent server at: {agent_path}")
    print(f"  Agent capabilities: filesystem, terminal support")

    try:
        # Step 2: Connect to agent via stdio transport
        print_section("Step 2: Establishing Connection")

        print(f"Launching agent: python {agent_path}")
        print("Establishing stdio transport...")

        async with stdio_transport(
            command=sys.executable,
            args=[agent_path]
        ) as (read_stream, write_stream):

            print("✓ Transport established")
            print("✓ Bidirectional communication ready\n")

            # Step 3: Protocol handshake (Initialize)
            print_section("Step 3: Protocol Handshake (Initialize)")

            client_info = ClientInfo(
                name="demo-client",
                version="1.0.0"
            )

            client_capabilities = ClientCapabilities(
                supportsInteractiveSessionMode=True
            )

            print(f"Sending initialize request...")
            print(f"  Client: {client_info.name} v{client_info.version}")

            init_result = await send_initialize(
                read_stream,
                write_stream,
                protocol_version=1,
                client_info=client_info,
                capabilities=client_capabilities
            )

            print(f"\n✓ Handshake successful!")
            print(f"  Protocol Version: {init_result.protocolVersion}")
            print(f"  Agent: {init_result.agentInfo.name} v{init_result.agentInfo.version}")
            print(f"  Agent Capabilities:")

            if hasattr(init_result, 'capabilities') and init_result.capabilities:
                caps = init_result.capabilities.model_dump() if hasattr(init_result.capabilities, 'model_dump') else vars(init_result.capabilities)
                for cap, value in caps.items():
                    if value:
                        print(f"    • {cap}: {value}")
            else:
                print(f"    (No capabilities reported)")

            # Step 4: Create a session
            print_section("Step 4: Creating Session")

            import os
            cwd = os.getcwd()
            print(f"Creating new session in: {cwd}")

            session_result = await send_session_new(
                read_stream,
                write_stream,
                cwd=cwd
            )

            session_id = session_result.sessionId
            print(f"✓ Session created: {session_id}")

            # Step 5: Send a prompt to the agent
            print_section("Step 5: Sending Prompt to Agent")

            prompt_text = "Hello, Agent! Please analyze this project."
            print(f"Sending prompt: '{prompt_text}'")

            prompt_result = await send_session_prompt(
                read_stream,
                write_stream,
                session_id=session_id,
                prompt=[TextContent(text=prompt_text)]
            )

            print(f"\n✓ Agent response received:")
            print(f"  Stop Reason: {prompt_result.stopReason}")

            if hasattr(prompt_result, 'agentMessage') and prompt_result.agentMessage:
                for msg in prompt_result.agentMessage:
                    if hasattr(msg, 'text'):
                        print(f"  Message: {msg.text}")

            # Step 6: Filesystem operations
            print_section("Step 6: Filesystem Operations")

            # Create a temporary file
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".txt", delete=False
            ) as tmp_file:
                test_content = "Hello from ACP client!\nThis is a test file."
                tmp_file.write(test_content)
                tmp_path = tmp_file.name

            print(f"Created test file: {tmp_path}")
            print(f"Original content:\n  {test_content.replace(chr(10), chr(10) + '  ')}")

            # Read file via ACP
            print(f"\nReading file via ACP agent...")
            file_contents = await send_fs_read_text_file(
                read_stream,
                write_stream,
                path=tmp_path
            )

            print(f"✓ File read successful:")
            print(f"  Content: {file_contents[:50]}...")

            # Write new content via ACP
            new_content = "Updated by ACP agent!\nModified content here."
            print(f"\nWriting new content via ACP agent...")

            await send_fs_write_text_file(
                read_stream,
                write_stream,
                path=tmp_path,
                contents=new_content
            )

            print(f"✓ File write successful")

            # Verify the write
            with open(tmp_path, "r") as f:
                verified_content = f.read()

            print(f"✓ Verified new content:")
            print(f"  {verified_content.replace(chr(10), chr(10) + '  ')}")

            # Cleanup temp file
            Path(tmp_path).unlink()

            # Step 7: Terminal operations
            print_section("Step 7: Terminal Operations")

            print("Creating terminal session...")
            terminal_info = await send_terminal_create(
                read_stream,
                write_stream,
                command="echo",
                args=["Hello from terminal!"]
            )

            print(f"✓ Terminal created: {terminal_info.id}")

            # Step 8: Summary
            print_section("Step 8: Demo Complete!")

            print("Successfully demonstrated:")
            print("  ✓ Stdio transport connection")
            print("  ✓ ACP protocol handshake (initialize)")
            print("  ✓ Session creation and management")
            print("  ✓ Agent prompt/response")
            print("  ✓ Filesystem read/write operations")
            print("  ✓ Terminal session creation")
            print("\nAll ACP protocol operations completed successfully!")

    finally:
        # Cleanup
        print_section("Cleanup")
        Path(agent_path).unlink()
        print(f"✓ Removed temporary agent server")


def main() -> None:
    """Main entry point."""
    try:
        anyio.run(run_demo)
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError running demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
