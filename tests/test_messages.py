"""Tests for ACP message modules (initialize, session, filesystem, terminal)."""

import anyio

from chuk_acp.protocol.messages.initialize import send_initialize, send_authenticate
from chuk_acp.protocol.messages.session import (
    send_session_new,
    send_session_load,
    send_session_prompt,
    send_session_set_mode,
    send_session_update,
    send_session_cancel,
    send_session_request_permission,
)
from chuk_acp.protocol.messages.filesystem import (
    send_fs_read_text_file,
    send_fs_write_text_file,
)
from chuk_acp.protocol.messages.terminal import (
    send_terminal_create,
    send_terminal_output,
    send_terminal_release,
    send_terminal_wait_for_exit,
    send_terminal_kill,
)
from chuk_acp.protocol.types import (
    ClientInfo,
    ClientCapabilities,
    TextContent,
)
from chuk_acp.protocol.jsonrpc import create_response


class TestInitializeMessages:
    """Test initialize message functions."""

    async def test_send_initialize(self):
        """Test send_initialize function."""
        send_stream, send_recv = anyio.create_memory_object_stream(10)
        recv_send, recv_stream = anyio.create_memory_object_stream(10)

        async def responder():
            req = await send_recv.receive()
            assert req.method == "initialize"
            assert req.params["protocolVersion"] == 1
            assert req.params["clientInfo"]["name"] == "test-client"

            resp = create_response(
                id=req.id,
                result={
                    "protocolVersion": 1,
                    "agentInfo": {"name": "test-agent", "version": "1.0.0"},
                    "agentCapabilities": {},
                },
            )
            await recv_send.send(resp)

        async with anyio.create_task_group() as tg:
            tg.start_soon(responder)

            result = await send_initialize(
                recv_stream,
                send_stream,
                protocol_version=1,
                client_info=ClientInfo(name="test-client", version="1.0.0"),
                capabilities=ClientCapabilities(),
            )

            assert result.protocolVersion == 1
            assert result.agentInfo.name == "test-agent"

    async def test_send_authenticate(self):
        """Test send_authenticate function."""
        send_stream, send_recv = anyio.create_memory_object_stream(10)
        recv_send, recv_stream = anyio.create_memory_object_stream(10)

        async def responder():
            req = await send_recv.receive()
            assert req.method == "authenticate"
            assert req.params["token"] == "test-token"

            resp = create_response(id=req.id, result={"authenticated": True})
            await recv_send.send(resp)

        async with anyio.create_task_group() as tg:
            tg.start_soon(responder)

            result = await send_authenticate(recv_stream, send_stream, token="test-token")

            assert result["authenticated"] is True


class TestSessionMessages:
    """Test session message functions."""

    async def test_send_session_new(self):
        """Test send_session_new function."""
        send_stream, send_recv = anyio.create_memory_object_stream(10)
        recv_send, recv_stream = anyio.create_memory_object_stream(10)

        async def responder():
            req = await send_recv.receive()
            assert req.method == "session/new"
            assert req.params["cwd"] == "/tmp"

            resp = create_response(id=req.id, result={"sessionId": "session-123"})
            await recv_send.send(resp)

        async with anyio.create_task_group() as tg:
            tg.start_soon(responder)

            result = await send_session_new(recv_stream, send_stream, cwd="/tmp")
            assert result.sessionId == "session-123"

    async def test_send_session_load(self):
        """Test send_session_load function."""
        send_stream, send_recv = anyio.create_memory_object_stream(10)
        recv_send, recv_stream = anyio.create_memory_object_stream(10)

        async def responder():
            req = await send_recv.receive()
            assert req.method == "session/load"
            assert req.params["sessionId"] == "session-123"
            assert req.params["cwd"] == "/tmp"

            resp = create_response(id=req.id, result={"sessionId": "session-123"})
            await recv_send.send(resp)

        async with anyio.create_task_group() as tg:
            tg.start_soon(responder)

            result = await send_session_load(
                recv_stream, send_stream, session_id="session-123", cwd="/tmp"
            )
            assert result["sessionId"] == "session-123"

    async def test_send_session_prompt(self):
        """Test send_session_prompt function."""
        send_stream, send_recv = anyio.create_memory_object_stream(10)
        recv_send, recv_stream = anyio.create_memory_object_stream(10)

        async def responder():
            req = await send_recv.receive()
            assert req.method == "session/prompt"
            assert req.params["sessionId"] == "session-123"
            assert len(req.params["prompt"]) == 1

            resp = create_response(id=req.id, result={"stopReason": "end_turn"})
            await recv_send.send(resp)

        async with anyio.create_task_group() as tg:
            tg.start_soon(responder)

            result = await send_session_prompt(
                recv_stream,
                send_stream,
                session_id="session-123",
                prompt=[TextContent(text="Hello")],
            )
            assert result.stopReason == "end_turn"

    async def test_send_session_set_mode(self):
        """Test send_session_set_mode function."""
        send_stream, send_recv = anyio.create_memory_object_stream(10)
        recv_send, recv_stream = anyio.create_memory_object_stream(10)

        async def responder():
            req = await send_recv.receive()
            assert req.method == "session/set_mode"
            assert req.params["sessionId"] == "session-123"
            assert req.params["mode"] == "code"

            resp = create_response(id=req.id, result={})
            await recv_send.send(resp)

        async with anyio.create_task_group() as tg:
            tg.start_soon(responder)

            await send_session_set_mode(
                recv_stream, send_stream, session_id="session-123", mode="code"
            )

    async def test_send_session_update(self):
        """Test send_session_update notification."""
        send_stream, recv_stream = anyio.create_memory_object_stream(10)

        await send_session_update(
            send_stream,
            session_id="session-123",
            agent_message_chunk=TextContent(text="Processing..."),
        )

        notif = await recv_stream.receive()
        assert notif.method == "session/update"
        assert notif.params["sessionId"] == "session-123"

    async def test_send_session_cancel(self):
        """Test send_session_cancel notification."""
        send_stream, recv_stream = anyio.create_memory_object_stream(10)

        await send_session_cancel(send_stream, session_id="session-123")

        notif = await recv_stream.receive()
        assert notif.method == "session/cancel"
        assert notif.params["sessionId"] == "session-123"

    async def test_send_session_request_permission(self):
        """Test send_session_request_permission function."""
        send_stream, send_recv = anyio.create_memory_object_stream(10)
        recv_send, recv_stream = anyio.create_memory_object_stream(10)

        async def responder():
            req = await send_recv.receive()
            assert req.method == "session/request_permission"
            assert req.params["sessionId"] == "session-123"
            assert req.params["action"] == "read_file"  # Spread into params

            resp = create_response(id=req.id, result={"id": "perm-123", "granted": True})
            await recv_send.send(resp)

        async with anyio.create_task_group() as tg:
            tg.start_soon(responder)

            from chuk_acp.protocol.types import PermissionRequest

            perm_req = PermissionRequest(action="read_file", description="Read config file")

            result = await send_session_request_permission(
                recv_stream, send_stream, session_id="session-123", request=perm_req
            )
            assert result.granted is True


class TestFilesystemMessages:
    """Test filesystem message functions."""

    async def test_send_fs_read_text_file(self):
        """Test send_fs_read_text_file function."""
        send_stream, send_recv = anyio.create_memory_object_stream(10)
        recv_send, recv_stream = anyio.create_memory_object_stream(10)

        async def responder():
            req = await send_recv.receive()
            assert req.method == "fs/read_text_file"
            assert req.params["path"] == "/tmp/test.txt"

            resp = create_response(id=req.id, result={"contents": "file contents"})
            await recv_send.send(resp)

        async with anyio.create_task_group() as tg:
            tg.start_soon(responder)

            result = await send_fs_read_text_file(recv_stream, send_stream, path="/tmp/test.txt")
            assert result == "file contents"

    async def test_send_fs_write_text_file(self):
        """Test send_fs_write_text_file function."""
        send_stream, send_recv = anyio.create_memory_object_stream(10)
        recv_send, recv_stream = anyio.create_memory_object_stream(10)

        async def responder():
            req = await send_recv.receive()
            assert req.method == "fs/write_text_file"
            assert req.params["path"] == "/tmp/test.txt"
            assert req.params["contents"] == "new contents"

            resp = create_response(id=req.id, result={})
            await recv_send.send(resp)

        async with anyio.create_task_group() as tg:
            tg.start_soon(responder)

            await send_fs_write_text_file(
                recv_stream, send_stream, path="/tmp/test.txt", contents="new contents"
            )


class TestTerminalMessages:
    """Test terminal message functions."""

    async def test_send_terminal_create(self):
        """Test send_terminal_create function."""
        send_stream, send_recv = anyio.create_memory_object_stream(10)
        recv_send, recv_stream = anyio.create_memory_object_stream(10)

        async def responder():
            req = await send_recv.receive()
            assert req.method == "terminal/create"
            assert req.params["command"] == "bash"

            resp = create_response(id=req.id, result={"id": "term-123"})
            await recv_send.send(resp)

        async with anyio.create_task_group() as tg:
            tg.start_soon(responder)

            result = await send_terminal_create(
                recv_stream, send_stream, command="bash", args=["-c", "echo hello"]
            )
            assert result.id == "term-123"

    async def test_send_terminal_output(self):
        """Test send_terminal_output notification."""
        send_stream, recv_stream = anyio.create_memory_object_stream(10)

        await send_terminal_output(
            send_stream, terminal_id="term-123", output="Hello, world!", stream="stdout"
        )

        notif = await recv_stream.receive()
        assert notif.method == "terminal/output"
        assert notif.params["id"] == "term-123"
        assert notif.params["output"] == "Hello, world!"

    async def test_send_terminal_release(self):
        """Test send_terminal_release function."""
        send_stream, send_recv = anyio.create_memory_object_stream(10)
        recv_send, recv_stream = anyio.create_memory_object_stream(10)

        async def responder():
            req = await send_recv.receive()
            assert req.method == "terminal/release"
            assert req.params["id"] == "term-123"

            resp = create_response(id=req.id, result={})
            await recv_send.send(resp)

        async with anyio.create_task_group() as tg:
            tg.start_soon(responder)

            await send_terminal_release(recv_stream, send_stream, terminal_id="term-123")

    async def test_send_terminal_wait_for_exit(self):
        """Test send_terminal_wait_for_exit function."""
        send_stream, send_recv = anyio.create_memory_object_stream(10)
        recv_send, recv_stream = anyio.create_memory_object_stream(10)

        async def responder():
            req = await send_recv.receive()
            assert req.method == "terminal/wait_for_exit"
            assert req.params["id"] == "term-123"

            resp = create_response(id=req.id, result={"exitCode": 0})
            await recv_send.send(resp)

        async with anyio.create_task_group() as tg:
            tg.start_soon(responder)

            result = await send_terminal_wait_for_exit(
                recv_stream, send_stream, terminal_id="term-123"
            )
            assert result.exitCode == 0

    async def test_send_terminal_kill(self):
        """Test send_terminal_kill function."""
        send_stream, send_recv = anyio.create_memory_object_stream(10)
        recv_send, recv_stream = anyio.create_memory_object_stream(10)

        async def responder():
            req = await send_recv.receive()
            assert req.method == "terminal/kill"
            assert req.params["id"] == "term-123"

            resp = create_response(id=req.id, result={})
            await recv_send.send(resp)

        async with anyio.create_task_group() as tg:
            tg.start_soon(responder)

            await send_terminal_kill(recv_stream, send_stream, terminal_id="term-123")
