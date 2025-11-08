"""Tests for send_message core messaging infrastructure."""

import pytest
import anyio

from chuk_acp.protocol.messages.send_message import (
    send_message,
    send_notification,
    CancellationToken,
    CancelledError,
)
from chuk_acp.protocol.jsonrpc import (
    create_response,
    create_error_response,
)


class TestCancellationToken:
    """Test CancellationToken class."""

    def test_create_token(self):
        """Test creating a cancellation token."""
        token = CancellationToken()
        assert not token.is_cancelled

    def test_cancel_token(self):
        """Test cancelling a token."""
        token = CancellationToken()
        token.cancel()
        assert token.is_cancelled

    def test_add_callback(self):
        """Test add_callback is called on cancel."""
        token = CancellationToken()
        called = []

        def callback():
            called.append(True)

        token.add_callback(callback)
        assert not called

        token.cancel()
        assert called == [True]

    def test_multiple_callbacks(self):
        """Test multiple callbacks are called."""
        token = CancellationToken()
        calls = []

        token.add_callback(lambda: calls.append(1))
        token.add_callback(lambda: calls.append(2))
        token.add_callback(lambda: calls.append(3))

        token.cancel()
        assert calls == [1, 2, 3]

    def test_callback_after_cancel(self):
        """Test callback added after cancel is called immediately."""
        token = CancellationToken()
        token.cancel()

        called = []
        token.add_callback(lambda: called.append(True))
        assert called == [True]


class TestSendNotification:
    """Test send_notification function."""

    async def test_send_notification(self):
        """Test sending a notification."""
        send_stream, recv_stream = anyio.create_memory_object_stream(10)

        await send_notification(send_stream, method="test/notify", params={"data": "test"})

        # Receive the message
        msg = await recv_stream.receive()
        assert msg.method == "test/notify"
        assert msg.params == {"data": "test"}

    async def test_send_notification_without_params(self):
        """Test sending a notification without params."""
        send_stream, recv_stream = anyio.create_memory_object_stream(10)

        await send_notification(send_stream, method="test/notify")

        msg = await recv_stream.receive()
        assert msg.method == "test/notify"
        assert msg.params is None

    async def test_send_notification_with_meta(self):
        """Test sending a notification with _meta field."""
        send_stream, recv_stream = anyio.create_memory_object_stream(10)

        await send_notification(
            send_stream, method="test/notify", params={"data": "test", "_meta": {"version": "1.0"}}
        )

        msg = await recv_stream.receive()
        assert msg.params["_meta"]["version"] == "1.0"


class TestSendMessage:
    """Test send_message function."""

    async def test_send_message_success(self):
        """Test sending a message and receiving success response."""
        send_stream, send_recv = anyio.create_memory_object_stream(10)
        recv_send, recv_stream = anyio.create_memory_object_stream(10)

        # Start a task to respond
        async def responder():
            # Receive the request
            req = await send_recv.receive()
            # Send back a response
            resp = create_response(id=req.id, result={"status": "ok"})
            await recv_send.send(resp)

        async with anyio.create_task_group() as tg:
            tg.start_soon(responder)

            # Send message
            result = await send_message(
                recv_stream, send_stream, method="test/method", params={"key": "value"}
            )

            assert result == {"status": "ok"}

    async def test_send_message_with_explicit_id(self):
        """Test sending a message with explicit ID."""
        send_stream, send_recv = anyio.create_memory_object_stream(10)
        recv_send, recv_stream = anyio.create_memory_object_stream(10)

        async def responder():
            req = await send_recv.receive()
            assert req.id == "custom-id-123"
            resp = create_response(id=req.id, result={"done": True})
            await recv_send.send(resp)

        async with anyio.create_task_group() as tg:
            tg.start_soon(responder)

            result = await send_message(
                recv_stream, send_stream, method="test", message_id="custom-id-123"
            )

            assert result == {"done": True}

    async def test_send_message_error_response(self):
        """Test sending a message and receiving error response."""
        send_stream, send_recv = anyio.create_memory_object_stream(10)
        recv_send, recv_stream = anyio.create_memory_object_stream(10)

        async def responder():
            req = await send_recv.receive()
            err = create_error_response(id=req.id, code=-32601, message="Method not found")
            await recv_send.send(err)

        async with anyio.create_task_group() as tg:
            tg.start_soon(responder)

            with pytest.raises(Exception) as exc_info:
                await send_message(recv_stream, send_stream, method="unknown/method")

            assert "Method not found" in str(exc_info.value)

    async def test_send_message_timeout(self):
        """Test send_message timeout."""
        send_stream, send_recv = anyio.create_memory_object_stream(10)
        recv_send, recv_stream = anyio.create_memory_object_stream(10)

        # Don't send a response - let it timeout
        with pytest.raises(TimeoutError):
            await send_message(recv_stream, send_stream, method="test", timeout=0.1)

    async def test_send_message_with_cancellation_token(self):
        """Test send_message respects cancellation token."""
        send_stream, send_recv = anyio.create_memory_object_stream(10)
        recv_send, recv_stream = anyio.create_memory_object_stream(10)

        token = CancellationToken()
        token.cancel()  # Pre-cancel the token

        # send_message checks for cancellation and should raise
        with pytest.raises(CancelledError):
            await send_message(
                recv_stream, send_stream, method="test", cancellation_token=token, timeout=1.0
            )

    async def test_send_message_filters_unrelated_responses(self):
        """Test that send_message filters out responses for other requests."""
        send_stream, send_recv = anyio.create_memory_object_stream(10)
        recv_send, recv_stream = anyio.create_memory_object_stream(10)

        async def responder():
            req = await send_recv.receive()

            # Send unrelated response first
            unrelated = create_response(id="other-request", result={"unrelated": True})
            await recv_send.send(unrelated)

            # Then send the correct response
            resp = create_response(id=req.id, result={"correct": True})
            await recv_send.send(resp)

        async with anyio.create_task_group() as tg:
            tg.start_soon(responder)

            result = await send_message(recv_stream, send_stream, method="test")

            # Should get the correct response, not the unrelated one
            assert result == {"correct": True}

    async def test_send_message_without_params(self):
        """Test sending a message without params."""
        send_stream, send_recv = anyio.create_memory_object_stream(10)
        recv_send, recv_stream = anyio.create_memory_object_stream(10)

        async def responder():
            req = await send_recv.receive()
            assert req.params is None
            resp = create_response(id=req.id, result={})
            await recv_send.send(resp)

        async with anyio.create_task_group() as tg:
            tg.start_soon(responder)

            result = await send_message(recv_stream, send_stream, method="test")

            assert result == {}

    async def test_send_message_with_complex_params(self):
        """Test sending a message with complex nested params."""
        send_stream, send_recv = anyio.create_memory_object_stream(10)
        recv_send, recv_stream = anyio.create_memory_object_stream(10)

        complex_params = {
            "nested": {"data": ["a", "b", "c"], "config": {"enabled": True, "count": 42}},
            "_meta": {"timestamp": "2024-01-01"},
        }

        async def responder():
            req = await send_recv.receive()
            assert req.params == complex_params
            resp = create_response(id=req.id, result={"processed": True})
            await recv_send.send(resp)

        async with anyio.create_task_group() as tg:
            tg.start_soon(responder)

            result = await send_message(
                recv_stream, send_stream, method="test", params=complex_params
            )

            assert result == {"processed": True}


class TestMessageIntegration:
    """Integration tests for messaging."""

    async def test_multiple_concurrent_messages(self):
        """Test sending multiple messages concurrently."""
        send_stream, send_recv = anyio.create_memory_object_stream(100)
        recv_send, recv_stream = anyio.create_memory_object_stream(100)

        results = []

        async def responder():
            # Respond to all requests
            for _ in range(5):
                req = await send_recv.receive()
                resp = create_response(id=req.id, result={"method": req.method})
                await recv_send.send(resp)

        async def sender(method: str):
            result = await send_message(recv_stream, send_stream, method=method, timeout=1.0)
            results.append(result)

        async with anyio.create_task_group() as tg:
            tg.start_soon(responder)

            # Send multiple concurrent requests
            tg.start_soon(sender, "method1")
            tg.start_soon(sender, "method2")
            tg.start_soon(sender, "method3")
            tg.start_soon(sender, "method4")
            tg.start_soon(sender, "method5")

        # Check we got all responses
        assert len(results) == 5
        methods = [r["method"] for r in results]
        assert set(methods) == {"method1", "method2", "method3", "method4", "method5"}

    async def test_notification_and_request_interleaved(self):
        """Test that notifications and requests can be interleaved."""
        send_stream, send_recv = anyio.create_memory_object_stream(10)
        recv_send, recv_stream = anyio.create_memory_object_stream(10)

        notifications_received = []

        async def responder():
            # Receive notification
            notif1 = await send_recv.receive()
            notifications_received.append(notif1.method)

            # Receive request and respond
            req = await send_recv.receive()
            resp = create_response(id=req.id, result={"ok": True})
            await recv_send.send(resp)

            # Receive another notification
            notif2 = await send_recv.receive()
            notifications_received.append(notif2.method)

        async with anyio.create_task_group() as tg:
            tg.start_soon(responder)

            # Send notification
            await send_notification(send_stream, method="notify1")

            # Send request
            result = await send_message(recv_stream, send_stream, method="request1")

            # Send another notification
            await send_notification(send_stream, method="notify2")

            # Wait a bit for all messages to be processed
            await anyio.sleep(0.1)

            assert result == {"ok": True}
            assert notifications_received == ["notify1", "notify2"]


class TestSendMessageErrorHandling:
    """Test error handling in send_message and send_notification."""

    @pytest.mark.asyncio
    async def test_send_message_send_failure(self):
        """Test send_message when write_stream.send() fails."""
        from chuk_acp.protocol.messages.send_message import send_message

        send_stream, _ = anyio.create_memory_object_stream(1)
        recv_stream, _ = anyio.create_memory_object_stream(1)

        # Close the send stream to cause send failure
        await send_stream.aclose()

        with pytest.raises(anyio.ClosedResourceError):
            await send_message(recv_stream, send_stream, method="test_method", timeout=1.0)

    @pytest.mark.asyncio
    async def test_send_notification_send_failure(self):
        """Test send_notification when write_stream.send() fails."""
        from chuk_acp.protocol.messages.send_message import send_notification

        send_stream, _ = anyio.create_memory_object_stream(1)

        # Close the stream to cause send failure
        await send_stream.aclose()

        with pytest.raises(anyio.ClosedResourceError):
            await send_notification(send_stream, method="test_notification")

    @pytest.mark.asyncio
    async def test_cancellation_callback_error(self):
        """Test that errors in cancellation callbacks are handled gracefully."""
        from chuk_acp.protocol.messages.send_message import CancellationToken

        def failing_callback():
            raise RuntimeError("Callback failed!")

        token = CancellationToken()
        token.add_callback(failing_callback)

        # Cancel should not raise even though callback raises
        # (errors are logged but not propagated)
        token.cancel()

        assert token.is_cancelled

    @pytest.mark.asyncio
    async def test_send_message_with_notification_in_stream(self):
        """Test send_message when receiving notifications before the response."""
        from chuk_acp.protocol.messages.send_message import send_message
        from chuk_acp.protocol.jsonrpc import (
            create_response,
            create_notification,
        )

        send_stream, send_recv = anyio.create_memory_object_stream(10)
        recv_send, recv_stream = anyio.create_memory_object_stream(10)

        async def responder():
            # Receive the request
            req = await send_recv.receive()

            # Send a notification first (should be ignored)
            notif = create_notification(method="some_event", params={"data": "test"})
            await recv_send.send(notif)

            # Then send the actual response
            resp = create_response(id=req.id, result={"success": True})
            await recv_send.send(resp)

        async with anyio.create_task_group() as tg:
            tg.start_soon(responder)

            result = await send_message(recv_stream, send_stream, method="test_method", timeout=2.0)

            assert result == {"success": True}
