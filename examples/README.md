# chuk-acp Examples

This directory contains examples demonstrating how to use chuk-acp to build ACP agents and clients.

## 🎯 Editor Integration (Use in Zed/VSCode!)

The easiest way to use chuk-acp agents is directly in your editor!

### Option 1: Local Development (Recommended)

Clone the repo and point your editor to the examples:

```json
{
  "agent_servers": {
    "Code Helper": {
      "command": "python",
      "args": ["/path/to/chuk-acp/examples/code_helper_agent.py"],
      "env": {}
    }
  }
}
```

### Option 2: Published Agents

For production use, publish your agent and use `uvx`:

```json
{
  "agent_servers": {
    "My Agent": {
      "command": "uvx",
      "args": ["--from", "my-agent-package", "my-agent"],
      "env": {}
    }
  }
}
```

See [zed_config.json](./zed_config.json) for more examples.

**Available demo agents:**
- **Echo Agent** (`echo_agent.py`) - Simple echo bot for testing
- **Code Helper** (`code_helper_agent.py`) - Coding assistant with examples and tips

## 🎯 CLI Tool (Fastest Start!)

The quickest way to interact with agents is using the `chuk-acp` CLI:

```bash
# Interactive chat with echo agent
chuk-acp python examples/echo_agent.py

# Connect to Kimi
chuk-acp kimi --acp

# Single prompt
chuk-acp python examples/echo_agent.py --prompt "Hello!"

# Using config file
chuk-acp --config examples/kimi_config.json
```

See [CLI.md](../CLI.md) for complete CLI documentation.

## 🚀 Quick Start Examples (Recommended)

These examples use the high-level `ACPClient` API - the easiest way to work with ACP agents programmatically.

### 1. simple_client.py - Basic Client Usage

The simplest example showing how to connect to an agent and send a prompt:

```bash
uv run python examples/simple_client.py
```

**What it demonstrates:**
- Creating an `ACPClient` instance
- Automatic protocol initialization
- Sending prompts and receiving responses
- Accessing agent info and session details

**Code highlights:**
```python
from chuk_acp import ACPClient

async with ACPClient("python", ["echo_agent.py"]) as client:
    result = await client.send_prompt("Hello!")
    print(f"Agent: {result.full_message}")
```

### 2. quick_start.py - Multiple Interactions

Shows how to have a multi-turn conversation with an agent:

```bash
uv run python examples/quick_start.py
```

**What it demonstrates:**
- Multiple prompts in a single session
- Accessing individual responses
- Full conversation flow

### 3. config_example.py - Configuration Support

Shows how to use `AgentConfig` for standard ACP configuration:

```bash
uv run python examples/config_example.py
```

**What it demonstrates:**
- Standard ACP configuration format (matches Zed, VSCode, etc.)
- Loading config from dictionaries
- Environment variable support
- Compatible with editor configuration files

**Config format:**
```json
{
  "command": "python",
  "args": ["agent.py"],
  "env": {
    "DEBUG": "true"
  }
}
```

### 4. echo_agent.py - Building an Agent

A complete ACP agent implementation using the high-level `ACPAgent` API - **just 35 lines of code!**

```bash
# Test with the CLI
uv run chuk-acp python examples/echo_agent.py

# Use with a client programmatically
uv run python examples/simple_client.py
```

**What it demonstrates:**
- Using the high-level `ACPAgent` base class
- Implementing `get_agent_info()` to define agent metadata
- Implementing `handle_prompt()` for agent logic
- Automatic protocol handling (init, sessions, responses)

**Code highlights:**
```python
from chuk_acp.agent import ACPAgent, AgentSession
from chuk_acp.protocol.types import AgentInfo, Content

class EchoAgent(ACPAgent):
    def get_agent_info(self) -> AgentInfo:
        return AgentInfo(name="echo-agent", version="0.1.0")

    async def handle_prompt(self, session: AgentSession, prompt: List[Content]) -> str:
        text = prompt[0].get("text", "") if prompt else ""
        return f"Echo: You said '{text}'"
```

**That's it!** The `ACPAgent` base class handles all protocol details automatically.

## 📚 Advanced Examples (Low-Level API)

For users who need fine-grained control over the protocol, see the `low_level/` directory.

### low_level/simple_client.py

Shows manual protocol handling without `ACPClient`:
- Direct use of `stdio_transport`
- Manual notification capture
- Request/response handling

```bash
uv run python examples/low_level/simple_client.py
```

### low_level/quick_start.py

Self-contained example with embedded agent:
- Agent and client in a single file
- Full protocol implementation
- Good for learning the protocol details

```bash
uv run python examples/low_level/quick_start.py
```

### low_level/comprehensive_demo.py

Complete demonstration of all ACP features:
- File system operations
- Terminal operations
- Session management
- All protocol capabilities

```bash
uv run python examples/low_level/comprehensive_demo.py
```

## 🎯 Which Example Should I Use?

| If you want to...                          | Use this example           |
|--------------------------------------------|----------------------------|
| **Get started quickly**                    | `simple_client.py`         |
| **See a complete conversation**            | `quick_start.py`           |
| **Use standard ACP config format**         | `config_example.py`        |
| **Build your own agent**                   | `echo_agent.py`            |
| **Understand the protocol details**        | `low_level/quick_start.py` |
| **See all ACP features**                   | `low_level/comprehensive_demo.py` |
| **Fine-grained protocol control**          | `low_level/simple_client.py` |

## 💡 Design Patterns

### High-Level Client Pattern (Recommended)

**Option A: Direct Usage**
```python
from chuk_acp import ACPClient

async with ACPClient("python", ["agent.py"]) as client:
    # Everything is handled automatically!
    result = await client.send_prompt("Hello!")
    print(result.full_message)
```

**Option B: Using Configuration (Matches Editor Configs)**
```python
from chuk_acp import ACPClient, AgentConfig

config = AgentConfig(
    command="kimi",
    args=["--acp"],
    env={"DEBUG": "true"}
)

async with ACPClient.from_config(config) as client:
    result = await client.send_prompt("Hello!")
    print(result.full_message)
```

**Benefits:**
- ✅ Automatic initialization
- ✅ Session management handled
- ✅ Notifications captured automatically
- ✅ Resource cleanup guaranteed
- ✅ Simple, readable code
- ✅ Standard config format (compatible with Zed, VSCode, etc.)

### High-Level Agent Pattern (Recommended for Building Agents)

```python
from chuk_acp.agent import ACPAgent, AgentSession
from chuk_acp.protocol.types import AgentInfo, Content

class MyAgent(ACPAgent):
    def get_agent_info(self) -> AgentInfo:
        return AgentInfo(name="my-agent", version="1.0.0")

    async def handle_prompt(self, session: AgentSession, prompt: List[Content]) -> str:
        text = prompt[0].get("text", "") if prompt else ""
        return f"Response to: {text}"

if __name__ == "__main__":
    MyAgent().run()
```

**Benefits:**
- ✅ Protocol details handled automatically (initialize, sessions, responses)
- ✅ Just implement 2 methods: `get_agent_info()` and `handle_prompt()`
- ✅ Session management included
- ✅ Error handling and logging built-in
- ✅ Works with any ACP client or editor
- ✅ **80% less code** than manual implementation

### Low-Level Pattern (Advanced)

```python
from chuk_acp import stdio_transport, send_initialize, send_session_new
from chuk_acp.protocol import create_request, METHOD_SESSION_PROMPT

async with stdio_transport("python", ["agent.py"]) as (read, write):
    init = await send_initialize(read, write, ...)
    session = await send_session_new(read, write, ...)

    # Manual request/response handling
    request = create_request(method=METHOD_SESSION_PROMPT, ...)
    await write.send(request)

    # Manual notification capture
    while True:
        message = await read.receive()
        # ... handle notifications and responses
```

**Benefits:**
- ✅ Full control over protocol flow
- ✅ Can implement custom behavior
- ✅ Good for debugging
- ✅ Educational for learning ACP

## 🔧 Running the Examples

### Prerequisites

```bash
# Install chuk-acp with pydantic support
uv pip install -e ".[pydantic]"
```

### Running Individual Examples

```bash
# High-level examples (start here!)
uv run python examples/simple_client.py       # Basic usage
uv run python examples/quick_start.py         # Multi-turn conversation
uv run python examples/config_example.py      # Configuration support

# Low-level examples (advanced)
uv run python examples/low_level/simple_client.py        # Manual protocol
uv run python examples/low_level/quick_start.py          # Self-contained
uv run python examples/low_level/comprehensive_demo.py   # All features
```

## 📝 Notes

### About echo_agent.py

The `echo_agent.py` is an ACP **agent server** that communicates via stdin/stdout. When run directly, it waits for JSON-RPC messages on stdin:

```bash
# Running alone won't show much output
python examples/echo_agent.py
# (It's waiting for protocol messages on stdin)

# Use with a client instead
python examples/simple_client.py
```

**Three ways to use the agent:**

1. **With a client (recommended):**
   ```bash
   uv run python examples/simple_client.py
   ```

2. **Manual testing with piped input:**
   ```bash
   echo '{"jsonrpc":"2.0","method":"initialize","params":{},"id":"1"}' | python examples/echo_agent.py
   ```

3. **As a subprocess in your code:**
   ```python
   async with ACPClient("python", ["echo_agent.py"]) as client:
       # Client handles all communication
   ```

### Debug Logging

The echo agent logs to `~/.local/share/chuk-acp/echo-agent.log` by default. Check this file for debugging:

```bash
tail -f ~/.local/share/chuk-acp/echo-agent.log
```

## 🎓 Learning Path

1. **Start with `simple_client.py`** - Understand the basics
2. **Read `echo_agent.py`** - See how agents work
3. **Try `quick_start.py`** - Multi-turn conversations
4. **Explore `low_level/quick_start.py`** - Understand protocol details
5. **Study `low_level/comprehensive_demo.py`** - See all features

## 📖 Additional Resources

- [Main README](../README.md) - Complete documentation
- [ACP Specification](https://agentclientprotocol.com) - Protocol details
- [API Reference](../README.md#api-reference) - Full API documentation

## 🤝 Contributing

Found a bug or have an idea for a better example? Please [open an issue](https://github.com/chuk-ai/chuk-acp/issues) or submit a pull request!
