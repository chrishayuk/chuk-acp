# Chuk-ACP Examples

This directory contains example scripts demonstrating how to use the chuk-acp library.

## Available Examples

### 1. Quick Start (`quick_start.py`)

A minimal example showing the basics of connecting to an ACP agent and performing simple operations.

**What it demonstrates:**
- Creating a simple echo agent
- Establishing stdio transport
- Protocol handshake (initialize)
- Sending a prompt and receiving a response

**Run it:**
```bash
uv run python examples/quick_start.py
```

### 2. Simple Client (`simple_client.py`)

A straightforward client example showing basic ACP communication.

**What it demonstrates:**
- Connecting to the echo agent
- Protocol handshake
- Session creation
- Sending a single prompt

**Run it:**
```bash
uv run python examples/simple_client.py
```

### 3. Comprehensive Demo (`comprehensive_demo.py`)

A complete walkthrough of all major ACP protocol features with detailed output.

**What it demonstrates:**
- Stdio transport connection
- ACP protocol handshake (initialize)
- Session creation and management
- Agent prompt/response
- Filesystem read/write operations via agent
- Terminal session creation
- Proper cleanup and error handling

**Run it:**
```bash
uv run python examples/comprehensive_demo.py
```

### 4. Echo Agent (`echo_agent.py`)

A simple standalone ACP agent server that echoes back messages. This demonstrates how to build an agent using the chuk-acp library.

**What it demonstrates:**
- Building a basic ACP-compliant agent using library helpers
- Using `create_response()` and `create_error_response()` for JSON-RPC
- Using `create_notification()` for session updates
- Using method constants (`METHOD_INITIALIZE`, etc.)
- Handling initialize requests
- Processing prompts and sessions
- JSON-RPC message handling via stdin/stdout

**Important:** The echo agent is designed to run as a **server process** that communicates via stdin/stdout. Running it directly won't show any output - it waits for JSON-RPC messages on stdin.

**How to use it:**

1. **With simple_client.py (Recommended):**
   ```bash
   uv run python examples/simple_client.py
   ```
   The simple_client will automatically launch echo_agent.py as a subprocess.

2. **Manual testing with piped input:**
   ```bash
   # From project root directory:
   echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":1}}' | uv run python examples/echo_agent.py

   # You should see a JSON response:
   # {"jsonrpc":"2.0","id":1,"result":{"protocolVersion":1,"agentInfo":{...}}}
   ```

3. **As a subprocess in your own code:**
   ```python
   from chuk_acp import stdio_transport

   async with stdio_transport("python", ["examples/echo_agent.py"]) as (read, write):
       # Send messages to the agent
       pass
   ```

The agent logs debug information to `/tmp/echo_agent.log` for troubleshooting.

## Requirements

All examples require:
- Python 3.11+
- chuk-acp installed with `uv pip install -e .` from project root
- Or install from PyPI: `uv pip install chuk-acp[pydantic]`

## Learning Path

If you're new to ACP, we recommend following this order:

1. **Start with `quick_start.py`** - Get familiar with basic concepts
2. **Try `simple_client.py`** - See a minimal client implementation
3. **Review `echo_agent.py`** - Understand how agents work
4. **Explore `comprehensive_demo.py`** - See all features in action

## Common Patterns

### Creating a Transport

```python
from chuk_acp.transport.stdio import stdio_transport

async with stdio_transport(
    command="python",
    args=["agent_server.py"]
) as (read_stream, write_stream):
    # Use read_stream and write_stream for communication
    pass
```

### Protocol Handshake

```python
from chuk_acp.protocol.messages.initialize import send_initialize
from chuk_acp.protocol.types import ClientInfo, ClientCapabilities

result = await send_initialize(
    read_stream,
    write_stream,
    protocol_version=1,
    client_info=ClientInfo(name="my-client", version="1.0.0"),
    capabilities=ClientCapabilities()
)
```

### Sending a Prompt

```python
from chuk_acp.protocol.messages.session import send_session_prompt
from chuk_acp.protocol.types import TextContent

result = await send_session_prompt(
    read_stream,
    write_stream,
    session_id="session-id",
    prompt=[TextContent(text="Your prompt here")]
)
```

## Documentation

For complete API documentation, see the main project README and the ACP specification at https://agentclientprotocol.com

## Support

If you encounter issues with any examples:
1. Ensure you're using Python 3.11+
2. Verify chuk-acp is installed: `uv pip list | grep chuk-acp`
3. Check the main project's issue tracker

## Contributing

Feel free to contribute additional examples! Ideal examples:
- Focus on a specific use case
- Include clear documentation
- Handle errors gracefully
- Clean up resources properly
