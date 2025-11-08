"""Simple echo agent for testing ACP protocol.

This agent echoes back user prompts with a simple response.
It's useful for testing the protocol implementation.
"""

import json
import logging
import sys
from typing import Any, Dict

# Set up logging
logging.basicConfig(level=logging.DEBUG, filename="/tmp/echo_agent.log")
logger = logging.getLogger(__name__)


class EchoAgent:
    """Simple echo agent that responds to prompts."""

    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize request."""
        logger.info(f"Initialize: {params}")

        return {
            "protocolVersion": params.get("protocolVersion", 1),
            "agentInfo": {
                "name": "echo-agent",
                "version": "0.1.0",
                "title": "Echo Agent",
            },
            "agentCapabilities": {},
        }

    def handle_session_new(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle session/new request."""
        import uuid

        session_id = f"session_{uuid.uuid4().hex[:8]}"
        self.sessions[session_id] = {
            "cwd": params.get("cwd"),
            "history": [],
        }

        logger.info(f"Created session: {session_id}")

        return {"sessionId": session_id}

    def handle_session_prompt(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle session/prompt request."""
        session_id = params["sessionId"]
        prompt = params["prompt"]

        logger.info(f"Prompt for {session_id}: {prompt}")

        if session_id not in self.sessions:
            raise Exception(f"Unknown session: {session_id}")

        # Send a session/update notification with the response
        update = {
            "jsonrpc": "2.0",
            "method": "session/update",
            "params": {
                "sessionId": session_id,
                "agentMessageChunk": {
                    "type": "text",
                    "text": f"Echo: You said '{prompt[0].get('text', '')}'",
                },
            },
        }

        sys.stdout.write(json.dumps(update) + "\n")
        sys.stdout.flush()

        # Return the result
        return {"stopReason": "end_turn"}

    def handle_message(self, message: Dict[str, Any]) -> None:
        """Handle incoming JSON-RPC message."""
        logger.debug(f"Received: {message}")

        method = message.get("method")
        params = message.get("params", {})
        msg_id = message.get("id")

        try:
            # Route to handler
            if method == "initialize":
                result = self.handle_initialize(params)
            elif method == "session/new":
                result = self.handle_session_new(params)
            elif method == "session/prompt":
                result = self.handle_session_prompt(params)
            else:
                raise Exception(f"Unknown method: {method}")

            # Send success response
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": result,
            }

            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()

        except Exception as e:
            logger.error(f"Error handling {method}: {e}")

            # Send error response
            error_response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32603,
                    "message": str(e),
                },
            }

            sys.stdout.write(json.dumps(error_response) + "\n")
            sys.stdout.flush()

    def run(self):
        """Run the agent (read stdin, write stdout)."""
        logger.info("Echo agent started")

        try:
            for line in sys.stdin:
                line = line.strip()
                if not line:
                    continue

                try:
                    message = json.loads(line)
                    self.handle_message(message)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")

        except KeyboardInterrupt:
            logger.info("Agent interrupted")
        except Exception as e:
            logger.error(f"Agent error: {e}")

        logger.info("Echo agent stopped")


if __name__ == "__main__":
    agent = EchoAgent()
    agent.run()
