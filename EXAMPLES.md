# Chuk-ACP Example Scripts

This document provides an overview of the example scripts included with chuk-acp.

## Quick Start

The fastest way to get started with chuk-acp:

```bash
python examples/quick_start.py
```

This minimal example (~130 lines) demonstrates:
- Creating a simple ACP agent
- Establishing stdio transport
- Performing the initialization handshake
- Sending a prompt and receiving a response
- Proper cleanup

**Perfect for:** First-time users who want to see ACP in action quickly.

## Comprehensive Demo

A complete walkthrough of all ACP features:

```bash
python examples/comprehensive_demo.py
```

This detailed example (~400 lines) demonstrates:
- Full stdio transport lifecycle
- ACP protocol handshake (initialize)
- Session creation and management
- Sending prompts to the agent
- Filesystem operations (read/write files via agent)
- Terminal session creation
- Detailed logging and error handling
- Proper resource cleanup

**Perfect for:** Understanding all ACP capabilities and best practices.

## Running the Examples

### Prerequisites

```bash
# Install chuk-acp
pip install -e .

# Or with uv
uv pip install -e .
```

### Execution

All examples are standalone and self-contained:

```bash
# Quick start (30 seconds)
python examples/quick_start.py

# Comprehensive demo (1 minute)  
python examples/comprehensive_demo.py

# Echo agent (runs as server)
python examples/echo_agent.py
```

## Example Output

### Quick Start Output

```
=== ACP Quick Start ===

1. Creating agent server...
2. Connecting to agent...
3. Initializing protocol...
   Connected to: echo-agent
4. Creating session...
   Session ID: session-1
5. Sending prompt...

✓ Success!
   Stop Reason: end_turn
   Response: Agent completed processing the prompt

✓ Cleanup complete
```

### Comprehensive Demo Output

The comprehensive demo provides detailed step-by-step output for:
- Transport connection establishment
- Protocol version negotiation
- Agent capabilities discovery
- Session lifecycle management
- File operations with verification
- Terminal creation

See the full output by running the script.

## Learning Path

Recommended order for learning chuk-acp:

1. **Start**: Run `quick_start.py` to see basic operation
2. **Explore**: Review the source code of `quick_start.py` (~130 lines)
3. **Deep dive**: Run `comprehensive_demo.py` for all features
4. **Understand**: Study `echo_agent.py` to learn agent implementation
5. **Build**: Create your own agent or client using the patterns shown

## Code Patterns

### Basic Client Pattern

```python
import anyio
from chuk_acp.transport.stdio import stdio_transport
from chuk_acp.protocol.messages.initialize import send_initialize
from chuk_acp.protocol.types import ClientInfo, ClientCapabilities

async def connect_to_agent():
    async with stdio_transport("python", ["agent.py"]) as (read, write):
        # Initialize
        result = await send_initialize(
            read, write,
            protocol_version=1,
            client_info=ClientInfo(name="my-client", version="1.0.0"),
            capabilities=ClientCapabilities()
        )
        
        # Use the connection...
        print(f"Connected to {result.agentInfo.name}")
        
anyio.run(connect_to_agent)
```

### Basic Agent Pattern

```python
import sys
import json

def handle_request(request):
    method = request.get("method")
    req_id = request.get("id")
    
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": 1,
                "agentInfo": {"name": "my-agent", "version": "1.0.0"},
                "agentCapabilities": {}
            }
        }
    # Handle other methods...

while True:
    line = sys.stdin.readline()
    if not line:
        break
    request = json.loads(line)
    response = handle_request(request)
    sys.stdout.write(json.dumps(response) + "\n")
    sys.stdout.flush()
```

## Customizing Examples

All examples are designed to be modified:

- Change the agent behavior in the embedded server code
- Add new ACP operations (permissions, tools, MCP servers)
- Experiment with different transport configurations
- Add error handling for specific scenarios

## Troubleshooting

### Import Errors

```
ModuleNotFoundError: No module named 'chuk_acp'
```

**Solution:** Install chuk-acp: `pip install -e .`

### Connection Errors

```
Transport connection failed
```

**Solution:** Ensure Python 3.11+ is installed and accessible

### Agent Not Responding

- Check that the agent script is executable
- Verify JSON-RPC message format
- Enable debug logging in the agent

## Next Steps

After running the examples:

1. Read the [ACP Specification](https://agentclientprotocol.com)
2. Review the API documentation in the main README
3. Explore the test suite in `tests/` for more usage patterns
4. Build your own agent or integrate with existing tools

## Support

For issues or questions:
- Check the [main README](README.md)
- Review the [examples README](examples/README.md)
- File an issue on the project repository

## Contributing Examples

We welcome new examples! Good examples:
- Solve a specific use case
- Include clear documentation
- Handle errors gracefully
- Clean up resources properly
- Are self-contained and runnable

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
