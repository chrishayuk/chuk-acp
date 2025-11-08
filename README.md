# chuk-acp

A Python implementation of the [Agent Client Protocol (ACP)](https://agentclientprotocol.com) - the standard protocol for communication between code editors and AI coding agents.

## Overview

The Agent Client Protocol (ACP) is to AI coding agents what the Language Server Protocol (LSP) is to programming languages. It standardizes communication between code editors/IDEs and coding agents (programs that use generative AI to autonomously modify code).

## Features

- **Complete ACP Implementation**: Full support for the Agent Client Protocol specification
- **JSON-RPC 2.0 Foundation**: Standards-compliant JSON-RPC messaging over stdio
- **Type-Safe**: Comprehensive type hints and validation support
- **Async-First**: Built on anyio for efficient async/await patterns
- **Flexible Transport**: Stdio transport with extensible architecture
- **Client & Agent Support**: Build both ACP-compliant editors and agents

## Installation

```bash
pip install chuk-acp
```

With Pydantic validation support:
```bash
pip install chuk-acp[pydantic]
```

## Quick Start

### Creating an ACP Agent

```python
import asyncio
from chuk_acp.agent import ACPAgent
from chuk_acp.types import AgentCapabilities, TextContent

agent = ACPAgent(
    name="my-agent",
    version="1.0.0",
    capabilities=AgentCapabilities()
)

@agent.on_prompt
async def handle_prompt(session_id: str, prompt: list) -> None:
    # Process the user's prompt
    await agent.send_update(
        session_id,
        agent_message_chunk=TextContent(text="Processing your request...")
    )
    # ... agent logic ...

asyncio.run(agent.run_stdio())
```

### Creating an ACP Client

```python
import asyncio
from chuk_acp.client import ACPClient
from chuk_acp.transport.stdio import StdioTransport

async def main():
    transport = StdioTransport(
        command="python",
        args=["my_agent.py"]
    )

    async with ACPClient(transport) as client:
        # Initialize connection
        await client.initialize()

        # Create a new session
        session_id = await client.create_session(
            working_directory="/path/to/project"
        )

        # Send a prompt
        await client.send_prompt(
            session_id,
            [{"type": "text", "text": "Help me refactor this code"}]
        )

asyncio.run(main())
```

## Protocol Support

chuk-acp implements the complete ACP specification:

### Agent Methods
- ✅ `initialize` - Protocol handshake and capability negotiation
- ✅ `authenticate` - Optional authentication
- ✅ `session/new` - Create new conversation sessions
- ✅ `session/prompt` - Process user prompts
- ✅ `session/load` - Resume previous sessions (optional capability)
- ✅ `session/set_mode` - Change session modes (optional capability)
- ✅ `session/cancel` - Cancel ongoing operations

### Client Methods
- ✅ `session/request_permission` - Request user approval for actions
- ✅ `fs/read_text_file` - Read file contents (optional capability)
- ✅ `fs/write_text_file` - Write file contents (optional capability)
- ✅ `terminal/create` - Create terminal sessions (optional capability)
- ✅ `terminal/output` - Stream terminal output (optional capability)
- ✅ `terminal/release` - Release terminal control (optional capability)
- ✅ `terminal/wait_for_exit` - Wait for command completion (optional capability)
- ✅ `terminal/kill` - Terminate running commands (optional capability)

### Content Types
- ✅ Text content
- ✅ Image content (base64-encoded)
- ✅ Audio content (base64-encoded)
- ✅ Embedded resources
- ✅ Resource links
- ✅ Annotations

### Session Features
- ✅ Session management (create, load, cancel)
- ✅ Multiple parallel sessions
- ✅ Session modes (ask, architect, code)
- ✅ Session history replay

### Tool Integration
- ✅ Tool calls with status tracking
- ✅ Permission requests
- ✅ File location tracking
- ✅ Structured output (diffs, terminals, content)

## Architecture

```
chuk-acp/
├── src/chuk_acp/
│   ├── protocol/           # Protocol layer (JSON-RPC, messages, types)
│   │   ├── jsonrpc.py      # JSON-RPC 2.0 implementation
│   │   ├── messages.py     # ACP message definitions
│   │   └── types.py        # Content types, capabilities, errors
│   ├── transport/          # Transport layer
│   │   ├── base.py         # Abstract transport interface
│   │   └── stdio.py        # Stdio transport implementation
│   ├── agent.py            # High-level agent implementation
│   ├── client.py           # High-level client implementation
│   └── __init__.py
├── examples/               # Example implementations
└── tests/                  # Test suite
```

## Examples

See the `examples/` directory for complete working examples:
- **minimal_agent.py** - Minimal ACP agent implementation
- **echo_agent.py** - Echo agent that responds to prompts
- **file_agent.py** - Agent with file system access
- **client_example.py** - Example ACP client usage

## Relationship to MCP

ACP complements the Model Context Protocol (MCP):
- **MCP** handles the _what_: What data and tools can agents access
- **ACP** handles the _where_: Where the agent lives in your workflow

ACP reuses MCP data structures for content types and resources, enabling seamless integration between protocols.

## Contributing

Contributions are welcome! This project follows the Apache 2.0 license.

## License

Apache-2.0

## Links

- [ACP Specification](https://agentclientprotocol.com)
- [GitHub Repository](https://github.com/chuk-ai/chuk-acp)
- [Issue Tracker](https://github.com/chuk-ai/chuk-acp/issues)
