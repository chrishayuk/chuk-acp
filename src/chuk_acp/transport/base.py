"""Base transport interface for ACP communication."""

from abc import ABC, abstractmethod
from types import TracebackType
from typing import Tuple, Union
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream

from ..protocol.jsonrpc import (
    JSONRPCRequest,
    JSONRPCNotification,
    JSONRPCResponse,
    JSONRPCError,
)


class TransportParameters(ABC):
    """Base class for transport parameters."""

    pass


class Transport(ABC):
    """Base transport interface for ACP communication."""

    def __init__(self, parameters: TransportParameters):
        self.parameters = parameters

    @abstractmethod
    async def get_streams(
        self,
    ) -> Tuple[
        MemoryObjectReceiveStream[Union[JSONRPCResponse, JSONRPCError, JSONRPCNotification]],
        MemoryObjectSendStream[Union[JSONRPCRequest, JSONRPCNotification]],
    ]:
        """Get read/write streams for message communication.

        Returns:
            Tuple of (read_stream, write_stream) for JSON-RPC messages.
        """
        pass

    @abstractmethod
    async def __aenter__(self) -> "Transport":
        """Enter async context."""
        pass

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit async context."""
        pass
