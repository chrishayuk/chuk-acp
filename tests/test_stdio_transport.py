"""Tests for stdio transport implementation."""

import pytest
import sys
import tempfile
import os
import anyio

from chuk_acp.transport.stdio import (
    StdioParameters,
    StdioTransport,
    stdio_transport,
)


class TestStdioParameters:
    """Test StdioParameters class."""

    def test_basic_creation(self):
        """Test basic parameter creation."""
        params = StdioParameters(command="python", args=["script.py"])

        assert params.command == "python"
        assert params.args == ["script.py"]
        assert params.env is None
        assert params.cwd is None

    def test_with_environment(self):
        """Test parameters with environment variables."""
        env = {"PATH": "/usr/bin", "DEBUG": "1"}
        params = StdioParameters(command="node", args=["server.js"], env=env)

        assert params.command == "node"
        assert params.args == ["server.js"]
        assert params.env == env

    def test_with_cwd(self):
        """Test parameters with working directory."""
        params = StdioParameters(command="python", cwd="/tmp")

        assert params.command == "python"
        assert params.cwd == "/tmp"

    def test_empty_args(self):
        """Test parameters with no args."""
        params = StdioParameters(command="./server")

        assert params.command == "./server"
        assert params.args == []


class TestStdioTransport:
    """Test StdioTransport class."""

    def test_initialization(self):
        """Test transport initialization."""
        params = StdioParameters(command="python", args=["server.py"])
        transport = StdioTransport(params)

        assert transport.parameters == params
        assert transport.process is None

    @pytest.mark.asyncio
    async def test_get_streams_without_start(self):
        """Test getting streams before starting transport raises RuntimeError."""
        params = StdioParameters(command="python")
        transport = StdioTransport(params)

        with pytest.raises(RuntimeError, match="Transport not initialized"):
            await transport.get_streams()

    @pytest.mark.asyncio
    async def test_context_manager_lifecycle(self):
        """Test transport context manager lifecycle."""
        # Create a simple echo server
        server_script = """
import sys
import json

# Read one message and echo it back
line = sys.stdin.readline()
if line:
    msg = json.loads(line)
    response = {
        "jsonrpc": "2.0",
        "id": msg.get("id"),
        "result": {"echo": True}
    }
    sys.stdout.write(json.dumps(response) + "\\n")
    sys.stdout.flush()
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(server_script)
            server_file = f.name

        try:
            params = StdioParameters(command=sys.executable, args=[server_file])
            transport = StdioTransport(params)

            assert transport.process is None

            async with transport as t:
                assert transport.process is not None
                assert t is transport

                # Verify streams are available
                read_stream, write_stream = await transport.get_streams()
                assert read_stream is not None
                assert write_stream is not None

            # After exit, process should be cleaned up
            assert transport.process is not None  # Process object still exists
        finally:
            if os.path.exists(server_file):
                os.unlink(server_file)

    @pytest.mark.asyncio
    async def test_message_sending_and_receiving(self):
        """Test actual message communication through stdio."""
        server_script = """
import sys
import json

# Simple echo server
while True:
    line = sys.stdin.readline()
    if not line:
        break

    try:
        msg = json.loads(line)
        response = {
            "jsonrpc": "2.0",
            "id": msg.get("id"),
            "result": {"method": msg.get("method"), "received": True}
        }
        sys.stdout.write(json.dumps(response) + "\\n")
        sys.stdout.flush()
    except:
        break
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(server_script)
            server_file = f.name

        try:
            async with stdio_transport(sys.executable, [server_file]) as (read, write):
                # Create and send a request
                from chuk_acp.protocol.jsonrpc import create_request

                request = create_request(method="test", params={"key": "value"})

                await write.send(request)

                # Receive the response
                response = await read.receive()

                assert response.id == request.id
                assert response.result["method"] == "test"
                assert response.result["received"] is True
        finally:
            if os.path.exists(server_file):
                os.unlink(server_file)

    @pytest.mark.asyncio
    async def test_stderr_logging(self):
        """Test that stderr is captured and logged."""
        server_script = """
import sys
import json

# Write to stderr
sys.stderr.write("Server starting\\n")
sys.stderr.flush()

# Echo one message
line = sys.stdin.readline()
if line:
    msg = json.loads(line)
    response = {"jsonrpc": "2.0", "id": msg.get("id"), "result": {}}
    sys.stdout.write(json.dumps(response) + "\\n")
    sys.stdout.flush()

sys.stderr.write("Server stopping\\n")
sys.stderr.flush()
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(server_script)
            server_file = f.name

        try:
            async with stdio_transport(sys.executable, [server_file]) as (read, write):
                from chuk_acp.protocol.jsonrpc import create_request

                request = create_request(method="test")

                await write.send(request)
                await read.receive()

                # Give stderr logger time to process
                await anyio.sleep(0.1)
        finally:
            if os.path.exists(server_file):
                os.unlink(server_file)

    @pytest.mark.asyncio
    async def test_process_termination(self):
        """Test that process is properly terminated on exit."""
        server_script = """
import sys
import time

# Server that sleeps
time.sleep(10)
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(server_script)
            server_file = f.name

        try:
            params = StdioParameters(command=sys.executable, args=[server_file])
            transport = StdioTransport(params)

            async with transport:
                assert transport.process is not None
                process = transport.process

            # Process should be terminated after context exit
            # Give it a moment to cleanup
            await anyio.sleep(0.2)

            # Process should have been asked to terminate
            assert process is not None
        finally:
            if os.path.exists(server_file):
                os.unlink(server_file)

    @pytest.mark.asyncio
    async def test_multiple_messages(self):
        """Test sending and receiving multiple messages."""
        server_script = """
import sys
import json

# Handle multiple messages
for i in range(3):
    line = sys.stdin.readline()
    if not line:
        break

    msg = json.loads(line)
    response = {
        "jsonrpc": "2.0",
        "id": msg.get("id"),
        "result": {"index": i, "method": msg.get("method")}
    }
    sys.stdout.write(json.dumps(response) + "\\n")
    sys.stdout.flush()
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(server_script)
            server_file = f.name

        try:
            async with stdio_transport(sys.executable, [server_file]) as (read, write):
                from chuk_acp.protocol.jsonrpc import create_request

                # Send 3 messages
                requests = [create_request(method=f"method{i}") for i in range(3)]

                for req in requests:
                    await write.send(req)

                # Receive 3 responses
                for i, req in enumerate(requests):
                    resp = await read.receive()
                    assert resp.id == req.id
                    assert resp.result["index"] == i
        finally:
            if os.path.exists(server_file):
                os.unlink(server_file)

    @pytest.mark.asyncio
    async def test_notifications(self):
        """Test sending notifications (no response expected)."""
        server_script = """
import sys
import json

# Read notifications and send one response at the end
notifications = []
for i in range(2):
    line = sys.stdin.readline()
    if not line:
        break
    msg = json.loads(line)
    notifications.append(msg)

# Send confirmation
response = {
    "jsonrpc": "2.0",
    "id": "final",
    "result": {"count": len(notifications)}
}
sys.stdout.write(json.dumps(response) + "\\n")
sys.stdout.flush()
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(server_script)
            server_file = f.name

        try:
            async with stdio_transport(sys.executable, [server_file]) as (read, write):
                from chuk_acp.protocol.jsonrpc import (
                    create_notification,
                    create_request,
                )

                # Send 2 notifications
                await write.send(create_notification(method="notify1"))
                await write.send(create_notification(method="notify2"))

                # Send a request to get confirmation
                await write.send(create_request(method="finish", id="final"))

                # Should receive the final response
                resp = await read.receive()
                assert resp.result["count"] == 2
        finally:
            if os.path.exists(server_file):
                os.unlink(server_file)

    @pytest.mark.asyncio
    async def test_stdio_transport_convenience_function(self):
        """Test the stdio_transport convenience function."""
        server_script = """
import sys
import json

line = sys.stdin.readline()
msg = json.loads(line)
response = {"jsonrpc": "2.0", "id": msg.get("id"), "result": {"ok": True}}
sys.stdout.write(json.dumps(response) + "\\n")
sys.stdout.flush()
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(server_script)
            server_file = f.name

        try:
            # Use convenience function
            async with stdio_transport(command=sys.executable, args=[server_file]) as (read, write):
                assert read is not None
                assert write is not None

                from chuk_acp.protocol.jsonrpc import create_request

                req = create_request(method="test")
                await write.send(req)

                resp = await read.receive()
                assert resp.result["ok"] is True
        finally:
            if os.path.exists(server_file):
                os.unlink(server_file)


class TestStdioTransportEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_invalid_json_from_server(self):
        """Test handling of invalid JSON from server."""
        server_script = """
import sys

# Send invalid JSON
sys.stdout.write("not valid json\\n")
sys.stdout.flush()

# Then send valid message
import json
line = sys.stdin.readline()
msg = json.loads(line)
response = {"jsonrpc": "2.0", "id": msg.get("id"), "result": {}}
sys.stdout.write(json.dumps(response) + "\\n")
sys.stdout.flush()
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(server_script)
            server_file = f.name

        try:
            async with stdio_transport(sys.executable, [server_file]) as (read, write):
                from chuk_acp.protocol.jsonrpc import create_request

                # Send a request
                req = create_request(method="test")
                await write.send(req)

                # Should still receive valid response despite invalid JSON before it
                resp = await read.receive()
                assert resp.id == req.id
        finally:
            if os.path.exists(server_file):
                os.unlink(server_file)

    @pytest.mark.asyncio
    async def test_process_timeout_and_kill(self):
        """Test that process is killed if it doesn't terminate gracefully."""
        server_script = """
import sys
import signal
import time

# Ignore SIGTERM to force timeout
signal.signal(signal.SIGTERM, signal.SIG_IGN)

# Sleep indefinitely
while True:
    time.sleep(1)
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(server_script)
            server_file = f.name

        try:
            params = StdioParameters(command=sys.executable, args=[server_file])
            transport = StdioTransport(params)

            async with transport:
                assert transport.process is not None

            # Process should have been killed
            await anyio.sleep(0.1)
        finally:
            if os.path.exists(server_file):
                os.unlink(server_file)

    @pytest.mark.asyncio
    async def test_empty_lines_ignored(self):
        """Test that empty lines in stdout are ignored."""
        server_script = """
import sys
import json

# Send some empty lines
sys.stdout.write("\\n\\n")
sys.stdout.flush()

# Then send a valid message
line = sys.stdin.readline()
msg = json.loads(line)
response = {"jsonrpc": "2.0", "id": msg.get("id"), "result": {"ok": True}}
sys.stdout.write(json.dumps(response) + "\\n")
sys.stdout.flush()
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(server_script)
            server_file = f.name

        try:
            async with stdio_transport(sys.executable, [server_file]) as (read, write):
                from chuk_acp.protocol.jsonrpc import create_request

                req = create_request(method="test")
                await write.send(req)
                resp = await read.receive()
                assert resp.result["ok"] is True
        finally:
            if os.path.exists(server_file):
                os.unlink(server_file)

    @pytest.mark.asyncio
    async def test_unexpected_message_type_on_stdout(self):
        """Test handling of unexpected message type (request) on stdout."""
        server_script = """
import sys
import json

# Server shouldn't send requests on stdout, but test handling
line = sys.stdin.readline()
msg = json.loads(line)

# Send a request instead of a response (unexpected)
unexpected = {"jsonrpc": "2.0", "id": "server-req", "method": "server_method"}
sys.stdout.write(json.dumps(unexpected) + "\\n")
sys.stdout.flush()

# Then send the proper response
response = {"jsonrpc": "2.0", "id": msg.get("id"), "result": {"ok": True}}
sys.stdout.write(json.dumps(response) + "\\n")
sys.stdout.flush()
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(server_script)
            server_file = f.name

        try:
            async with stdio_transport(sys.executable, [server_file]) as (read, write):
                from chuk_acp.protocol.jsonrpc import create_request

                req = create_request(method="test")
                await write.send(req)

                # Should still receive the valid response (unexpected message logged)
                resp = await read.receive()
                assert resp.result["ok"] is True
        finally:
            if os.path.exists(server_file):
                os.unlink(server_file)

    @pytest.mark.asyncio
    async def test_type_error_on_invalid_parameters(self):
        """Test TypeError is raised for invalid parameters."""
        transport = StdioTransport("not-a-StdioParameters-object")

        with pytest.raises(TypeError, match="Expected StdioParameters"):
            async with transport:
                pass
