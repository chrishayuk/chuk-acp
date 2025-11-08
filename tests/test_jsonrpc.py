"""Tests for JSON-RPC 2.0 implementation."""

from chuk_acp.protocol.jsonrpc import (
    JSONRPCRequest,
    JSONRPCNotification,
    JSONRPCResponse,
    JSONRPCError,
    create_request,
    create_notification,
    create_response,
    create_error_response,
    parse_message,
)


class TestJSONRPCRequest:
    """Test JSONRPCRequest class."""

    def test_create_request_with_id(self):
        """Test creating a request with explicit id."""
        req = create_request(method="test", params={"key": "value"}, id="123")
        assert req.jsonrpc == "2.0"
        assert req.id == "123"
        assert req.method == "test"
        assert req.params == {"key": "value"}

    def test_create_request_auto_id(self):
        """Test creating a request with auto-generated id."""
        req = create_request(method="test")
        assert req.jsonrpc == "2.0"
        assert req.id is not None
        assert isinstance(req.id, str)
        assert req.method == "test"

    def test_create_request_without_params(self):
        """Test creating a request without params."""
        req = create_request(method="test", id="456")
        assert req.params is None

    def test_request_serialization(self):
        """Test request serialization to dict."""
        req = create_request(method="initialize", params={"version": 1}, id="1")
        data = req.model_dump(exclude_none=True)
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == "1"
        assert data["method"] == "initialize"
        assert data["params"] == {"version": 1}

    def test_request_with_integer_id(self):
        """Test request with integer id."""
        req = JSONRPCRequest(jsonrpc="2.0", id=42, method="test")
        assert req.id == 42


class TestJSONRPCNotification:
    """Test JSONRPCNotification class."""

    def test_create_notification(self):
        """Test creating a notification."""
        notif = create_notification(method="session/update", params={"status": "progress"})
        assert notif.jsonrpc == "2.0"
        assert notif.method == "session/update"
        assert notif.params == {"status": "progress"}
        # Notifications should not have id field
        data = notif.model_dump(exclude_none=True)
        assert "id" not in data

    def test_create_notification_without_params(self):
        """Test creating a notification without params."""
        notif = create_notification(method="session/cancel")
        assert notif.params is None

    def test_notification_serialization(self):
        """Test notification serialization."""
        notif = create_notification(method="test/notify", params={"data": "test"})
        data = notif.model_dump(exclude_none=True)
        assert data["jsonrpc"] == "2.0"
        assert data["method"] == "test/notify"
        assert data["params"]["data"] == "test"
        assert "id" not in data


class TestJSONRPCResponse:
    """Test JSONRPCResponse class."""

    def test_create_response(self):
        """Test creating a success response."""
        resp = create_response(id="123", result={"status": "ok"})
        assert resp.jsonrpc == "2.0"
        assert resp.id == "123"
        assert resp.result == {"status": "ok"}

    def test_response_with_null_result(self):
        """Test response with null result (converts to empty dict)."""
        resp = create_response(id="456", result=None)
        assert resp.result == {}  # None converts to empty dict per spec

    def test_response_serialization(self):
        """Test response serialization."""
        resp = create_response(id=789, result={"data": "test"})
        data = resp.model_dump(exclude_none=True)
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 789
        assert data["result"]["data"] == "test"
        assert "error" not in data


class TestJSONRPCError:
    """Test JSONRPCError class."""

    def test_create_error_response(self):
        """Test creating an error response."""
        err = create_error_response(id="123", code=-32600, message="Invalid Request")
        assert err.jsonrpc == "2.0"
        assert err.id == "123"
        assert err.error["code"] == -32600
        assert err.error["message"] == "Invalid Request"

    def test_error_with_data(self):
        """Test error response with additional data."""
        err = create_error_response(
            id="456",
            code=-32603,
            message="Internal error",
            data={"details": "Something went wrong"},
        )
        assert err.error["data"] == {"details": "Something went wrong"}

    def test_error_without_data(self):
        """Test error response without data field."""
        err = create_error_response(id="789", code=-32601, message="Method not found")
        data = err.error
        assert "data" not in data

    def test_error_serialization(self):
        """Test error serialization."""
        err = create_error_response(id="100", code=-32700, message="Parse error")
        data = err.model_dump(exclude_none=True)
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == "100"
        assert data["error"]["code"] == -32700
        assert data["error"]["message"] == "Parse error"
        assert "result" not in data

    def test_error_with_null_id(self):
        """Test error response with null id (for parse errors)."""
        err = create_error_response(id=None, code=-32700, message="Parse error")
        assert err.id is None


class TestParseMessage:
    """Test message parsing."""

    def test_parse_request(self):
        """Test parsing a request message."""
        data = {"jsonrpc": "2.0", "id": "123", "method": "initialize", "params": {"version": 1}}
        msg = parse_message(data)
        assert isinstance(msg, JSONRPCRequest)
        assert msg.id == "123"
        assert msg.method == "initialize"

    def test_parse_notification(self):
        """Test parsing a notification message."""
        data = {"jsonrpc": "2.0", "method": "session/update", "params": {"status": "ok"}}
        msg = parse_message(data)
        assert isinstance(msg, JSONRPCNotification)
        assert msg.method == "session/update"

    def test_parse_response(self):
        """Test parsing a success response."""
        data = {"jsonrpc": "2.0", "id": "456", "result": {"status": "completed"}}
        msg = parse_message(data)
        assert isinstance(msg, JSONRPCResponse)
        assert msg.id == "456"
        assert msg.result == {"status": "completed"}

    def test_parse_error_response(self):
        """Test parsing an error response."""
        data = {
            "jsonrpc": "2.0",
            "id": "789",
            "error": {"code": -32601, "message": "Method not found"},
        }
        msg = parse_message(data)
        assert isinstance(msg, JSONRPCError)
        assert msg.id == "789"
        assert msg.error["code"] == -32601

    def test_parse_notification_without_params(self):
        """Test parsing notification without params."""
        data = {"jsonrpc": "2.0", "method": "cancel"}
        msg = parse_message(data)
        assert isinstance(msg, JSONRPCNotification)
        assert msg.params is None

    def test_parse_response_with_null_result(self):
        """Test parsing response with null result."""
        data = {"jsonrpc": "2.0", "id": "100", "result": None}
        msg = parse_message(data)
        assert isinstance(msg, JSONRPCResponse)
        assert msg.result is None

    def test_parse_error_with_data(self):
        """Test parsing error with additional data."""
        data = {
            "jsonrpc": "2.0",
            "id": "200",
            "error": {
                "code": -32603,
                "message": "Internal error",
                "data": {"details": "Stack overflow"},
            },
        }
        msg = parse_message(data)
        assert isinstance(msg, JSONRPCError)
        assert msg.error["data"]["details"] == "Stack overflow"

    def test_parse_request_with_integer_id(self):
        """Test parsing request with integer id."""
        data = {"jsonrpc": "2.0", "id": 42, "method": "test"}
        msg = parse_message(data)
        assert isinstance(msg, JSONRPCRequest)
        assert msg.id == 42


class TestJSONRPCCompliance:
    """Test JSON-RPC 2.0 protocol compliance."""

    def test_jsonrpc_version_required(self):
        """Test that jsonrpc field is always '2.0'."""
        req = create_request(method="test", id="1")
        notif = create_notification(method="test")
        resp = create_response(id="1", result={})
        err = create_error_response(id="1", code=-32600, message="Error")

        assert req.jsonrpc == "2.0"
        assert notif.jsonrpc == "2.0"
        assert resp.jsonrpc == "2.0"
        assert err.jsonrpc == "2.0"

    def test_request_requires_method(self):
        """Test that requests require method field."""
        req = create_request(method="test")
        assert req.method == "test"

    def test_request_requires_id(self):
        """Test that requests require id field."""
        req = create_request(method="test", id="123")
        assert req.id == "123"

    def test_notification_has_no_id(self):
        """Test that notifications don't have id in serialization."""
        notif = create_notification(method="test")
        data = notif.model_dump(exclude_none=True)
        assert "id" not in data

    def test_response_requires_id(self):
        """Test that responses require id field."""
        resp = create_response(id="123", result={})
        assert resp.id == "123"

    def test_error_codes_are_integers(self):
        """Test that error codes are integers."""
        err = create_error_response(id="1", code=-32600, message="Error")
        assert isinstance(err.error["code"], int)

    def test_standard_error_codes(self):
        """Test standard JSON-RPC error codes."""
        # Parse error
        err1 = create_error_response(id=None, code=-32700, message="Parse error")
        assert err1.error["code"] == -32700

        # Invalid request
        err2 = create_error_response(id="1", code=-32600, message="Invalid Request")
        assert err2.error["code"] == -32600

        # Method not found
        err3 = create_error_response(id="1", code=-32601, message="Method not found")
        assert err3.error["code"] == -32601

        # Invalid params
        err4 = create_error_response(id="1", code=-32602, message="Invalid params")
        assert err4.error["code"] == -32602

        # Internal error
        err5 = create_error_response(id="1", code=-32603, message="Internal error")
        assert err5.error["code"] == -32603


class TestMessageTypes:
    """Test different message type combinations."""

    def test_request_vs_notification_distinction(self):
        """Test that requests and notifications are distinct."""
        req = create_request(method="test", id="1")
        notif = create_notification(method="test")

        req_data = req.model_dump(exclude_none=True)
        notif_data = notif.model_dump(exclude_none=True)

        assert "id" in req_data
        assert "id" not in notif_data

    def test_response_vs_error_distinction(self):
        """Test that success and error responses are distinct."""
        success = create_response(id="1", result={"status": "ok"})
        error = create_error_response(id="1", code=-32600, message="Error")

        success_data = success.model_dump(exclude_none=True)
        error_data = error.model_dump(exclude_none=True)

        assert "result" in success_data
        assert "error" not in success_data
        assert "error" in error_data
        assert "result" not in error_data

    def test_batch_messages(self):
        """Test that multiple messages can be created."""
        messages = [
            create_request(method="method1", id="1"),
            create_request(method="method2", id="2"),
            create_notification(method="notify1"),
        ]

        assert len(messages) == 3
        assert isinstance(messages[0], JSONRPCRequest)
        assert isinstance(messages[1], JSONRPCRequest)
        assert isinstance(messages[2], JSONRPCNotification)


class TestJSONRPCExceptions:
    """Test JSON-RPC exception classes."""

    def test_jsonrpc_exception_base(self):
        """Test base JSONRPCException class."""
        from chuk_acp.protocol.jsonrpc import JSONRPCException

        exc = JSONRPCException(code=-32000, message="Custom error", data={"detail": "info"})
        assert exc.code == -32000
        assert exc.message == "Custom error"
        assert exc.data == {"detail": "info"}
        assert "JSON-RPC Error -32000" in str(exc)

    def test_jsonrpc_exception_to_dict(self):
        """Test JSONRPCException to_dict method."""
        from chuk_acp.protocol.jsonrpc import JSONRPCException

        exc = JSONRPCException(code=-32000, message="Error", data={"key": "value"})
        error_dict = exc.to_dict()

        assert error_dict["code"] == -32000
        assert error_dict["message"] == "Error"
        assert error_dict["data"] == {"key": "value"}

    def test_jsonrpc_exception_to_dict_without_data(self):
        """Test JSONRPCException to_dict without data field."""
        from chuk_acp.protocol.jsonrpc import JSONRPCException

        exc = JSONRPCException(code=-32000, message="Error")
        error_dict = exc.to_dict()

        assert error_dict["code"] == -32000
        assert error_dict["message"] == "Error"
        assert "data" not in error_dict

    def test_parse_error(self):
        """Test ParseError exception."""
        from chuk_acp.protocol.jsonrpc import ParseError

        exc = ParseError(data={"position": 10})
        assert exc.code == -32700
        assert exc.message == "Parse error"
        assert exc.data == {"position": 10}

    def test_parse_error_without_data(self):
        """Test ParseError without data."""
        from chuk_acp.protocol.jsonrpc import ParseError

        exc = ParseError()
        assert exc.code == -32700
        assert exc.message == "Parse error"
        assert exc.data is None

    def test_invalid_request(self):
        """Test InvalidRequest exception."""
        from chuk_acp.protocol.jsonrpc import InvalidRequest

        exc = InvalidRequest(data={"reason": "missing method"})
        assert exc.code == -32600
        assert exc.message == "Invalid Request"
        assert exc.data == {"reason": "missing method"}

    def test_invalid_request_without_data(self):
        """Test InvalidRequest without data."""
        from chuk_acp.protocol.jsonrpc import InvalidRequest

        exc = InvalidRequest()
        assert exc.code == -32600
        assert exc.data is None

    def test_method_not_found(self):
        """Test MethodNotFound exception."""
        from chuk_acp.protocol.jsonrpc import MethodNotFound

        exc = MethodNotFound(method="unknown_method")
        assert exc.code == -32601
        assert exc.message == "Method not found"
        assert exc.data == {"method": "unknown_method"}

    def test_invalid_params(self):
        """Test InvalidParams exception."""
        from chuk_acp.protocol.jsonrpc import InvalidParams

        exc = InvalidParams(data={"expected": "string", "got": "int"})
        assert exc.code == -32602
        assert exc.message == "Invalid params"
        assert exc.data == {"expected": "string", "got": "int"}

    def test_invalid_params_without_data(self):
        """Test InvalidParams without data."""
        from chuk_acp.protocol.jsonrpc import InvalidParams

        exc = InvalidParams()
        assert exc.code == -32602
        assert exc.data is None

    def test_internal_error(self):
        """Test InternalError exception."""
        from chuk_acp.protocol.jsonrpc import InternalError

        exc = InternalError(data={"trace": "stack trace"})
        assert exc.code == -32603
        assert exc.message == "Internal error"
        assert exc.data == {"trace": "stack trace"}

    def test_internal_error_without_data(self):
        """Test InternalError without data."""
        from chuk_acp.protocol.jsonrpc import InternalError

        exc = InternalError()
        assert exc.code == -32603
        assert exc.data is None


class TestPydanticValidation:
    """Test Pydantic-specific validation when available."""

    def test_error_validation_with_valid_error(self):
        """Test JSONRPCError with valid error structure."""
        from chuk_acp.protocol.jsonrpc import JSONRPCError

        error = JSONRPCError(
            jsonrpc="2.0", id="123", error={"code": -32600, "message": "Invalid Request"}
        )
        assert error.error["code"] == -32600
        assert error.error["message"] == "Invalid Request"

    def test_error_validation_with_data(self):
        """Test JSONRPCError with error data."""
        from chuk_acp.protocol.jsonrpc import JSONRPCError

        error = JSONRPCError(
            jsonrpc="2.0",
            id="123",
            error={
                "code": -32603,
                "message": "Internal error",
                "data": {"detail": "Database connection failed"},
            },
        )
        assert error.error["code"] == -32603
        assert error.error["data"]["detail"] == "Database connection failed"

    def test_config_dict_import(self):
        """Test ConfigDict is importable when Pydantic is available."""
        from chuk_acp.protocol.jsonrpc import PYDANTIC_AVAILABLE

        if PYDANTIC_AVAILABLE:
            # Should be able to import ConfigDict
            from chuk_acp.protocol.acp_pydantic_base import ConfigDict

            assert ConfigDict is not None
