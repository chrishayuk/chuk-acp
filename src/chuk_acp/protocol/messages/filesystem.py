"""ACP file system messages (client methods)."""

from typing import Any
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream

from .send_message import send_message
from ..constants import METHOD_FS_READ_TEXT_FILE, METHOD_FS_WRITE_TEXT_FILE


async def send_fs_read_text_file(
    read_stream: MemoryObjectReceiveStream[Any],
    write_stream: MemoryObjectSendStream[Any],
    path: str,
    *,
    timeout: float = 60.0,
) -> str:
    """Read a text file (requires fs.readTextFile client capability).

    Args:
        read_stream: Stream to receive messages.
        write_stream: Stream to send messages.
        path: Absolute path to file. All file paths MUST be absolute.
        timeout: Request timeout in seconds.

    Returns:
        File contents as text.

    Raises:
        Exception: If reading fails.
    """
    params = {"path": path}

    result = await send_message(
        read_stream,
        write_stream,
        method=METHOD_FS_READ_TEXT_FILE,
        params=params,
        timeout=timeout,
    )

    return result["contents"]  # type: ignore[no-any-return]


async def send_fs_write_text_file(
    read_stream: MemoryObjectReceiveStream[Any],
    write_stream: MemoryObjectSendStream[Any],
    path: str,
    contents: str,
    *,
    timeout: float = 60.0,
) -> None:
    """Write a text file (requires fs.writeTextFile client capability).

    Args:
        read_stream: Stream to receive messages.
        write_stream: Stream to send messages.
        path: Absolute path to file. All file paths MUST be absolute.
        contents: File contents to write.
        timeout: Request timeout in seconds.

    Raises:
        Exception: If writing fails.
    """
    params = {
        "path": path,
        "contents": contents,
    }

    await send_message(
        read_stream,
        write_stream,
        method=METHOD_FS_WRITE_TEXT_FILE,
        params=params,
        timeout=timeout,
    )
