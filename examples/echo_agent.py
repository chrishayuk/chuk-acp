"""Simple echo agent for testing ACP protocol.

This agent echoes back user prompts, demonstrating how easy it is
to build an ACP agent using the high-level ACPAgent API.
"""

from typing import List
from chuk_acp.agent import ACPAgent, AgentSession
from chuk_acp.protocol.types import AgentInfo, Content


class EchoAgent(ACPAgent):
    """Simple echo agent that responds to prompts."""

    def get_agent_info(self) -> AgentInfo:
        """Return agent information."""
        return AgentInfo(
            name="echo-agent",
            version="0.1.0",
            title="Echo Agent",
        )

    async def handle_prompt(self, session: AgentSession, prompt: List[Content]) -> str:
        """Handle a prompt by echoing it back."""
        # Extract text from the prompt
        text = prompt[0].get("text", "") if prompt else ""

        # Return the echo response
        return f"Echo: You said '{text}'"


if __name__ == "__main__":
    agent = EchoAgent(log_file="/tmp/echo_agent.log")
    agent.run()
