"""JSON-RPC 2.0 implementation for ACP."""

from typing import Any, Optional, Union, Literal, Dict, List
from .acp_pydantic_base import AcpPydanticBase, PYDANTIC_AVAILABLE

if PYDANTIC_AVAILABLE:
    from .acp_pydantic_base import ConfigDict

# JSON-RPC types
RequestId = Union[str, int]


# JSON-RPC Exception types
class JSONRPCException(Exception):
    """Base exception for JSON-RPC errors."""

    def __init__(self, code: int, message: str, data: Optional[Any] = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(f"JSON-RPC Error {code}: {message}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to JSON-RPC error object."""
        error: Dict[str, Any] = {
            "code": self.code,
            "message": self.message,
        }
        if self.data is not None:
            error["data"] = self.data
        return error


# Standard JSON-RPC error codes
class ParseError(JSONRPCException):
    """Invalid JSON was received."""

    def __init__(self, data: Optional[Any] = None):
        super().__init__(-32700, "Parse error", data)


class InvalidRequest(JSONRPCException):
    """The JSON sent is not a valid Request object."""

    def __init__(self, data: Optional[Any] = None):
        super().__init__(-32600, "Invalid Request", data)


class MethodNotFound(JSONRPCException):
    """The method does not exist / is not available."""

    def __init__(self, method: str):
        super().__init__(-32601, "Method not found", {"method": method})


class InvalidParams(JSONRPCException):
    """Invalid method parameter(s)."""

    def __init__(self, data: Optional[Any] = None):
        super().__init__(-32602, "Invalid params", data)


class InternalError(JSONRPCException):
    """Internal JSON-RPC error."""

    def __init__(self, data: Optional[Any] = None):
        super().__init__(-32603, "Internal error", data)


# Message types
class JSONRPCRequest(AcpPydanticBase):
    """JSON-RPC 2.0 Request message that expects a response."""

    jsonrpc: Literal["2.0"] = "2.0"
    id: RequestId
    method: str
    params: Optional[Dict[str, Any]] = None

    if PYDANTIC_AVAILABLE:
        model_config = ConfigDict(extra="allow")


class JSONRPCNotification(AcpPydanticBase):
    """JSON-RPC 2.0 Notification message (no response expected)."""

    jsonrpc: Literal["2.0"] = "2.0"
    method: str
    params: Optional[Dict[str, Any]] = None

    if PYDANTIC_AVAILABLE:
        model_config = ConfigDict(extra="allow")


class JSONRPCResponse(AcpPydanticBase):
    """JSON-RPC 2.0 Response message (success)."""

    jsonrpc: Literal["2.0"] = "2.0"
    id: RequestId
    result: Any  # Can be any JSON-serializable value

    if PYDANTIC_AVAILABLE:
        model_config = ConfigDict(extra="allow")


class JSONRPCError(AcpPydanticBase):
    """JSON-RPC 2.0 Error response message."""

    jsonrpc: Literal["2.0"] = "2.0"
    id: Optional[RequestId]
    error: Dict[str, Any]  # {code: int, message: str, data?: any}

    if PYDANTIC_AVAILABLE:
        model_config = ConfigDict(extra="allow")

        def model_post_init(self, __context: Any) -> None:
            """Validate error structure."""
            if self.error:
                if "code" not in self.error or not isinstance(self.error["code"], int):
                    raise ValueError("Error must have an integer 'code' field")
                if "message" not in self.error or not isinstance(self.error["message"], str):
                    raise ValueError("Error must have a string 'message' field")


# For batch support (ACP doesn't currently use batching, but included for completeness)
JSONRPCBatchRequest = List[Union[JSONRPCRequest, JSONRPCNotification]]
JSONRPCBatchResponse = List[Union[JSONRPCResponse, JSONRPCError]]

# Union type for any valid JSON-RPC message
JSONRPCMessage = Union[
    JSONRPCRequest,
    JSONRPCNotification,
    JSONRPCResponse,
    JSONRPCError,
    JSONRPCBatchRequest,
    JSONRPCBatchResponse,
]


# Helper functions to create messages
def create_request(
    method: str,
    params: Optional[Dict[str, Any]] = None,
    id: Optional[RequestId] = None,
) -> JSONRPCRequest:
    """Create a request message with auto-generated ID if not provided."""
    if id is None:
        import uuid

        id = str(uuid.uuid4())

    return JSONRPCRequest(jsonrpc="2.0", id=id, method=method, params=params)


def create_notification(
    method: str, params: Optional[Dict[str, Any]] = None
) -> JSONRPCNotification:
    """Create a notification message."""
    return JSONRPCNotification(jsonrpc="2.0", method=method, params=params)


def create_response(id: RequestId, result: Any = None) -> JSONRPCResponse:
    """Create a successful response message."""
    if result is None:
        result = {}  # Empty result as per spec
    return JSONRPCResponse(jsonrpc="2.0", id=id, result=result)


def create_error_response(
    id: Optional[RequestId], code: int, message: str, data: Any = None
) -> JSONRPCError:
    """Create an error response message."""
    error = {"code": code, "message": message}
    if data is not None:
        error["data"] = data
    return JSONRPCError(jsonrpc="2.0", id=id, error=error)


def parse_message(
    data: Union[Dict[str, Any], List[Any]],
) -> Union[JSONRPCRequest, JSONRPCNotification, JSONRPCResponse, JSONRPCError, List[Any]]:
    """Parse incoming JSON data into appropriate JSON-RPC message type.

    Args:
        data: Parsed JSON data (dict for single message, list for batch)

    Returns:
        Appropriate JSONRPCMessage subtype

    Raises:
        InvalidRequest: If the message doesn't match any valid JSON-RPC format
    """
    # Handle batch messages
    if isinstance(data, list):
        messages = []
        for item in data:
            messages.append(parse_message(item))
        return messages

    # Single message
    if not isinstance(data, dict):
        raise InvalidRequest("Message must be a dict or list")

    # Check required fields
    if data.get("jsonrpc") != "2.0":
        raise InvalidRequest("Missing or invalid jsonrpc version")

    has_id = "id" in data
    has_method = "method" in data
    has_result = "result" in data
    has_error = "error" in data

    # Determine message type based on fields
    if has_method and has_id:
        # Request
        return JSONRPCRequest.model_validate(data)
    elif has_method and not has_id:
        # Notification
        return JSONRPCNotification.model_validate(data)
    elif has_id and has_result and not has_error:
        # Success response
        return JSONRPCResponse.model_validate(data)
    elif has_id and has_error and not has_result:
        # Error response
        return JSONRPCError.model_validate(data)
    else:
        raise InvalidRequest("Invalid JSON-RPC message structure")
