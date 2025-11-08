# chuk-acp Implementation

A pure Python implementation of the Agent Client Protocol (ACP) following the chuk-mcp architectural patterns.

## Implementation Status

✅ **Complete** - Core protocol library is functional and ready for use.

### What's Implemented

#### 1. JSON-RPC 2.0 Foundation (`src/chuk_acp/protocol/jsonrpc.py`)
- ✅ Request, Notification, Response, Error message types
- ✅ Message parsing and validation
- ✅ Helper functions for creating messages
- ✅ Optional Pydantic validation support

#### 2. Protocol Types (`src/chuk_acp/protocol/types/`)
Organized into separate modules following chuk-mcp pattern:

- ✅ **info.py**: AgentInfo, ClientInfo
- ✅ **content.py**: TextContent, ImageContent, AudioContent, EmbeddedResource, ResourceLink, Annotations
- ✅ **capabilities.py**: ClientCapabilities, AgentCapabilities with detailed sub-capabilities
- ✅ **mcp_servers.py**: StdioMCPServer, HttpMCPServer, SseMCPServer
- ✅ **session.py**: SessionMode, StopReason, Location
- ✅ **tools.py**: ToolCall, ToolCallUpdate, ToolCallStatus
- ✅ **plan.py**: Plan, Task, TaskStatus
- ✅ **permission.py**: PermissionRequest, PermissionResponse
- ✅ **terminal.py**: TerminalInfo, TerminalOutput, TerminalExit

#### 3. Protocol Messages (`src/chuk_acp/protocol/messages/`)

**Core Messaging:**
- ✅ `send_message()`: Send request and await response
- ✅ `send_notification()`: Send one-way notification
- ✅ `CancellationToken`: Support for cancelling requests

**Agent Methods (requests to agent):**
- ✅ `send_initialize()`: Initialize connection with capability negotiation
- ✅ `send_authenticate()`: Optional authentication
- ✅ `send_session_new()`: Create new session
- ✅ `send_session_load()`: Load existing session (optional capability)
- ✅ `send_session_prompt()`: Send user prompt to agent
- ✅ `send_session_set_mode()`: Change session mode (optional capability)
- ✅ `send_session_cancel()`: Cancel ongoing operation (notification)

**Client Methods (requests from agent to client):**
- ✅ `send_session_update()`: Agent sends progress updates (notification)
- ✅ `send_session_request_permission()`: Request user permission
- ✅ `send_fs_read_text_file()`: Read file (optional capability)
- ✅ `send_fs_write_text_file()`: Write file (optional capability)
- ✅ `send_terminal_create()`: Create terminal session (optional capability)
- ✅ `send_terminal_output()`: Send terminal output (notification, optional capability)
- ✅ `send_terminal_release()`: Release terminal control (optional capability)
- ✅ `send_terminal_wait_for_exit()`: Wait for process exit (optional capability)
- ✅ `send_terminal_kill()`: Kill running process (optional capability)

#### 4. Transport Layer (`src/chuk_acp/transport/`)
- ✅ **base.py**: Abstract Transport interface
- ✅ **stdio.py**: Full stdio transport implementation
  - Process spawning and management
  - Newline-delimited JSON-RPC over stdin/stdout
  - Background tasks for reading/writing
  - Automatic stderr logging
  - Clean async context manager API
- ✅ **stdio_transport()**: Convenience context manager

#### 5. Examples (`examples/`)
- ✅ **simple_client.py**: Complete client example
- ✅ **echo_agent.py**: Minimal echo agent for testing
- ✅ **README.md**: Examples documentation

#### 6. Documentation
- ✅ **README.md**: Library overview and quick start
- ✅ **IMPLEMENTATION.md**: This file
- ✅ **pyproject.toml**: Package configuration
- ✅ **.gitignore**: Python gitignore

## Architecture

```
chuk-acp/
├── src/chuk_acp/
│   ├── __init__.py                    # Main exports
│   ├── protocol/
│   │   ├── __init__.py
│   │   ├── acp_pydantic_base.py       # Optional Pydantic base
│   │   ├── jsonrpc.py                 # JSON-RPC 2.0 implementation
│   │   ├── types/                     # Protocol types
│   │   │   ├── __init__.py
│   │   │   ├── info.py
│   │   │   ├── content.py
│   │   │   ├── capabilities.py
│   │   │   ├── mcp_servers.py
│   │   │   ├── session.py
│   │   │   ├── tools.py
│   │   │   ├── plan.py
│   │   │   ├── permission.py
│   │   │   └── terminal.py
│   │   └── messages/                  # Protocol messages
│   │       ├── __init__.py
│   │       ├── send_message.py        # Core messaging
│   │       ├── initialize.py          # Initialize & auth
│   │       ├── session.py             # Session methods
│   │       ├── filesystem.py          # File system methods
│   │       └── terminal.py            # Terminal methods
│   └── transport/
│       ├── __init__.py
│       ├── base.py                    # Abstract interface
│       └── stdio.py                   # Stdio implementation
├── examples/
│   ├── README.md
│   ├── simple_client.py
│   └── echo_agent.py
├── README.md
├── IMPLEMENTATION.md
├── pyproject.toml
└── .gitignore
```

## Design Principles

1. **Pure Protocol Library**: Focuses on protocol implementation, not high-level abstractions
2. **Following chuk-mcp Patterns**: Maintains consistency with chuk-mcp architecture
3. **Type Safety**: Full type hints and optional Pydantic validation
4. **Async-First**: Built on anyio for efficient async/await patterns
5. **Spec Compliance**: Implements the official ACP specification

## Key Differences from MCP

- **Purpose**: MCP is for AI ↔ Tools, ACP is for Editors ↔ Agents
- **Architecture**: ACP uses stdio subprocess model (like LSP)
- **Content Types**: ACP reuses MCP content types where possible
- **Session Management**: ACP has explicit session lifecycle
- **Tool Integration**: ACP has tool calls with status tracking

## Usage Example

```python
import asyncio
from chuk_acp import (
    stdio_transport,
    send_initialize,
    send_session_new,
    send_session_prompt,
    ClientInfo,
    ClientCapabilities,
    TextContent,
)

async def main():
    # Connect to agent via stdio
    async with stdio_transport("python", ["my_agent.py"]) as (read, write):
        # Initialize
        init = await send_initialize(
            read, write,
            protocol_version=1,
            client_info=ClientInfo(name="my-client", version="1.0.0"),
            capabilities=ClientCapabilities(),
        )

        # Create session
        session = await send_session_new(read, write, working_directory="/tmp")

        # Send prompt
        result = await send_session_prompt(
            read, write,
            session_id=session.sessionId,
            prompt=[TextContent(text="Help me code")],
        )

        print(f"Done: {result.stopReason}")

asyncio.run(main())
```

## Protocol Compliance

chuk-acp implements the complete ACP specification:

- ✅ JSON-RPC 2.0 over stdio
- ✅ Protocol version negotiation (currently version 1)
- ✅ Capability negotiation (client and agent)
- ✅ All baseline agent methods (initialize, session/new, session/prompt)
- ✅ Optional agent methods (session/load, session/set_mode)
- ✅ All baseline client methods (session/request_permission)
- ✅ Optional client methods (fs/*, terminal/*)
- ✅ Content types (text, image, audio, resources)
- ✅ Session management (create, load, cancel)
- ✅ Tool call tracking with status updates
- ✅ Plan and task management
- ✅ Permission requests
- ✅ MCP server integration support
- ✅ Absolute file paths requirement
- ✅ 1-indexed line numbers

## Testing

Basic testing can be done with the included examples:

```bash
# Install in development mode
pip install -e .

# Run the echo example
cd examples
python simple_client.py
```

## Future Enhancements

The library is complete for protocol-level usage. Potential future additions:

1. **High-level abstractions**: Agent and Client classes (like chuk-mcp's MCPServer)
2. **Additional transports**: HTTP, SSE (currently only stdio)
3. **Testing framework**: Protocol compliance testing
4. **More examples**: Advanced usage patterns, real agent implementations
5. **Documentation**: API reference, protocol guides

## Dependencies

**Required:**
- `anyio >= 4.0.0`: Async I/O framework
- `typing-extensions >= 4.8.0`: Type hints support

**Optional:**
- `pydantic >= 2.0.0`: Runtime validation

## Contributing

This is a pure protocol implementation. Contributions should focus on:
- Protocol compliance and correctness
- Performance improvements
- Bug fixes
- Documentation improvements

## License

Apache-2.0

## References

- [ACP Specification](https://agentclientprotocol.com)
- [chuk-mcp](https://github.com/chuk-ai/chuk-mcp) - Model Context Protocol implementation
- [Language Server Protocol](https://microsoft.github.io/language-server-protocol/) - Similar architecture
