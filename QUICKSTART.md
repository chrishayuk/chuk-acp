# Quick Start - No Installation Required!

Get started with chuk-acp in under 2 minutes without cloning the repo.

## Try It Now (No Installation!)

### 1. Download the Standalone Agent

```bash
# Download the example agent
curl -O https://raw.githubusercontent.com/chuk-ai/chuk-acp/main/examples/standalone_agent.py

# Or use wget
wget https://raw.githubusercontent.com/chuk-ai/chuk-acp/main/examples/standalone_agent.py
```

### 2. Run It with uvx (Recommended)

```bash
# Install chuk-acp temporarily and run your agent
uvx --from chuk-acp chuk-acp python standalone_agent.py

# Single prompt mode
uvx --from chuk-acp chuk-acp python standalone_agent.py --prompt "Hello!"
```

### 3. Or Install Permanently

```bash
# Install chuk-acp
pip install chuk-acp

# Run your agent
chuk-acp python standalone_agent.py

# Or run the agent directly
python standalone_agent.py
# (Then connect to it from another terminal with: chuk-acp python standalone_agent.py)
```

## What You Get

The `standalone_agent.py` is a complete, working ACP agent that:
- ✅ Works with Zed, VSCode, Claude Code
- ✅ Handles conversations
- ✅ Shows you how to customize it
- ✅ Includes examples for LLM integration
- ✅ Only 200 lines - easy to understand!

## Customize It

Open `standalone_agent.py` and find the `_generate_response()` method. This is where you add your logic:

```python
def _generate_response(self, prompt: str) -> str:
    """Replace this with your logic!"""

    # Option 1: Call an LLM
    import openai
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

    # Option 2: Your custom logic
    # ... analyze code, query database, etc.
```

## Use in Zed/VSCode

After downloading `standalone_agent.py`, add to your editor settings:

**Zed (`settings.json`):**
```json
{
  "agent_servers": {
    "My Agent": {
      "command": "python",
      "args": ["/absolute/path/to/standalone_agent.py"]
    }
  }
}
```

**VSCode (`.vscode/settings.json`):**
```json
{
  "acp.agents": {
    "My Agent": {
      "command": "python",
      "args": ["/absolute/path/to/standalone_agent.py"]
    }
  }
}
```

## Try External Agents

You can also connect to existing agents without any files:

```bash
# Claude Code (requires ANTHROPIC_API_KEY)
ANTHROPIC_API_KEY=sk-... uvx chuk-acp claude-code-acp

# Kimi (Chinese AI assistant)
uvx chuk-acp kimi --acp
```

## Next Steps

1. **Customize the agent** - Edit `standalone_agent.py`
2. **Add LLM integration** - OpenAI, Anthropic, Ollama, etc.
3. **Build something cool** - Code analysis, documentation, testing
4. **Share it** - Package as pip-installable module

## Examples

### Interactive Chat
```bash
$ uvx --from chuk-acp chuk-acp python standalone_agent.py

╔═══════════════════════════════════════════════════════════════╗
║           ACP Interactive Client                              ║
╚═══════════════════════════════════════════════════════════════╝

Connected to: standalone-agent v1.0.0
Session ID: session_abc123

Commands: /info, /new, /quit

You: Hello!
Agent: Hello! I'm a standalone ACP agent.

I'm a template you can customize for your needs...
```

### Single Prompt
```bash
$ uvx --from chuk-acp chuk-acp python standalone_agent.py --prompt "What can you do?"

Agent: I'm a customizable ACP agent template!

**Current capabilities:**
- Basic conversation (you're seeing it now!)
- Session management (built-in)
- Works with Zed, VSCode, Claude Code...
```

## Learn More

- 📚 [Full Documentation](https://github.com/chuk-ai/chuk-acp)
- 🎯 [More Examples](https://github.com/chuk-ai/chuk-acp/tree/main/examples)
- 🔧 [API Reference](https://github.com/chuk-ai/chuk-acp#api-reference)
- 💬 [ACP Specification](https://agentclientprotocol.com)

## Troubleshooting

**Agent won't start?**
```bash
# Make sure chuk-acp is installed
pip install chuk-acp

# Or use uvx to install it automatically
uvx --from chuk-acp chuk-acp python standalone_agent.py
```

**Can't download the file?**
```bash
# Direct link
https://raw.githubusercontent.com/chuk-ai/chuk-acp/main/examples/standalone_agent.py

# Or copy the code from
https://github.com/chuk-ai/chuk-acp/blob/main/examples/standalone_agent.py
```

**Need help?**
- [Open an issue](https://github.com/chuk-ai/chuk-acp/issues)
- [Check the FAQ](https://github.com/chuk-ai/chuk-acp#faq)
