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
  - [CLI Tool](#cli-tool)
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

- 💬 **Interact with agents instantly** using the CLI (`uvx chuk-acp claude-code-acp` or `uvx chuk-acp kimi --acp`)
- 🤖 **Build ACP-compliant coding agents** easily with the high-level `ACPAgent` API
- 🖥️ **Build editors/IDEs** that can connect to any ACP-compliant agent with `ACPClient`
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

- **CLI Tool**: Interactive command-line client for testing agents (`uvx chuk-acp`)
- **Zero Installation**: Run with `uvx` - no setup required
- **Type-Safe**: Comprehensive type hints throughout
- **Async-First**: Built on `anyio` for efficient async/await patterns
- **Optional Pydantic**: Use Pydantic for validation, or go dependency-free with fallback
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

### 🚀 Try It Now with uvx (No Installation!)

The fastest way to get started is using `uvx` to run the CLI without any installation:

```bash
# Connect to Claude Code (requires ANTHROPIC_API_KEY)
ANTHROPIC_API_KEY=sk-... uvx chuk-acp claude-code-acp

# Connect to Kimi agent
uvx chuk-acp kimi --acp

# Chat with any ACP agent
uvx chuk-acp python examples/echo_agent.py

# Single prompt mode
uvx chuk-acp kimi --acp --prompt "Create a Python function to calculate fibonacci"

# With faster validation (optional)
uvx --from 'chuk-acp[pydantic]' chuk-acp claude-code-acp
```

**That's it!** `uvx` automatically handles installation and runs the CLI. Perfect for quick testing or one-off usage.

### Using uv (Recommended for Development)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer:

```bash
# Basic installation (includes CLI)
uv pip install chuk-acp

# With Pydantic validation support (recommended for better performance)
uv pip install chuk-acp[pydantic]

# Or add to your project
uv add chuk-acp
```

### Using pip

```bash
# Basic installation (includes CLI)
pip install chuk-acp

# With Pydantic support (recommended)
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
- Optional: `pydantic` (for faster validation - works without it using fallback mechanism)

---

## Quick Start

### CLI Tool - Interactive Chat with Any Agent

The easiest way to interact with ACP agents is using the built-in CLI. Works instantly with `uvx` or after installation.

#### Try It Now (No Installation!)

```bash
# Connect to Claude Code (requires ANTHROPIC_API_KEY)
ANTHROPIC_API_KEY=sk-... uvx chuk-acp claude-code-acp

# Connect to Kimi agent
uvx chuk-acp kimi --acp

# Interactive chat opens automatically
# Just start typing your questions!
```

#### After Installation

```bash
# Interactive mode (default)
chuk-acp python examples/echo_agent.py

# Single prompt and exit
chuk-acp kimi --acp --prompt "Create a Python function to calculate factorial"

# Using a config file
chuk-acp --config examples/kimi_config.json

# With environment variables
chuk-acp python agent.py --env DEBUG=true --env API_KEY=xyz

# Verbose output for debugging
chuk-acp python agent.py --verbose
```

#### Interactive Mode Commands

When in interactive chat mode, you can use these special commands:

| Command | Description |
|---------|-------------|
| `/quit` or `/exit` | Exit the client |
| `/new` | Start a new session (clears context) |
| `/info` | Show agent information and session ID |

#### Example Interactive Session

**With Claude Code:**
```bash
$ ANTHROPIC_API_KEY=sk-... uvx chuk-acp claude-code-acp

╔═══════════════════════════════════════════════════════════════╗
║           ACP Interactive Client                              ║
╚═══════════════════════════════════════════════════════════════╝

You: Create a Python function to check if a string is a palindrome

Agent: Here's a Python function to check if a string is a palindrome:

def is_palindrome(s):
    # Remove spaces and convert to lowercase
    s = s.replace(" ", "").lower()
    # Check if string equals its reverse
    return s == s[::-1]

You: /quit
Goodbye!
```

**With Kimi:**
```bash
$ uvx chuk-acp kimi --acp

You: What's the best way to handle async errors in Python?
Agent: [Kimi's response...]
```

#### Configuration Files

Use standard ACP configuration format (compatible with Zed, VSCode, etc.):

**claude_code_config.json:**
```json
{
  "command": "claude-code-acp",
  "args": [],
  "env": {
    "ANTHROPIC_API_KEY": "sk-..."
  }
}
```

**kimi_config.json:**
```json
{
  "command": "kimi",
  "args": ["--acp"],
  "env": {}
}
```

Then use with:
```bash
chuk-acp --config claude_code_config.json
chuk-acp --config kimi_config.json
```

**📖 See [CLI.md](CLI.md) for complete CLI documentation and advanced usage.**

### The Easiest Way: ACPClient

The fastest way to get started programmatically is with the high-level `ACPClient`, which handles all protocol details automatically:

**Option A: Direct Usage**
```python
"""quickstart.py"""
import anyio
from chuk_acp import ACPClient

async def main():
    # Connect to an agent - handles initialization, sessions, everything!
    async with ACPClient("python", ["echo_agent.py"]) as client:
        # Send a prompt and get the response
        result = await client.send_prompt("Hello!")
        print(f"Agent: {result.full_message}")

anyio.run(main)
```

**Option B: Using Standard ACP Configuration**

This matches the configuration format used by editors like Zed, VSCode, etc.:

```python
"""quickstart_config.py"""
import anyio
from chuk_acp import ACPClient, AgentConfig

async def main():
    # Standard ACP configuration format
    config = AgentConfig(
        command="kimi",           # Any ACP-compatible agent
        args=["--acp"],          # Agent-specific arguments
        env={"DEBUG": "true"}    # Optional environment variables
    )

    async with ACPClient.from_config(config) as client:
        result = await client.send_prompt("Hello!")
        print(f"Agent: {result.full_message}")

anyio.run(main)
```

Or load from a JSON file (like `~/.config/zed/settings.json`):

```python
from chuk_acp import load_agent_config

config = load_agent_config("~/.config/my-app/agent.json")
async with ACPClient.from_config(config) as client:
    result = await client.send_prompt("Hello!")
```

**What `ACPClient` does automatically:**
- ✅ Starts the agent process
- ✅ Handles protocol initialization
- ✅ Creates and manages sessions
- ✅ Captures all notifications
- ✅ Cleans up resources
- ✅ Supports standard ACP configuration format

**Want more control?** The low-level API gives you fine-grained control over the protocol. See the examples below.

---

### Building an Agent

The fastest way to build an ACP agent is with the high-level `ACPAgent` class:

```python
"""my_agent.py"""
from typing import List
from chuk_acp.agent import ACPAgent, AgentSession
from chuk_acp.protocol.types import AgentInfo, Content

class MyAgent(ACPAgent):
    """Your custom agent implementation."""

    def get_agent_info(self) -> AgentInfo:
        """Return agent information."""
        return AgentInfo(
            name="my-agent",
            version="1.0.0",
            title="My Custom Agent"
        )

    async def handle_prompt(
        self, session: AgentSession, prompt: List[Content]
    ) -> str:
        """Handle a prompt - this is where your agent logic goes."""
        # Extract text from prompt
        text = prompt[0].get("text", "") if prompt else ""

        # Your agent logic here
        response = f"I received: {text}"

        # Return the response
        return response

if __name__ == "__main__":
    agent = MyAgent()
    agent.run()
```

**Run your agent:**
```bash
# Test with CLI
chuk-acp python my_agent.py

# Or use with editors
# Add to your editor's ACP configuration
```

**What `ACPAgent` does automatically:**
- ✅ Handles all protocol messages (initialize, session/new, session/prompt)
- ✅ Manages sessions and routing
- ✅ Sends responses in correct format
- ✅ Error handling and logging
- ✅ Stdin/stdout transport

**Real example:** See [`examples/echo_agent.py`](examples/echo_agent.py) - a complete working agent in just 35 lines!

---

### More Examples

For more complete examples showing different use cases:

```bash
# Clone the repository
git clone https://github.com/chuk-ai/chuk-acp.git
cd chuk-acp

# Install
uv pip install -e ".[pydantic]"

# Run examples (all use the high-level ACPClient)
uv run python examples/simple_client.py   # Basic single prompt
uv run python examples/quick_start.py     # Multi-turn conversation
uv run python examples/config_example.py  # Configuration support (Zed/VSCode format)

# Advanced: Low-level protocol examples
uv run python examples/low_level/simple_client.py        # Manual protocol handling
uv run python examples/low_level/quick_start.py          # Self-contained with embedded agent
uv run python examples/low_level/comprehensive_demo.py   # All ACP features
```

See the [examples directory](https://github.com/chuk-ai/chuk-acp/tree/main/examples) for detailed documentation.

> **Note**: Examples are in the GitHub repository. If you installed via pip, clone the repo to access them.

### Option B: Build Your Own (10 Minutes)

Create a complete ACP client and agent from scratch.

#### Step 1: Install

```bash
uv pip install chuk-acp[pydantic]
```

#### Step 2: Create an Agent

Save this as `echo_agent.py`:

```python
"""echo_agent.py - A simple ACP agent"""
import json
import sys
import uuid

from chuk_acp.protocol import (
    create_response,
    create_notification,
    METHOD_INITIALIZE,
    METHOD_SESSION_NEW,
    METHOD_SESSION_PROMPT,
    METHOD_SESSION_UPDATE,
)
from chuk_acp.protocol.types import AgentInfo, AgentCapabilities, TextContent

# Read messages from stdin, write to stdout
for line in sys.stdin:
    msg = json.loads(line.strip())
    method = msg.get("method")
    params = msg.get("params", {})
    msg_id = msg.get("id")

    # Route to handlers
    if method == METHOD_INITIALIZE:
        result = {
            "protocolVersion": 1,
            "agentInfo": AgentInfo(name="echo-agent", version="1.0.0").model_dump(),
            "agentCapabilities": AgentCapabilities().model_dump(),
        }
        response = create_response(id=msg_id, result=result)

    elif method == METHOD_SESSION_NEW:
        session_id = f"session-{uuid.uuid4().hex[:8]}"
        response = create_response(id=msg_id, result={"sessionId": session_id})

    elif method == METHOD_SESSION_PROMPT:
        session_id = params["sessionId"]
        user_text = params["prompt"][0].get("text", "")

        # Send a notification with the echo
        notification = create_notification(
            method=METHOD_SESSION_UPDATE,
            params={
                "sessionId": session_id,
                "agentMessageChunk": TextContent(text=f"Echo: {user_text}").model_dump(),
            },
        )
        sys.stdout.write(json.dumps(notification.model_dump()) + "\n")
        sys.stdout.flush()

        # Send the response
        response = create_response(id=msg_id, result={"stopReason": "end_turn"})

    else:
        continue

    sys.stdout.write(json.dumps(response.model_dump()) + "\n")
    sys.stdout.flush()
```

#### Step 3: Create a Client

Save this as `my_client.py`:

```python
"""my_client.py - Connect to the echo agent using ACPClient"""
import anyio
from chuk_acp import ACPClient


async def main():
    # Connect to the agent - handles everything automatically!
    async with ACPClient("python", ["echo_agent.py"]) as client:
        # Send a prompt and get the response
        result = await client.send_prompt("Hello!")
        print(f"Agent says: {result.full_message}")


if __name__ == "__main__":
    anyio.run(main())
```

#### Step 4: Run It!

```bash
uv run python my_client.py
```

**Output:**
```
✓ Connected to echo-agent
✓ Session: session-a1b2c3d4

Sending: Hello!
Agent says: Echo: Hello!
✓ Done!
```

🎉 **That's it!** You've built a working ACP agent and client.

### What You Learned

**Option A** showed you the fastest path - running pre-built examples.

**Option B** taught you:
- **Agents**: Read JSON-RPC from stdin, write to stdout using `create_response()` and `create_notification()`
- **Clients**: Connect via `stdio_transport`, use `send_initialize()` and `send_session_new()`, manually handle messages to capture notifications
- **Protocol flow**: Initialize → Create Session → Send Prompts (with notifications) → Get Response
- **Best practices**: Use library types (`TextContent`, `AgentInfo`) and method constants (`METHOD_INITIALIZE`)

### Next Steps

**Explore More Features:**

Check out the complete examples in the [GitHub repository](https://github.com/chuk-ai/chuk-acp/tree/main/examples):
- [simple_client.py](https://github.com/chuk-ai/chuk-acp/blob/main/examples/simple_client.py) - Clean client with notification handling
- [echo_agent.py](https://github.com/chuk-ai/chuk-acp/blob/main/examples/echo_agent.py) - Production-ready agent with error handling
- [comprehensive_demo.py](https://github.com/chuk-ai/chuk-acp/blob/main/examples/comprehensive_demo.py) - Filesystem, terminal, all ACP features

**Build Something:**
- Add file system access to your agent (see Example 3 below)
- Implement tool calls and permission requests
- Support multiple concurrent sessions
- Add streaming for long responses

**Learn More:**
- [API Reference](#api-reference) - Complete API documentation
- [Protocol Support](#protocol-support) - What's supported in ACP v1
- [ACP Specification](https://agentclientprotocol.com) - Official protocol docs

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

### Example 1: Echo Agent (Using Library)

A minimal agent that echoes user input using chuk-acp library helpers:

```python
"""echo_agent.py - Agent using chuk-acp library"""
import json
import sys
import uuid
from typing import Dict, Any

from chuk_acp.protocol import (
    create_response,
    create_error_response,
    create_notification,
    METHOD_INITIALIZE,
    METHOD_SESSION_NEW,
    METHOD_SESSION_PROMPT,
    METHOD_SESSION_UPDATE,
)
from chuk_acp.protocol.types import (
    AgentInfo,
    AgentCapabilities,
    TextContent,
)

class EchoAgent:
    def __init__(self):
        self.sessions = {}

    def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Use library types instead of manual dict construction."""
        agent_info = AgentInfo(name="echo-agent", version="0.1.0")
        agent_capabilities = AgentCapabilities()

        return {
            "protocolVersion": 1,
            "agentInfo": agent_info.model_dump(exclude_none=True),
            "agentCapabilities": agent_capabilities.model_dump(exclude_none=True),
        }

    def handle_session_new(self, params: Dict[str, Any]) -> Dict[str, Any]:
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        self.sessions[session_id] = {"cwd": params.get("cwd")}
        return {"sessionId": session_id}

    def handle_session_prompt(self, params: Dict[str, Any]) -> Dict[str, Any]:
        session_id = params["sessionId"]
        prompt = params["prompt"]

        # Use library helpers to create notification
        text_content = TextContent(
            text=f"Echo: You said '{prompt[0].get('text', '')}'"
        )

        notification = create_notification(
            method=METHOD_SESSION_UPDATE,
            params={
                "sessionId": session_id,
                "agentMessageChunk": text_content.model_dump(exclude_none=True),
            },
        )

        sys.stdout.write(json.dumps(notification.model_dump(exclude_none=True)) + "\n")
        sys.stdout.flush()

        return {"stopReason": "end_turn"}

    def run(self):
        for line in sys.stdin:
            message = json.loads(line.strip())
            method = message.get("method")
            msg_id = message.get("id")

            try:
                # Route to handler using method constants
                if method == METHOD_INITIALIZE:
                    result = self.handle_initialize(message.get("params", {}))
                elif method == METHOD_SESSION_NEW:
                    result = self.handle_session_new(message.get("params", {}))
                elif method == METHOD_SESSION_PROMPT:
                    result = self.handle_session_prompt(message.get("params", {}))
                else:
                    raise Exception(f"Unknown method: {method}")

                # Use library helper to create response
                response = create_response(id=msg_id, result=result)
            except Exception as e:
                # Use library helper for error responses
                response = create_error_response(id=msg_id, code=-32603, message=str(e))

            sys.stdout.write(json.dumps(response.model_dump(exclude_none=True)) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    EchoAgent().run()
```

> **Note**: This demonstrates using the library's protocol helpers (`create_response`, `create_notification`, `TextContent`, etc.) instead of manual JSON construction. See `examples/echo_agent.py` for the complete implementation.

### Example 2: Client with Session Updates

Capture and handle streaming updates from agent:

```python
"""client_with_updates.py - Capture session/update notifications"""
import asyncio
import uuid

import anyio

from chuk_acp import (
    stdio_transport,
    send_initialize,
    send_session_new,
    ClientInfo,
    ClientCapabilities,
    TextContent,
)
from chuk_acp.protocol import (
    create_request,
    JSONRPCNotification,
    JSONRPCResponse,
    METHOD_SESSION_PROMPT,
    METHOD_SESSION_UPDATE,
)

async def main():
    async with stdio_transport("python", ["examples/echo_agent.py"]) as (read, write):
        # Initialize
        init_result = await send_initialize(
            read, write,
            protocol_version=1,
            client_info=ClientInfo(name="client", version="1.0.0"),
            capabilities=ClientCapabilities()
        )
        print(f"Connected to {init_result.agentInfo.name}")

        # Create session
        session = await send_session_new(read, write, cwd="/tmp")

        # Send prompt and capture notifications
        prompt_text = "Write a hello world function"
        print(f"User: {prompt_text}")

        request_id = str(uuid.uuid4())
        request = create_request(
            method=METHOD_SESSION_PROMPT,
            params={
                "sessionId": session.sessionId,
                "prompt": [TextContent(text=prompt_text).model_dump(exclude_none=True)],
            },
            id=request_id,
        )
        await write.send(request)

        # Collect notifications and response
        agent_messages = []
        stop_reason = None

        with anyio.fail_after(60.0):
            while stop_reason is None:
                message = await read.receive()

                # Handle session/update notifications
                if isinstance(message, JSONRPCNotification):
                    if message.method == METHOD_SESSION_UPDATE:
                        params = message.params or {}

                        # Agent message chunks
                        if "agentMessageChunk" in params:
                            chunk = params["agentMessageChunk"]
                            if isinstance(chunk, dict) and "text" in chunk:
                                agent_messages.append(chunk["text"])

                        # Thoughts (optional)
                        if "thought" in params:
                            print(f"[Thinking: {params['thought']}]")

                        # Tool calls (optional)
                        if "toolCall" in params:
                            tool = params["toolCall"]
                            print(f"[Calling: {tool.get('name')}]")

                # Handle response
                elif isinstance(message, JSONRPCResponse):
                    if message.id == request_id:
                        result = message.result
                        if isinstance(result, dict):
                            stop_reason = result.get("stopReason")

        # Display captured agent messages
        if agent_messages:
            print(f"Agent: {''.join(agent_messages)}")

        print(f"Completed: {stop_reason}")

asyncio.run(main())
```

> **Key Point**: To capture `session/update` notifications, you need to manually handle the request/response loop instead of using `send_session_prompt()`, which discards notifications. See `examples/simple_client.py` for a complete working example.

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

### High-Level Client

The `ACPClient` provides the simplest way to interact with ACP agents:

#### Direct Usage

```python
from chuk_acp import ACPClient

async with ACPClient("python", ["agent.py"]) as client:
    # Access agent information
    print(f"Agent: {client.agent_info.name}")
    print(f"Session: {client.current_session.sessionId}")

    # Send prompts
    result = await client.send_prompt("Hello!")
    print(result.full_message)  # Complete agent response
    print(result.stop_reason)   # Why agent stopped

    # Create new sessions
    new_session = await client.new_session(cwd="/other/path")
```

#### Configuration-Based Usage

Use standard ACP configuration format (compatible with Zed, VSCode, etc.):

```python
from chuk_acp import ACPClient, AgentConfig, load_agent_config

# Method 1: Create config directly
config = AgentConfig(
    command="kimi",
    args=["--acp"],
    env={"DEBUG": "true"},
    cwd="/optional/path"
)

async with ACPClient.from_config(config) as client:
    result = await client.send_prompt("Hello!")

# Method 2: Load from JSON file
config = load_agent_config("~/.config/my-app/agent.json")
async with ACPClient.from_config(config) as client:
    result = await client.send_prompt("Hello!")

# Method 3: From dictionary (like editor configs)
config = AgentConfig(**{
    "command": "kimi",
    "args": ["--acp"],
    "env": {}
})
async with ACPClient.from_config(config) as client:
    result = await client.send_prompt("Hello!")
```

**Example JSON config file:**
```json
{
  "command": "kimi",
  "args": ["--acp"],
  "env": {
    "DEBUG": "true",
    "LOG_LEVEL": "info"
  },
  "cwd": "/optional/path"
}
```

**Key Classes:**
- `ACPClient` - Main client class
- `AgentConfig` - Standard ACP configuration format
- `load_agent_config()` - Load config from JSON file
- `PromptResult` - Contains response and all notifications
- `SessionInfo` - Session information
- `SessionUpdate` - Individual notification from agent

### Low-Level Protocol API

For fine-grained control over the protocol:

### Protocol Helpers

#### JSON-RPC Message Helpers

Build protocol messages using library helpers:

```python
from chuk_acp.protocol import (
    create_request,
    create_response,
    create_error_response,
    create_notification,
)

# Create a request
request = create_request(
    method="session/prompt",
    params={"sessionId": "session-1", "prompt": [...]},
    id="req-123"
)

# Create a response
response = create_response(id="req-123", result={"stopReason": "end_turn"})

# Create an error response
error = create_error_response(id="req-123", code=-32603, message="Internal error")

# Create a notification
notification = create_notification(
    method="session/update",
    params={"sessionId": "session-1", "agentMessageChunk": {...}}
)
```

#### Method Constants

Use constants instead of string literals for protocol methods:

```python
from chuk_acp.protocol import (
    METHOD_INITIALIZE,
    METHOD_SESSION_NEW,
    METHOD_SESSION_PROMPT,
    METHOD_SESSION_UPDATE,
    METHOD_SESSION_CANCEL,
    METHOD_FS_READ_TEXT_FILE,
    METHOD_FS_WRITE_TEXT_FILE,
    METHOD_TERMINAL_CREATE,
    # ... and more
)

# Use in message routing
if method == METHOD_INITIALIZE:
    # Handle initialize
    pass
elif method == METHOD_SESSION_PROMPT:
    # Handle prompt
    pass
```

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

> **Note**: `send_session_prompt` discards `session/update` notifications from the agent. To capture agent responses (message chunks, thoughts, tool calls), manually handle the request/response loop. See Example 2 or `examples/simple_client.py` for details.

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
- **CLI Documentation**: [CLI.md](CLI.md)

### Related Projects

**ACP Agents:**
- **Claude Code**: https://github.com/zed-industries/claude-code-acp - Anthropic's official Claude adapter
- **Kimi**: https://github.com/MoonshotAI/kimi-cli - AI coding agent from Moonshot AI

**Protocols:**
- **Model Context Protocol (MCP)**: https://modelcontextprotocol.io - Data & tool access for agents
- **Language Server Protocol (LSP)**: https://microsoft.github.io/language-server-protocol/ - Inspiration for ACP

### Community

- Report bugs: [GitHub Issues](https://github.com/chuk-ai/chuk-acp/issues)
- Ask questions: [GitHub Discussions](https://github.com/chuk-ai/chuk-acp/discussions)
- Contribute: See [CONTRIBUTING.md](CONTRIBUTING.md)

---

<div align="center">

**Built with ❤️ for the AI coding community**

[⭐ Star us on GitHub](https://github.com/chuk-ai/chuk-acp) | [📦 Install from PyPI](https://pypi.org/project/chuk-acp/) | [📖 Read the Spec](https://agentclientprotocol.com)

</div>
