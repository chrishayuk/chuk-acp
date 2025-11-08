#!/usr/bin/env python3
"""Standalone ACP Agent Example - No installation required!

This is a complete, self-contained ACP agent that you can copy and run.
Just save this file and run: python standalone_agent.py

Usage:
    # Test it with the chuk-acp CLI:
    uvx chuk-acp python standalone_agent.py

    # Or configure in Zed/VSCode:
    {
      "agent_servers": {
        "My Agent": {
          "command": "python",
          "args": ["/path/to/standalone_agent.py"]
        }
      }
    }

To customize this agent for your needs:
1. Change the agent name/description in get_agent_info()
2. Modify handle_prompt() to add your logic
3. Add LLM integration (OpenAI, Anthropic, Ollama, etc.)
4. Package and distribute via pip/uvx
"""

# First, check if chuk-acp is installed, if not provide instructions
try:
    from chuk_acp.agent import ACPAgent, AgentSession
    from chuk_acp.protocol.types import AgentInfo, Content
except ImportError:
    print(
        """
╔══════════════════════════════════════════════════════════════════════╗
║                    chuk-acp Not Installed                            ║
╚══════════════════════════════════════════════════════════════════════╝

This agent requires chuk-acp. Install it with:

    pip install chuk-acp

Or run without installation using uvx:

    uvx --from chuk-acp chuk-acp python standalone_agent.py

For more info: https://github.com/chuk-ai/chuk-acp
"""
    )
    import sys

    sys.exit(1)

import os
import tempfile
from typing import List


class StandaloneAgent(ACPAgent):
    """A simple standalone agent you can customize."""

    def get_agent_info(self) -> AgentInfo:
        """Return agent information."""
        return AgentInfo(
            name="standalone-agent",
            version="1.0.0",
            title="Standalone ACP Agent",
            description="A simple agent you can customize for your needs",
        )

    async def handle_prompt(self, session: AgentSession, prompt: List[Content]) -> str:
        """Handle a prompt - customize this for your use case!"""
        # Extract text from the prompt
        text = prompt[0].get("text", "") if prompt else ""

        # Simple keyword-based responses - replace with your logic
        response = self._generate_response(text)
        return response

    def _generate_response(self, prompt: str) -> str:
        """Generate a response based on the prompt.

        TODO: Replace this with your actual logic:
        - Call an LLM API (OpenAI, Anthropic, Ollama)
        - Query a database or knowledge base
        - Run code analysis tools
        - Execute shell commands
        - Anything else your agent needs to do!
        """
        prompt_lower = prompt.lower()

        # Example responses - customize these!
        if "hello" in prompt_lower or "hi" in prompt_lower:
            return """Hello! I'm a standalone ACP agent.

I'm a template you can customize for your needs. Some ideas:
- Connect me to an LLM (OpenAI, Anthropic, Ollama)
- Add database access for context
- Integrate with your company's tools
- Build domain-specific assistants

Check the code to see how easy it is to modify me!"""

        elif "help" in prompt_lower or "what can you do" in prompt_lower:
            return """I'm a customizable ACP agent template!

**Current capabilities:**
- Basic conversation (you're seeing it now!)
- Session management (built-in)
- Works with Zed, VSCode, Claude Code

**How to customize me:**
1. Edit the `_generate_response()` method
2. Add API calls (OpenAI, etc.)
3. Add your business logic
4. Package and distribute!

**Example integration:**
```python
# Add OpenAI
import openai
response = openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}]
)
return response.choices[0].message.content
```

Want to learn more? Ask me "show me code examples" """

        elif "code" in prompt_lower or "example" in prompt_lower:
            return """Here's how to customize this agent:

**1. Add LLM Integration (OpenAI):**
```python
import openai

async def handle_prompt(self, session: AgentSession, prompt: List[Content]) -> str:
    text = prompt[0].get("text", "") if prompt else ""

    # Call OpenAI
    response = await openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": text}]
    )

    return response.choices[0].message.content
```

**2. Add Context/Memory:**
```python
async def handle_prompt(self, session: AgentSession, prompt: List[Content]) -> str:
    text = prompt[0].get("text", "") if prompt else ""

    # Use session context for memory
    if "history" not in session.context:
        session.context["history"] = []

    session.context["history"].append(text)

    # Your response logic here
    return f"You've asked {len(session.context['history'])} questions"
```

**3. Add File System Access:**
```python
async def handle_prompt(self, session: AgentSession, prompt: List[Content]) -> str:
    text = prompt[0].get("text", "") if prompt else ""

    # Read files from the session's working directory
    cwd = session.cwd or "."
    # ... your file operations
```

The possibilities are endless!"""

        else:
            # Default response
            return f"""I received: "{prompt}"

I'm a template agent - customize me for your needs!

**Try asking:**
- "Hello" - Get started
- "What can you do?" - Learn about capabilities
- "Show me code examples" - See how to customize

**To make me useful:**
Replace `_generate_response()` with your logic:
- LLM API calls
- Database queries
- Tool integrations
- Custom business logic

Check the source code - it's simple to modify!"""


if __name__ == "__main__":
    # Use platform-independent temporary directory for logs
    log_path = os.path.join(tempfile.gettempdir(), "standalone_agent.log")

    # Log startup info to the log file (not stdout - that's for JSON-RPC)
    import logging

    logging.basicConfig(level=logging.INFO, filename=log_path, format="%(asctime)s - %(message)s")
    logging.info("╔══════════════════════════════════════════════════════════════════════╗")
    logging.info("║               Standalone ACP Agent Starting                          ║")
    logging.info("║  This is a template - customize it for your needs!                  ║")
    logging.info("╚══════════════════════════════════════════════════════════════════════╝")
    logging.info(f"Log file: {log_path}")

    agent = StandaloneAgent(log_file=log_path)
    agent.run()
