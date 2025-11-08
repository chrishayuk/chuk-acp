#!/usr/bin/env python3
"""Code Helper Agent - A simple coding assistant for Zed/VSCode.

This agent provides helpful coding responses and can be configured in
ACP-compatible editors like Zed, VSCode, or Claude Code.

Usage:
    # Run directly
    python examples/code_helper_agent.py

    # Or via uvx (no installation needed!)
    uvx --from chuk-acp chuk-acp python examples/code_helper_agent.py

    # Configure in Zed (settings.json):
    {
      "agent_servers": {
        "Code Helper": {
          "command": "uvx",
          "args": ["--from", "chuk-acp", "chuk-acp", "python", "examples/code_helper_agent.py"],
          "env": {}
        }
      }
    }
"""

import os
import tempfile
from typing import List

from chuk_acp.agent import ACPAgent, AgentSession
from chuk_acp.protocol.types import AgentInfo, Content


class CodeHelperAgent(ACPAgent):
    """A helpful coding assistant agent."""

    def get_agent_info(self) -> AgentInfo:
        """Return agent information."""
        return AgentInfo(
            name="code-helper",
            version="1.0.0",
            title="Code Helper Agent",
            description="A helpful coding assistant built with chuk-acp",
        )

    async def handle_prompt(self, session: AgentSession, prompt: List[Content]) -> str:
        """Handle a prompt by providing helpful coding responses."""
        # Extract text from the prompt
        text = prompt[0].get("text", "") if prompt else ""

        # Simple response logic - you could integrate with an LLM API here
        response = self._generate_response(text)

        return response

    def _generate_response(self, prompt: str) -> str:
        """Generate a helpful response to the user's prompt."""
        prompt_lower = prompt.lower()

        # Simple keyword-based responses (you could replace this with actual LLM calls)
        if "hello" in prompt_lower or "hi" in prompt_lower:
            return """Hello! I'm Code Helper, a coding assistant built with chuk-acp.

I can help you with:
- Explaining code concepts
- Providing code examples
- Debugging assistance
- Best practices
- Architecture advice

What would you like help with today?"""

        elif "python" in prompt_lower and any(
            word in prompt_lower for word in ["function", "def", "class"]
        ):
            return """Here's a Python example:

```python
def greet(name: str) -> str:
    \"\"\"Greet someone by name.\"\"\"
    return f"Hello, {name}!"

# Usage
message = greet("World")
print(message)  # Output: Hello, World!
```

Python best practices:
- Use type hints for clarity
- Write docstrings for functions
- Follow PEP 8 style guidelines
- Use descriptive variable names"""

        elif "javascript" in prompt_lower or "typescript" in prompt_lower:
            return """Here's a JavaScript/TypeScript example:

```typescript
function greet(name: string): string {
  return `Hello, ${name}!`;
}

// Usage
const message = greet("World");
console.log(message);  // Output: Hello, World!
```

JavaScript/TypeScript tips:
- Use const/let instead of var
- Prefer arrow functions for callbacks
- Use async/await for promises
- Add type annotations in TypeScript"""

        elif "help" in prompt_lower or "what can you do" in prompt_lower:
            return """I'm a code helper agent that can assist with:

📝 **Code Examples**: Ask me for examples in Python, JavaScript, TypeScript, etc.
🐛 **Debugging**: Share your error and I'll help troubleshoot
💡 **Best Practices**: Get advice on coding patterns and architecture
🔧 **Quick Fixes**: Common solutions to programming problems

**Note**: I'm a demo agent built with chuk-acp. You can:
- Extend me with real LLM integration (OpenAI, Anthropic, etc.)
- Add more languages and capabilities
- Customize responses for your team's needs

Try asking me: "Show me a Python function" or "JavaScript async example" """

        elif "acp" in prompt_lower or "chuk" in prompt_lower:
            return """I'm built using **chuk-acp**, a Python implementation of the Agent Client Protocol (ACP)!

Key features of chuk-acp:
- 🚀 High-level APIs for building agents
- 🔌 Works with Zed, VSCode, Claude Code
- 🐍 Pure Python, optional Pydantic support
- 📦 Easy distribution via uvx (no installation!)
- ✅ 100% test coverage

Example - Building an agent:
```python
from chuk_acp.agent import ACPAgent, AgentSession
from chuk_acp.protocol.types import AgentInfo, Content

class MyAgent(ACPAgent):
    def get_agent_info(self) -> AgentInfo:
        return AgentInfo(name="my-agent", version="1.0.0")

    async def handle_prompt(self, session: AgentSession, prompt: List[Content]) -> str:
        text = prompt[0].get("text", "")
        return f"You said: {text}"

if __name__ == "__main__":
    MyAgent().run()
```

Check out: https://github.com/chuk-ai/chuk-acp"""

        else:
            # Generic helpful response
            return f"""I received your message: "{prompt}"

I'm a demo code helper agent. Here are some things you can try:

💬 **Ask about programming languages**: "Show me a Python function"
🔍 **Request examples**: "JavaScript async example"
❓ **Get help**: "What can you do?"
🤖 **Learn about ACP**: "Tell me about chuk-acp"

**Want to customize me?**
This agent is open source! You can:
- Add LLM integration (OpenAI, Anthropic, Ollama)
- Connect to documentation databases
- Add code analysis tools
- Implement file operations

The code is in: examples/code_helper_agent.py"""


if __name__ == "__main__":
    # Use platform-independent temporary directory for logs
    log_path = os.path.join(tempfile.gettempdir(), "code_helper_agent.log")
    agent = CodeHelperAgent(log_file=log_path)
    agent.run()
