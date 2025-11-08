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
python examples/quick_start.py
```

### 2. Comprehensive Demo (`comprehensive_demo.py`)

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
python examples/comprehensive_demo.py
```

### 3. Echo Agent (`echo_agent.py`)

A simple standalone ACP agent server that echoes back messages.

**What it demonstrates:**
- Building a basic ACP-compliant agent
- Handling initialize requests
- Processing prompts
- JSON-RPC message handling

**Run it:**
```bash
python examples/echo_agent.py
```

Then connect to it with a client in another terminal.

## Requirements

All examples require:
- Python 3.11+
- chuk-acp installed (`pip install -e .` from project root)
- anyio (installed automatically with chuk-acp)

## Learning Path

If you're new to ACP, we recommend following this order:

1. **Start with `quick_start.py`** - Get familiar with basic concepts
2. **Review `echo_agent.py`** - Understand how agents work
3. **Explore `comprehensive_demo.py`** - See all features in action

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
2. Verify chuk-acp is installed: `pip list | grep chuk-acp`
3. Check the main project's issue tracker

## Contributing

Feel free to contribute additional examples! Ideal examples:
- Focus on a specific use case
- Include clear documentation
- Handle errors gracefully
- Clean up resources properly
