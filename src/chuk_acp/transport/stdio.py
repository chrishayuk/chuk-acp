"""Stdio transport for ACP - JSON-RPC over stdin/stdout."""

import json
import logging
import subprocess
from contextlib import asynccontextmanager
from types import TracebackType
from typing import Optional, List, Dict, Tuple, Union, AsyncGenerator

import anyio
from anyio.streams.memory import MemoryObjectSendStream, MemoryObjectReceiveStream

from .base import Transport, TransportParameters
from ..protocol.jsonrpc import (
    JSONRPCRequest,
    JSONRPCNotification,
    JSONRPCResponse,
    JSONRPCError,
    parse_message,
)

logger = logging.getLogger(__name__)


class StdioParameters(TransportParameters):
    """Parameters for stdio transport."""

    def __init__(
        self,
        command: str,
        args: Optional[List[str]] = None,
        env: Optional[Dict[str, str]] = None,
        cwd: Optional[str] = None,
    ):
        """Initialize stdio parameters.

        Args:
            command: Command to execute.
            args: Command arguments.
            env: Environment variables.
            cwd: Working directory.
        """
        self.command = command
        self.args = args or []
        self.env = env
        self.cwd = cwd


class StdioTransport(Transport):
    """Stdio transport for ACP communication."""

    def __init__(self, parameters: StdioParameters):
        super().__init__(parameters)
        self.process: Optional[anyio.abc.Process] = None
        self._read_stream: Optional[
            MemoryObjectReceiveStream[Union[JSONRPCResponse, JSONRPCError, JSONRPCNotification]]
        ] = None
        self._write_stream: Optional[
            MemoryObjectSendStream[Union[JSONRPCRequest, JSONRPCNotification]]
        ] = None
        self._task_group: Optional[anyio.abc.TaskGroup] = None

    async def get_streams(
        self,
    ) -> Tuple[
        MemoryObjectReceiveStream[Union[JSONRPCResponse, JSONRPCError, JSONRPCNotification]],
        MemoryObjectSendStream[Union[JSONRPCRequest, JSONRPCNotification]],
    ]:
        """Get read/write streams for message communication."""
        if not self._read_stream or not self._write_stream:
            raise RuntimeError("Transport not initialized. Use async context manager.")
        return self._read_stream, self._write_stream

    async def __aenter__(self) -> "StdioTransport":
        """Enter async context and start the subprocess."""
        params = self.parameters
        if not isinstance(params, StdioParameters):
            raise TypeError("Expected StdioParameters")

        # Create memory streams for communication
        read_send, read_recv = anyio.create_memory_object_stream[
            Union[JSONRPCResponse, JSONRPCError, JSONRPCNotification]
        ](100)
        write_send, write_recv = anyio.create_memory_object_stream[
            Union[JSONRPCRequest, JSONRPCNotification]
        ](100)

        self._read_stream = read_recv
        self._write_stream = write_send

        # Start process
        self.process = await anyio.open_process(
            [params.command] + params.args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=params.env,
            cwd=params.cwd,
        )

        # Start background tasks
        self._task_group = anyio.create_task_group()
        await self._task_group.__aenter__()

        self._task_group.start_soon(self._stdout_reader, read_send)
        self._task_group.start_soon(self._stdin_writer, write_recv)
        self._task_group.start_soon(self._stderr_logger)

        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit async context and cleanup."""
        # Close streams
        if self._write_stream:
            await self._write_stream.aclose()

        # Terminate process
        if self.process:
            try:
                self.process.terminate()
                with anyio.fail_after(5):
                    await self.process.wait()
            except TimeoutError:
                logger.warning("Process did not terminate, killing...")
                self.process.kill()
                await self.process.wait()
            except Exception as e:
                logger.error(f"Error terminating process: {e}")

        # Cancel background tasks
        if self._task_group:
            self._task_group.cancel_scope.cancel()
            try:
                await self._task_group.__aexit__(exc_type, exc_val, exc_tb)
            except Exception:
                pass

    async def _stdout_reader(
        self,
        send_stream: MemoryObjectSendStream[
            Union[JSONRPCResponse, JSONRPCError, JSONRPCNotification]
        ],
    ) -> None:
        """Read stdout and parse JSON-RPC messages."""
        try:
            assert self.process and self.process.stdout

            buffer = ""
            logger.debug("stdout reader started")

            async for chunk in self.process.stdout:
                if isinstance(chunk, bytes):
                    buffer += chunk.decode("utf-8")
                else:
                    buffer += chunk

                # Split on newlines
                lines = buffer.split("\n")
                buffer = lines[-1]

                for line in lines[:-1]:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        data = json.loads(line)
                        message = parse_message(data)

                        # Only send responses and notifications on read stream
                        if isinstance(
                            message, (JSONRPCResponse, JSONRPCError, JSONRPCNotification)
                        ):
                            await send_stream.send(message)
                        else:
                            logger.warning(f"Unexpected message type on stdout: {type(message)}")

                    except json.JSONDecodeError as e:
                        logger.error(f"JSON decode error: {e} - line: {line[:120]}")
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")

            logger.debug("stdout reader exiting")

        except Exception as e:
            logger.error(f"stdout reader error: {e}")
        finally:
            await send_stream.aclose()

    async def _stdin_writer(
        self,
        recv_stream: MemoryObjectReceiveStream[Union[JSONRPCRequest, JSONRPCNotification]],
    ) -> None:
        """Write JSON-RPC messages to stdin."""
        try:
            assert self.process and self.process.stdin

            logger.debug("stdin writer started")

            async for message in recv_stream:
                # Serialize message to JSON
                if hasattr(message, "model_dump"):
                    data = message.model_dump(exclude_none=True)
                else:
                    data = {
                        "jsonrpc": "2.0",
                        "method": getattr(message, "method", ""),
                        "id": getattr(message, "id", None),
                        "params": getattr(message, "params", None),
                    }

                line = json.dumps(data) + "\n"
                await self.process.stdin.send(line.encode("utf-8"))

            logger.debug("stdin writer exiting")

        except Exception as e:
            logger.error(f"stdin writer error: {e}")

    async def _stderr_logger(self) -> None:
        """Log stderr output."""
        try:
            assert self.process and self.process.stderr

            logger.debug("stderr logger started")

            async for chunk in self.process.stderr:
                if isinstance(chunk, bytes):
                    text = chunk.decode("utf-8", errors="replace")
                else:
                    text = chunk

                for line in text.splitlines():
                    if line.strip():
                        logger.info(f"[agent stderr] {line}")

            logger.debug("stderr logger exiting")

        except Exception as e:
            logger.error(f"stderr logger error: {e}")


@asynccontextmanager
async def stdio_transport(
    command: str,
    args: Optional[List[str]] = None,
    env: Optional[Dict[str, str]] = None,
    cwd: Optional[str] = None,
) -> AsyncGenerator[
    Tuple[
        MemoryObjectReceiveStream[Union[JSONRPCResponse, JSONRPCError, JSONRPCNotification]],
        MemoryObjectSendStream[Union[JSONRPCRequest, JSONRPCNotification]],
    ],
    None,
]:
    """Convenience context manager for stdio transport.

    Args:
        command: Command to execute.
        args: Command arguments.
        env: Environment variables.
        cwd: Working directory.

    Yields:
        Tuple of (read_stream, write_stream) for JSON-RPC messages.

    Example:
        ```python
        async with stdio_transport("python", ["agent.py"]) as (read, write):
            # Use streams
            await send_initialize(read, write, ...)
        ```
    """
    params = StdioParameters(command=command, args=args, env=env, cwd=cwd)
    transport = StdioTransport(params)

    async with transport:
        read_stream, write_stream = await transport.get_streams()
        yield read_stream, write_stream
