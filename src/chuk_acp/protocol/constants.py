"""ACP protocol method name constants.

These constants define the standard method names used in the Agent Client Protocol.
Using constants instead of string literals helps prevent typos and makes the code
more maintainable.
"""

# Initialize and authentication
METHOD_INITIALIZE = "initialize"
METHOD_AUTHENTICATE = "authenticate"

# Session management
METHOD_SESSION_NEW = "session/new"
METHOD_SESSION_LOAD = "session/load"
METHOD_SESSION_PROMPT = "session/prompt"
METHOD_SESSION_UPDATE = "session/update"
METHOD_SESSION_SET_MODE = "session/set_mode"
METHOD_SESSION_CANCEL = "session/cancel"
METHOD_SESSION_REQUEST_PERMISSION = "session/request_permission"

# Filesystem operations
METHOD_FS_READ_TEXT_FILE = "fs/read_text_file"
METHOD_FS_WRITE_TEXT_FILE = "fs/write_text_file"

# Terminal operations
METHOD_TERMINAL_CREATE = "terminal/create"
METHOD_TERMINAL_OUTPUT = "terminal/output"
METHOD_TERMINAL_RELEASE = "terminal/release"
METHOD_TERMINAL_WAIT_FOR_EXIT = "terminal/wait_for_exit"
METHOD_TERMINAL_KILL = "terminal/kill"

__all__ = [
    # Initialize and authentication
    "METHOD_INITIALIZE",
    "METHOD_AUTHENTICATE",
    # Session management
    "METHOD_SESSION_NEW",
    "METHOD_SESSION_LOAD",
    "METHOD_SESSION_PROMPT",
    "METHOD_SESSION_UPDATE",
    "METHOD_SESSION_SET_MODE",
    "METHOD_SESSION_CANCEL",
    "METHOD_SESSION_REQUEST_PERMISSION",
    # Filesystem operations
    "METHOD_FS_READ_TEXT_FILE",
    "METHOD_FS_WRITE_TEXT_FILE",
    # Terminal operations
    "METHOD_TERMINAL_CREATE",
    "METHOD_TERMINAL_OUTPUT",
    "METHOD_TERMINAL_RELEASE",
    "METHOD_TERMINAL_WAIT_FOR_EXIT",
    "METHOD_TERMINAL_KILL",
]
