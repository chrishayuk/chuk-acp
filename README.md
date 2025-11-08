# chuk-acp

[![CI](https://github.com/chuk-ai/chuk-acp/actions/workflows/ci.yml/badge.svg)](https://github.com/chuk-ai/chuk-acp/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/chuk-acp.svg)](https://badge.fury.io/py/chuk-acp)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![codecov](https://codecov.io/gh/chuk-ai/chuk-acp/branch/main/graph/badge.svg)](https://codecov.io/gh/chuk-ai/chuk-acp)

A Python implementation of the [Agent Client Protocol (ACP)](https://agentclientprotocol.com) - the standard protocol for communication between code editors and AI coding agents.

---

## 📖 Table of Contents

- [Overview](#overview)
- [Why ACP?](#why-acp)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
  - [Building an Agent](#building-an-agent)
  - [Building a Client](#building-a-client)
- [Core Concepts](#core-concepts)
- [Complete Examples](#complete-examples)
- [API Reference](#api-reference)
- [Protocol Support](#protocol-support)
- [Architecture](#architecture)
- [Testing](#testing)
- [Relationship to MCP](#relationship-to-mcp)
- [Contributing](#contributing)
- [License](#license)
- [Links](#links)

---

## Overview

The **Agent Client Protocol (ACP)** is to AI coding agents what the Language Server Protocol (LSP) is to programming languages. It standardizes communication between code editors/IDEs and coding agents—programs that use generative AI to autonomously modify code.

**chuk-acp** provides a complete, production-ready Python implementation of ACP, enabling you to:

- 🤖 **Build ACP-compliant coding agents** that work with any ACP-compatible editor
- 🖥️ **Build editors/IDEs** that can connect to any ACP-compliant agent
- 🔌 **Integrate AI capabilities** into existing development tools
- 🧪 **Test and develop** against the ACP specification

---

## Why ACP?

### The Problem

Without a standard protocol, every AI coding tool creates its own proprietary interface, leading to:

- Fragmentation across different tools and editors
- Inability to switch agents or editors without rewriting integration code
- Duplicated effort implementing similar functionality
- Limited interoperability

### The Solution

ACP provides a **standard, open protocol** that:

- ✅ Enables **any agent to work with any editor**
- ✅ Provides **consistent user experience** across tools
- ✅ Allows **innovation at both the editor and agent level**
- ✅ Built on proven standards (JSON-RPC 2.0)
- ✅ Supports **async/streaming** for real-time AI interactions

Think LSP for language tooling, but for AI coding agents.

---

## Features

### 🎯 Complete ACP Implementation

- Full support for ACP v1 specification
- All baseline methods and content types
- Optional capabilities (modes, session loading, file system, terminal)
- Protocol compliance test suite

### 🔧 Developer-Friendly

- **Type-Safe**: Comprehensive type hints throughout
- **Async-First**: Built on `anyio` for efficient async/await patterns
- **Optional Pydantic**: Use Pydantic for validation, or go dependency-free
- **Well-Documented**: Extensive examples and API documentation
- **Production-Ready**: Tested across Python 3.11, 3.12 on Linux, macOS, Windows

### 🚀 Flexible & Extensible

- **Multiple transports**: Stdio (with more coming)
- **Custom methods**: Extend protocol with `_meta` fields and custom methods
- **Pluggable**: Easy to integrate into existing tools
- **MCP Integration**: Seamless compatibility with Model Context Protocol

### 🛡️ Quality & Security

- Comprehensive test coverage
- Security scanning with Bandit and CodeQL
- Type checking with mypy
- Automated dependency updates
- CI/CD with GitHub Actions

---

## Installation

### Basic Installation

```bash
pip install chuk-acp
```

### With Pydantic Support

For runtime validation and enhanced type safety:

```bash
pip install chuk-acp[pydantic]
```

### Development Installation

```bash
git clone https://github.com/chuk-ai/chuk-acp.git
cd chuk-acp
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev,pydantic]"
```

### Requirements

- Python 3.11 or higher
- Dependencies: `anyio`, `typing-extensions`
- Optional: `pydantic` (for validation)

---

## Quick Start

### Building an Agent

Create an ACP agent that responds to prompts:

```python
"""my_agent.py - A simple ACP agent"""
import asyncio
from chuk_acp.protocol.messages import send_session_update
from chuk_acp.protocol.types import TextContent
from chuk_acp.transport import stdio_transport

async def handle_prompt(session_id: str, prompt: list, write_stream):
    """Process a user prompt and send response."""

    # Extract user's text
    user_text = prompt[0].get('text', '')

    # Send response back to client
    await send_session_update(
        write_stream,
        session_id=session_id,
        agent_message_chunk=TextContent(
            text=f"You asked: {user_text}\n\nHere's my response..."
        )
    )

# Run the agent
if __name__ == "__main__":
    # Your agent implementation here
    # See examples/echo_agent.py for complete example
    pass
```

### Building a Client

Connect to an agent and send prompts:

```python
"""my_client.py - Connect to an ACP agent"""
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
    # Connect to agent
    async with stdio_transport("python", ["my_agent.py"]) as (read, write):

        # Initialize connection
        init_result = await send_initialize(
            read, write,
            protocol_version=1,
            client_info=ClientInfo(name="my-client", version="1.0.0"),
            capabilities=ClientCapabilities()
        )
        print(f"Connected to {init_result.agentInfo.name}")

        # Create session
        session = await send_session_new(read, write, cwd="/path/to/project")

        # Send prompt
        result = await send_session_prompt(
            read, write,
            session_id=session.sessionId,
            prompt=[TextContent(text="Help me write a function")]
        )

        print(f"Agent finished: {result.stopReason}")

asyncio.run(main())
```

---

## Core Concepts

### The Agent-Client Model

```
┌─────────────┐                  ┌──────────────┐
│   Client    │ ←── JSON-RPC ──→ │    Agent     │
│  (Editor)   │     over stdio   │  (AI Tool)   │
└─────────────┘                  └──────────────┘
      ↑                                 ↑
      │                                 │
  User Interface                   AI Model
  File System                      Code Analysis
  Permissions                      Code Generation
```

### Key Components

#### 1. **Protocol Layer** (`chuk_acp.protocol`)

The core protocol implementation:

- **JSON-RPC 2.0**: Request/response and notification messages
- **Message Types**: Initialize, session management, prompts
- **Content Types**: Text, images, audio, resources, annotations
- **Capabilities**: Negotiate features between client and agent

#### 2. **Transport Layer** (`chuk_acp.transport`)

Communication mechanism:

- **Stdio Transport**: Process-based communication (current)
- **Extensible**: WebSocket, HTTP, etc. (future)

#### 3. **Type System** (`chuk_acp.protocol.types`)

Strongly-typed protocol structures:

- Content types (text, image, audio)
- Capabilities and features
- Session modes and states
- Tool calls and permissions

### The ACP Flow

```
1. INITIALIZE
   Client ──→ Agent: Protocol version, capabilities
   Agent  ──→ Client: Agent info, supported features

2. SESSION CREATION
   Client ──→ Agent: Working directory, MCP servers
   Agent  ──→ Client: Session ID

3. PROMPT TURN
   Client ──→ Agent: User prompt (text, images, etc.)
   Agent  ──→ Client: [Streaming updates]
   Agent  ──→ Client: Stop reason (end_turn, max_tokens, etc.)

4. ONGOING INTERACTION
   - Session updates (thoughts, tool calls, messages)
   - Permission requests (file access, terminal, etc.)
   - Mode changes (ask → code → architect)
   - Cancellation support
```

---

## Complete Examples

### Example 1: Echo Agent (Minimal)

A minimal agent that echoes user input:

```python
"""echo_agent.py"""
import json
import sys
from typing import Dict, Any

class EchoAgent:
    def __init__(self):
        self.sessions = {}

    def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "protocolVersion": 1,
            "agentInfo": {
                "name": "echo-agent",
                "version": "0.1.0"
            },
            "agentCapabilities": {}
        }

    def handle_session_new(self, params: Dict[str, Any]) -> Dict[str, Any]:
        import uuid
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        self.sessions[session_id] = {"cwd": params.get("cwd")}
        return {"sessionId": session_id}

    def handle_session_prompt(self, params: Dict[str, Any]) -> Dict[str, Any]:
        session_id = params["sessionId"]
        prompt = params["prompt"]

        # Send update notification
        update = {
            "jsonrpc": "2.0",
            "method": "session/update",
            "params": {
                "sessionId": session_id,
                "agentMessageChunk": {
                    "type": "text",
                    "text": f"Echo: {prompt[0].get('text', '')}"
                }
            }
        }
        sys.stdout.write(json.dumps(update) + "\n")
        sys.stdout.flush()

        return {"stopReason": "end_turn"}

    def run(self):
        for line in sys.stdin:
            message = json.loads(line.strip())
            method = message.get("method")

            if method == "initialize":
                result = self.handle_initialize(message.get("params", {}))
            elif method == "session/new":
                result = self.handle_session_new(message.get("params", {}))
            elif method == "session/prompt":
                result = self.handle_session_prompt(message.get("params", {}))
            else:
                continue

            response = {
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "result": result
            }
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    EchoAgent().run()
```

### Example 2: Client with Session Updates

Handle streaming updates from agent:

```python
"""client_with_updates.py"""
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

async def handle_update(update: dict):
    """Handle session/update notifications from agent."""
    params = update.get("params", {})

    if "agentMessageChunk" in params:
        chunk = params["agentMessageChunk"]
        if chunk["type"] == "text":
            print(f"Agent: {chunk['text']}")

    if "thought" in params:
        print(f"[Thinking: {params['thought']}]")

    if "toolCall" in params:
        tool = params["toolCall"]
        print(f"[Calling: {tool['name']}]")

async def main():
    async with stdio_transport("python", ["echo_agent.py"]) as (read, write):
        # Initialize
        init_result = await send_initialize(
            read, write,
            protocol_version=1,
            client_info=ClientInfo(name="client", version="1.0.0"),
            capabilities=ClientCapabilities()
        )

        # Create session
        session = await send_session_new(read, write, cwd="/tmp")

        # Send prompt (will receive updates)
        result = await send_session_prompt(
            read, write,
            session_id=session.sessionId,
            prompt=[TextContent(text="Write a hello world function")],
            timeout=60.0
        )

        print(f"Completed: {result.stopReason}")

asyncio.run(main())
```

### Example 3: Agent with File System Access

Agent that can read/write files:

```python
"""file_agent.py - Agent with filesystem capabilities"""
from chuk_acp.protocol.types import AgentCapabilities

# Declare filesystem capabilities
capabilities = AgentCapabilities(
    filesystem=True  # Enables fs/read_text_file and fs/write_text_file
)

async def handle_file_operation(session_id: str, operation: str, path: str):
    """Request file access from client."""

    # Request permission
    permission = await send_session_request_permission(
        read, write,
        session_id=session_id,
        request=PermissionRequest(
            id="perm-123",
            description=f"Read file: {path}",
            tools=[{"name": "fs/read_text_file", "arguments": {"path": path}}]
        )
    )

    if permission.granted:
        # Read the file via client
        # (Client implements fs/read_text_file method)
        pass
```

### Example 4: Multi-Session Client

Manage multiple concurrent sessions:

```python
"""multi_session_client.py"""
import asyncio
from chuk_acp import stdio_transport, send_session_new, send_session_prompt

async def create_and_run_session(read, write, cwd: str, prompt: str):
    """Create a session and send a prompt."""
    session = await send_session_new(read, write, cwd=cwd)
    result = await send_session_prompt(
        read, write,
        session_id=session.sessionId,
        prompt=[TextContent(text=prompt)]
    )
    return result

async def main():
    async with stdio_transport("python", ["my_agent.py"]) as (read, write):
        # Initialize once
        await send_initialize(...)

        # Run multiple sessions concurrently
        tasks = [
            create_and_run_session(read, write, "/project1", "Refactor auth"),
            create_and_run_session(read, write, "/project2", "Add tests"),
            create_and_run_session(read, write, "/project3", "Fix bug #123"),
        ]

        results = await asyncio.gather(*tasks)
        print(f"Completed {len(results)} sessions")

asyncio.run(main())
```

---

## API Reference

### Transport

#### `stdio_transport(command, args)`

Create a stdio transport connection to an agent.

```python
async with stdio_transport("python", ["agent.py"]) as (read_stream, write_stream):
    # Use streams for communication
    pass
```

### Initialization

#### `send_initialize(read, write, protocol_version, client_info, capabilities)`

Initialize the connection and negotiate capabilities.

```python
result = await send_initialize(
    read_stream,
    write_stream,
    protocol_version=1,
    client_info=ClientInfo(name="my-client", version="1.0.0"),
    capabilities=ClientCapabilities(filesystem=True)
)
# result.agentInfo, result.capabilities, result.protocolVersion
```

### Session Management

#### `send_session_new(read, write, cwd, mcp_servers=None, mode=None)`

Create a new session.

```python
session = await send_session_new(
    read_stream,
    write_stream,
    cwd="/absolute/path",
    mode="code"  # Optional: ask, architect, code
)
# session.sessionId
```

#### `send_session_prompt(read, write, session_id, prompt)`

Send a prompt to the agent.

```python
result = await send_session_prompt(
    read_stream,
    write_stream,
    session_id="session-123",
    prompt=[
        TextContent(text="Write a function"),
        ImageContent(data="base64...", mimeType="image/png")
    ]
)
# result.stopReason: end_turn, max_tokens, cancelled, refusal
```

#### `send_session_cancel(write, session_id)`

Cancel an ongoing prompt turn.

```python
await send_session_cancel(write_stream, session_id="session-123")
```

### Content Types

#### `TextContent(text)`

Plain text content.

```python
content = TextContent(text="Hello, world!")
```

#### `ImageContent(data, mimeType)`

Base64-encoded image.

```python
content = ImageContent(
    data="iVBORw0KGgoAAAANSUhEUgA...",
    mimeType="image/png"
)
```

#### `AudioContent(data, mimeType)`

Base64-encoded audio.

```python
content = AudioContent(
    data="SUQzBAA...",
    mimeType="audio/mpeg"
)
```

---

## Protocol Support

chuk-acp implements the **complete ACP v1 specification**.

### ✅ Baseline Agent Methods (Required)

| Method | Description | Status |
|--------|-------------|--------|
| `initialize` | Protocol handshake and capability negotiation | ✅ |
| `authenticate` | Optional authentication | ✅ |
| `session/new` | Create new conversation sessions | ✅ |
| `session/prompt` | Process user prompts | ✅ |
| `session/cancel` | Cancel ongoing operations | ✅ |

### ✅ Optional Agent Methods

| Method | Capability | Status |
|--------|------------|--------|
| `session/load` | Resume previous sessions | ✅ |
| `session/set_mode` | Change session modes | ✅ |

### ✅ Client Methods (Callbacks)

| Method | Description | Status |
|--------|-------------|--------|
| `session/request_permission` | Request user approval for actions | ✅ |
| `fs/read_text_file` | Read file contents | ✅ |
| `fs/write_text_file` | Write file contents | ✅ |
| `terminal/create` | Create terminal sessions | ✅ |
| `terminal/output` | Stream terminal output | ✅ |
| `terminal/release` | Release terminal control | ✅ |
| `terminal/wait_for_exit` | Wait for command completion | ✅ |
| `terminal/kill` | Terminate running commands | ✅ |

### ✅ Content Types

- Text content (baseline - always supported)
- Image content (base64-encoded)
- Audio content (base64-encoded)
- Embedded resources
- Resource links
- Annotations

### ✅ Session Features

- Session management (create, load, cancel)
- Multiple parallel sessions
- Session modes: `ask`, `architect`, `code`
- Session history replay
- MCP server integration

### ✅ Tool Integration

- Tool calls with status tracking (`pending`, `in_progress`, `completed`, `failed`)
- Permission requests
- File location tracking
- Structured output (diffs, terminals, content)
- Slash commands (optional)

### ✅ Protocol Requirements

- **File paths**: All paths must be absolute ✅
- **Line numbers**: 1-based indexing ✅
- **JSON-RPC 2.0**: Strict compliance ✅
- **Extensibility**: `_meta` fields and custom methods ✅

---

## Architecture

### Project Structure

```
chuk-acp/
├── src/chuk_acp/
│   ├── protocol/              # Core protocol implementation
│   │   ├── jsonrpc.py         # JSON-RPC 2.0 (requests, responses, errors)
│   │   ├── acp_pydantic_base.py # Optional Pydantic support
│   │   ├── types/             # Protocol type definitions
│   │   │   ├── content.py     # Content types (text, image, audio)
│   │   │   ├── capabilities.py # Client/agent capabilities
│   │   │   ├── session.py     # Session types and modes
│   │   │   ├── tools.py       # Tool calls and permissions
│   │   │   ├── plan.py        # Task planning types
│   │   │   ├── terminal.py    # Terminal integration
│   │   │   └── ...
│   │   └── messages/          # Message handling
│   │       ├── initialize.py  # Initialize/authenticate
│   │       ├── session.py     # Session management
│   │       ├── filesystem.py  # File operations
│   │       ├── terminal.py    # Terminal operations
│   │       └── send_message.py # Core messaging utilities
│   │
│   ├── transport/             # Transport layer
│   │   ├── base.py            # Abstract transport interface
│   │   └── stdio.py           # Stdio transport (subprocess)
│   │
│   └── __init__.py            # Public API exports
│
├── examples/                  # Working examples
│   ├── echo_agent.py          # Simple echo agent
│   ├── simple_client.py       # Basic client
│   ├── quick_start.py         # Getting started
│   └── comprehensive_demo.py  # Full-featured demo
│
├── tests/                     # Test suite
│   ├── test_protocol_compliance.py  # Spec compliance
│   ├── test_jsonrpc.py        # JSON-RPC tests
│   ├── test_types.py          # Type system tests
│   ├── test_messages.py       # Message handling
│   └── test_stdio_transport.py # Transport tests
│
└── .github/                   # CI/CD workflows
    ├── workflows/
    │   ├── ci.yml             # Testing and linting
    │   ├── publish.yml        # PyPI publishing
    │   └── codeql.yml         # Security scanning
    └── ...
```

### Design Principles

1. **Protocol First**: Strict adherence to ACP specification
2. **Type Safety**: Comprehensive type hints throughout
3. **Optional Dependencies**: Pydantic is optional, not required
4. **Async by Default**: Built on `anyio` for async/await
5. **Extensibility**: Custom methods and `_meta` fields supported
6. **Testability**: Loosely coupled, dependency injection
7. **Zero-Config**: Works out of the box with sensible defaults

### Layer Separation

```
┌─────────────────────────────────────┐
│     User Code (Agents/Clients)      │
├─────────────────────────────────────┤
│     High-Level API (messages/)      │  ← send_initialize, send_prompt, etc.
├─────────────────────────────────────┤
│    Protocol Layer (types/, jsonrpc) │  ← Content types, capabilities
├─────────────────────────────────────┤
│    Transport Layer (transport/)     │  ← Stdio, future: WebSocket, HTTP
└─────────────────────────────────────┘
```

---

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
uv run pytest tests/test_protocol_compliance.py -v

# Test without Pydantic (fallback mode)
uv pip uninstall pydantic
uv run pytest
```

### Test Categories

- **Protocol Compliance** (`test_protocol_compliance.py`): Validates ACP spec adherence
- **JSON-RPC** (`test_jsonrpc.py`): JSON-RPC 2.0 implementation
- **Types** (`test_types.py`): Type system and content types
- **Messages** (`test_messages.py`): Message handling and serialization
- **Transport** (`test_stdio_transport.py`): Transport layer

### Code Quality Checks

```bash
# Format code
make format

# Lint
make lint

# Type check
make mypy

# Security scan
make security

# All checks
make check
```

---

## Relationship to MCP

**ACP** and **MCP** (Model Context Protocol) are complementary protocols:

| Protocol | Purpose | Focus |
|----------|---------|-------|
| **MCP** | What data/tools agents can access | Context & tools |
| **ACP** | Where the agent lives in your workflow | Agent lifecycle |

### Integration

ACP reuses MCP data structures for content types and resources:

```python
from chuk_acp.protocol.types import (
    TextContent,      # From MCP
    ImageContent,     # From MCP
    ResourceContent,  # From MCP
)

# ACP sessions can specify MCP servers
session = await send_session_new(
    read, write,
    cwd="/project",
    mcp_servers=[
        MCPServer(
            name="filesystem",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", "/path"]
        )
    ]
)
```

### When to Use What

- **Use ACP** to build AI coding agents that integrate with editors
- **Use MCP** to provide context and tools to language models
- **Use both** for a complete AI-powered development environment

---

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for:

- Development setup
- Code style and standards
- Testing requirements
- Pull request process
- Release workflow

### Quick Start for Contributors

```bash
# Clone and setup
git clone https://github.com/chuk-ai/chuk-acp.git
cd chuk-acp
uv venv
source .venv/bin/activate
uv pip install -e ".[dev,pydantic]"

# Run checks
make check

# Run examples
cd examples && python simple_client.py
```

### Areas for Contribution

- 🐛 Bug fixes and issue resolution
- ✨ New features (check ACP spec for ideas)
- 📚 Documentation improvements
- 🧪 Additional test coverage
- 🌐 Additional transports (WebSocket, HTTP, etc.)
- 🎨 Example agents and clients
- 🔧 Tooling and developer experience

---

## License

This project is licensed under the **Apache License 2.0**.

See [LICENSE](LICENSE) for full details.

---

## Links

### Official Resources

- **ACP Specification**: https://agentclientprotocol.com
- **GitHub Repository**: https://github.com/chuk-ai/chuk-acp
- **PyPI Package**: https://pypi.org/project/chuk-acp/
- **Issue Tracker**: https://github.com/chuk-ai/chuk-acp/issues
- **Discussions**: https://github.com/chuk-ai/chuk-acp/discussions

### Related Projects

- **Model Context Protocol (MCP)**: https://modelcontextprotocol.io
- **Language Server Protocol (LSP)**: https://microsoft.github.io/language-server-protocol/

### Community

- Report bugs: [GitHub Issues](https://github.com/chuk-ai/chuk-acp/issues)
- Ask questions: [GitHub Discussions](https://github.com/chuk-ai/chuk-acp/discussions)
- Contribute: See [CONTRIBUTING.md](CONTRIBUTING.md)

---

<div align="center">

**Built with ❤️ for the AI coding community**

[⭐ Star us on GitHub](https://github.com/chuk-ai/chuk-acp) | [📦 Install from PyPI](https://pypi.org/project/chuk-acp/) | [📖 Read the Spec](https://agentclientprotocol.com)

</div>
