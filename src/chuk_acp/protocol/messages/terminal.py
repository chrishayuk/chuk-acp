"""ACP terminal messages (client methods)."""

from typing import Optional, List, Dict, Any
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream

from .send_message import send_message, send_notification
from ..constants import (
    METHOD_TERMINAL_CREATE,
    METHOD_TERMINAL_OUTPUT,
    METHOD_TERMINAL_RELEASE,
    METHOD_TERMINAL_WAIT_FOR_EXIT,
    METHOD_TERMINAL_KILL,
)
from ..types import TerminalInfo, TerminalExit


async def send_terminal_create(
    read_stream: MemoryObjectReceiveStream[Any],
    write_stream: MemoryObjectSendStream[Any],
    command: str,
    args: Optional[List[str]] = None,
    cwd: Optional[str] = None,
    env: Optional[Dict[str, str]] = None,
    *,
    timeout: float = 60.0,
) -> TerminalInfo:
    """Create a terminal session (requires terminal.create client capability).

    Args:
        read_stream: Stream to receive messages.
        write_stream: Stream to send messages.
        command: Command to execute.
        args: Command arguments.
        cwd: Working directory (absolute path).
        env: Environment variables.
        timeout: Request timeout in seconds.

    Returns:
        TerminalInfo with session ID.

    Raises:
        Exception: If terminal creation fails.
    """
    params: Dict[str, Any] = {"command": command}

    if args:
        params["args"] = args
    if cwd:
        params["cwd"] = cwd
    if env:
        params["env"] = env

    result = await send_message(
        read_stream,
        write_stream,
        method=METHOD_TERMINAL_CREATE,
        params=params,
        timeout=timeout,
    )

    return TerminalInfo.model_validate(result)


async def send_terminal_output(
    write_stream: MemoryObjectSendStream[Any],
    terminal_id: str,
    output: str,
    stream: str = "stdout",
) -> None:
    """Send terminal output notification (requires terminal.output client capability).

    Args:
        write_stream: Stream to send messages.
        terminal_id: Terminal session ID.
        output: Output text.
        stream: Output stream ('stdout' or 'stderr').
    """
    params = {
        "id": terminal_id,
        "output": output,
        "stream": stream,
    }

    await send_notification(
        write_stream,
        method=METHOD_TERMINAL_OUTPUT,
        params=params,
    )


async def send_terminal_release(
    read_stream: MemoryObjectReceiveStream[Any],
    write_stream: MemoryObjectSendStream[Any],
    terminal_id: str,
    *,
    timeout: float = 60.0,
) -> None:
    """Release terminal control (requires terminal.release client capability).

    Args:
        read_stream: Stream to receive messages.
        write_stream: Stream to send messages.
        terminal_id: Terminal session ID.
        timeout: Request timeout in seconds.

    Raises:
        Exception: If releasing fails.
    """
    params = {"id": terminal_id}

    await send_message(
        read_stream,
        write_stream,
        method=METHOD_TERMINAL_RELEASE,
        params=params,
        timeout=timeout,
    )


async def send_terminal_wait_for_exit(
    read_stream: MemoryObjectReceiveStream[Any],
    write_stream: MemoryObjectSendStream[Any],
    terminal_id: str,
    *,
    timeout: float = 300.0,
) -> TerminalExit:
    """Wait for terminal process to exit (requires terminal.waitForExit client capability).

    Args:
        read_stream: Stream to receive messages.
        write_stream: Stream to send messages.
        terminal_id: Terminal session ID.
        timeout: Request timeout in seconds (longer for command execution).

    Returns:
        TerminalExit with exit code.

    Raises:
        Exception: If waiting fails.
    """
    params = {"id": terminal_id}

    result = await send_message(
        read_stream,
        write_stream,
        method=METHOD_TERMINAL_WAIT_FOR_EXIT,
        params=params,
        timeout=timeout,
    )

    return TerminalExit.model_validate(result)


async def send_terminal_kill(
    read_stream: MemoryObjectReceiveStream[Any],
    write_stream: MemoryObjectSendStream[Any],
    terminal_id: str,
    *,
    timeout: float = 60.0,
) -> None:
    """Kill a running terminal process (requires terminal.kill client capability).

    Args:
        read_stream: Stream to receive messages.
        write_stream: Stream to send messages.
        terminal_id: Terminal session ID.
        timeout: Request timeout in seconds.

    Raises:
        Exception: If killing fails.
    """
    params = {"id": terminal_id}

    await send_message(
        read_stream,
        write_stream,
        method=METHOD_TERMINAL_KILL,
        params=params,
        timeout=timeout,
    )
