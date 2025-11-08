# chuk-acp CLI

Interactive command-line client for Agent Client Protocol (ACP) agents.

## Installation

### Using uvx (Recommended)

The fastest way to use the CLI without installation:

```bash
# Run directly with uvx (no installation needed!)

# Connect to Claude Code (requires ANTHROPIC_API_KEY)
ANTHROPIC_API_KEY=sk-... uvx chuk-acp claude-code-acp

# Connect to Kimi
uvx chuk-acp kimi --acp

# Connect to echo agent
uvx chuk-acp python examples/echo_agent.py

# With pydantic for faster validation (optional)
uvx --from 'chuk-acp[pydantic]' chuk-acp claude-code-acp
```

### Traditional Installation

```bash
# Basic installation (works fine, uses fallback validation)
pip install chuk-acp

# With pydantic for faster validation (recommended)
pip install chuk-acp[pydantic]
```

**Note:** The CLI works without pydantic (using a fallback mechanism), but installing with `[pydantic]` provides faster validation.

## Quick Start

### Interactive Mode

Start an interactive chat session with an agent:

```bash
# With echo agent example
chuk-acp python examples/echo_agent.py

# With Kimi (requires Kimi CLI installed)
chuk-acp kimi --acp

# Using a config file
chuk-acp --config examples/kimi_config.json
```

### Single Prompt Mode

Send a single prompt and exit:

```bash
# Quick question
chuk-acp python examples/echo_agent.py --prompt "Hello!"

# With Kimi
chuk-acp kimi --acp --prompt "Explain ACP protocol"
```

## Usage

### Basic Syntax

```bash
chuk-acp [OPTIONS] COMMAND [ARGS...]
```

or

```bash
chuk-acp --config CONFIG_FILE [OPTIONS]
```

### Options

| Option | Description |
|--------|-------------|
| `--config`, `-c` | Path to agent configuration JSON file |
| `--prompt`, `-p` | Send a single prompt and exit (non-interactive) |
| `--cwd` | Working directory for the agent |
| `--env` | Environment variable (KEY=VALUE, repeatable) |
| `--client-name` | Client name to send to agent (default: chuk-acp-cli) |
| `--client-version` | Client version (default: 0.1.0) |
| `--verbose`, `-v` | Show agent info, session details, etc. |

### Interactive Commands

When in interactive mode, you can use these commands:

| Command | Description |
|---------|-------------|
| `/quit` or `/exit` | Exit the client |
| `/new` | Start a new session |
| `/info` | Show agent information |

## Examples

### Connect to Echo Agent

```bash
# Interactive mode
chuk-acp python examples/echo_agent.py

# Single prompt
chuk-acp python examples/echo_agent.py --prompt "Test message"

# Verbose output
chuk-acp python examples/echo_agent.py --verbose
```

### Connect to Claude Code

[Claude Code](https://github.com/zed-industries/claude-code-acp) is Anthropic's official ACP adapter for Claude.

#### Installation

Install Claude Code adapter:

```bash
npm install -g @zed-industries/claude-code-acp
```

#### Usage

```bash
# Direct command (requires API key)
ANTHROPIC_API_KEY=sk-... chuk-acp claude-code-acp

# Using config file
chuk-acp --config examples/claude_code_config.json

# Single prompt
ANTHROPIC_API_KEY=sk-... chuk-acp claude-code-acp --prompt "Refactor this function"

# Verbose mode
ANTHROPIC_API_KEY=sk-... chuk-acp claude-code-acp --verbose
```

#### Features

Claude Code provides:
- Context integration with @-mentions
- Media/image support
- Tool execution with permissions
- Code review and edit functionality
- TODO list management
- Terminal access (interactive & background)
- Custom slash commands
- MCP server integration

### Connect to Kimi

[Kimi](https://github.com/MoonshotAI/kimi-cli) is an AI coding agent that supports ACP.

#### Installation

Install the Kimi CLI:

```bash
npm install -g @moonshot-ai/kimi-cli
# or
brew install moonshot-ai/tap/kimi
```

#### Usage

```bash
# Direct command
chuk-acp kimi --acp

# Using config file
chuk-acp --config examples/kimi_config.json

# Single prompt
chuk-acp kimi --acp --prompt "Create a Python function to calculate factorial"

# Verbose mode
chuk-acp kimi --acp --verbose
```

#### Example Session

```bash
$ chuk-acp kimi --acp

╔═══════════════════════════════════════════════════════════════╗
║           ACP Interactive Client                              ║
╚═══════════════════════════════════════════════════════════════╝

Type your messages below. Commands:
  /quit or /exit - Exit the client
  /new - Start a new session
  /info - Show agent information

You: Create a Python function to calculate fibonacci numbers

Agent: Here's a Python function to calculate Fibonacci numbers:

def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b

You: /quit
Goodbye!
```

### Using Configuration Files

Create a JSON configuration file:

**kimi_config.json:**
```json
{
  "command": "kimi",
  "args": ["--acp"],
  "env": {}
}
```

**custom_agent.json:**
```json
{
  "command": "python",
  "args": ["my_agent.py"],
  "env": {
    "DEBUG": "true",
    "LOG_LEVEL": "info"
  },
  "cwd": "/path/to/agent"
}
```

Then use with:

```bash
chuk-acp --config kimi_config.json
chuk-acp --config custom_agent.json --prompt "Hello!"
```

### Environment Variables

Pass environment variables to the agent:

```bash
chuk-acp python agent.py \
  --env DEBUG=true \
  --env LOG_LEVEL=info \
  --env API_KEY=your-key
```

### Working Directory

Specify a working directory for the agent:

```bash
chuk-acp python agent.py --cwd /tmp
```

### Custom Client Info

Set custom client name and version:

```bash
chuk-acp kimi --acp \
  --client-name "my-client" \
  --client-version "1.0.0"
```

## Configuration File Format

Configuration files use the standard ACP configuration format (compatible with Zed, VSCode, etc.):

```json
{
  "command": "agent-command",
  "args": ["--flag1", "--flag2"],
  "env": {
    "KEY": "value"
  },
  "cwd": "/optional/working/directory"
}
```

### Fields

- `command` (required): The command to execute (e.g., "python", "kimi", "node")
- `args` (optional): Array of arguments to pass to the command
- `env` (optional): Object of environment variables
- `cwd` (optional): Working directory for the agent process

## Troubleshooting

### Command Not Found

If you see "command not found: chuk-acp", ensure the package is installed:

```bash
pip install chuk-acp[pydantic]
```

### Agent Not Found

If you see "Agent command not found", ensure:

1. The agent command is in your PATH (for system commands like `kimi`)
2. Python paths are absolute or relative to current directory
3. The agent file exists at the specified path

### Connection Errors

Use verbose mode to see detailed error information:

```bash
chuk-acp python agent.py --verbose
```

### Pydantic Not Installed

If you see "requires pydantic", install with:

```bash
pip install chuk-acp[pydantic]
```

## Advanced Usage

### Scripting with Single Prompt Mode

Use the CLI in scripts with single-prompt mode:

```bash
#!/bin/bash
RESPONSE=$(chuk-acp kimi --acp --prompt "Generate a random UUID")
echo "Agent response: $RESPONSE"
```

### Multiple Sessions

Start a new session during interaction:

```
You: Hello
Agent: Hi there!

You: /new
Started new session: session-abc123

You: This is a fresh conversation
Agent: Yes, new session started!
```

### Piping Input

You can pipe prompts to the CLI:

```bash
echo "Hello from pipe" | chuk-acp python examples/echo_agent.py
```

## See Also

- [Main README](README.md) - Complete library documentation
- [Examples](examples/README.md) - Code examples
- [ACP Specification](https://agentclientprotocol.com) - Protocol details

## Support

For issues or questions:
- GitHub Issues: https://github.com/chuk-ai/chuk-acp/issues
- ACP Specification: https://agentclientprotocol.com
