"""Command-line interface for interacting with ACP agents."""

import argparse
import asyncio
import os
import sys
from typing import Optional

from chuk_acp.client import ACPClient, AgentConfig, load_agent_config
from chuk_acp.protocol.types import ClientInfo


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for CLI."""
    parser = argparse.ArgumentParser(
        description="Agent Client Protocol (ACP) tool - run agents or connect as a client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect mode (interactive if TTY, passthrough if piped)
  chuk-acp python examples/echo_agent.py

  # Explicit agent passthrough mode (for editors like Zed)
  chuk-acp agent python my_agent.py

  # Explicit interactive client mode
  chuk-acp client python examples/echo_agent.py

  # Force interactive mode even when piped
  chuk-acp --interactive python examples/echo_agent.py

  # Single prompt
  chuk-acp client python examples/echo_agent.py --prompt "Hello!"

  # Using a config file
  chuk-acp --config agent_config.json

  # With working directory
  chuk-acp python agent.py --cwd /tmp

  # With environment variables
  chuk-acp python agent.py --env DEBUG=true --env LOG_LEVEL=info
        """,
    )

    # Mode selection
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Force interactive client mode even when stdin is not a TTY",
    )

    # Configuration options
    parser.add_argument(
        "--config",
        "-c",
        type=str,
        help="Path to agent configuration JSON file",
    )

    # Direct command specification
    parser.add_argument(
        "mode_or_command",
        type=str,
        nargs="?",
        help="Mode ('agent' or 'client') or command to run (e.g., 'python', 'kimi')",
    )
    parser.add_argument(
        "args",
        nargs="*",
        help="Arguments to pass to the agent command",
    )

    # Additional options
    parser.add_argument(
        "--cwd",
        type=str,
        help="Working directory for the agent",
    )
    parser.add_argument(
        "--env",
        action="append",
        help="Environment variable (format: KEY=VALUE, can be used multiple times)",
    )
    parser.add_argument(
        "--prompt",
        "-p",
        type=str,
        help="Send a single prompt and exit (non-interactive mode)",
    )
    parser.add_argument(
        "--client-name",
        type=str,
        default="chuk-acp-cli",
        help="Client name to send to agent (default: chuk-acp-cli)",
    )
    parser.add_argument(
        "--client-version",
        type=str,
        default="0.1.0",
        help="Client version to send to agent (default: 0.1.0)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output (show agent info, session details, etc.)",
    )

    return parser


def parse_env_vars(env_list: Optional[list[str]]) -> dict[str, str]:
    """Parse environment variables from KEY=VALUE format."""
    if not env_list:
        return {}

    env_dict = {}
    for env_var in env_list:
        if "=" not in env_var:
            print(f"Warning: Invalid env format '{env_var}', expected KEY=VALUE", file=sys.stderr)
            continue
        key, value = env_var.split("=", 1)
        env_dict[key] = value
    return env_dict


async def interactive_mode(client: ACPClient, verbose: bool = False) -> None:
    """Run interactive REPL mode."""
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║           ACP Interactive Client                              ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print()

    if verbose and client.agent_info:
        print(f"Connected to: {client.agent_info.name} v{client.agent_info.version}")
        if hasattr(client.agent_info, "title") and client.agent_info.title:
            print(f"Title: {client.agent_info.title}")
        if client.current_session:
            print(f"Session ID: {client.current_session.sessionId}")
        print()

    print("Type your messages below. Commands:")
    print("  /quit or /exit - Exit the client")
    print("  /new - Start a new session")
    print("  /info - Show agent information")
    print()

    try:
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.lower() in ("/quit", "/exit"):
                    print("\nGoodbye!")
                    break

                if user_input.lower() == "/new":
                    session = await client.new_session()
                    print(f"Started new session: {session.sessionId}\n")
                    continue

                if user_input.lower() == "/info":
                    if client.agent_info:
                        print(f"\nAgent: {client.agent_info.name} v{client.agent_info.version}")
                        if hasattr(client.agent_info, "title") and client.agent_info.title:
                            print(f"Title: {client.agent_info.title}")
                    if client.current_session:
                        print(f"Session: {client.current_session.sessionId}")
                    print()
                    continue

                # Send prompt to agent
                result = await client.send_prompt(user_input)

                # Display response
                if result.full_message:
                    print(f"\nAgent: {result.full_message}\n")
                else:
                    print("\n(No response from agent)\n")

                if verbose:
                    print(f"[Stop reason: {result.stop_reason}]\n")

            except KeyboardInterrupt:
                print("\n\nUse /quit or /exit to exit gracefully.")
                continue
            except EOFError:
                print("\n\nGoodbye!")
                break

    except Exception as e:
        print(f"\nError during interaction: {e}", file=sys.stderr)
        raise


async def single_prompt_mode(client: ACPClient, prompt: str, verbose: bool = False) -> None:
    """Send a single prompt and exit."""
    if verbose and client.agent_info:
        print(f"Connected to: {client.agent_info.name} v{client.agent_info.version}")
        print()

    result = await client.send_prompt(prompt)

    if result.full_message:
        print(result.full_message)
    else:
        print("(No response from agent)", file=sys.stderr)
        sys.exit(1)

    if verbose:
        print(f"\n[Stop reason: {result.stop_reason}]")


def agent_passthrough_mode(config: AgentConfig) -> None:
    """Run agent in passthrough mode - just execute the command directly.

    This mode is used by editors like Zed that want to communicate directly
    with the agent via stdio using the ACP protocol.

    The agent process handles all protocol communication - we just exec it.
    """
    import logging

    # Set up debug logging
    logging.basicConfig(
        level=logging.DEBUG,
        filename=os.path.expanduser("~/chuk_acp_passthrough.log"),
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    # Build the command
    cmd = [config.command] + config.args

    logger.debug("Agent passthrough mode starting")
    logger.debug(f"Command: {config.command}")
    logger.debug(f"Args: {config.args}")
    logger.debug(f"Full command: {cmd}")
    logger.debug(f"CWD: {config.cwd}")
    logger.debug(f"Env: {config.env}")

    # Prepare environment
    env = os.environ.copy()
    if config.env:
        env.update(config.env)

    # Add Python unbuffered mode if running Python
    if config.command == "python" or config.command == "python3":
        cmd.insert(1, "-u")
        logger.debug(f"Added -u flag, command now: {cmd}")

    # Execute the agent process, replacing this process
    # This ensures stdio is directly connected
    try:
        logger.debug(f"Executing: {cmd[0]} with args {cmd}")
        os.execvpe(cmd[0], cmd, env)
    except Exception as e:
        logger.error(f"Error executing agent: {e}")
        print(f"Error executing agent: {e}", file=sys.stderr)
        sys.exit(1)


async def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Determine mode and command
    mode = None  # 'agent', 'client', or None for auto-detect
    command = None
    command_args = []

    if args.mode_or_command:
        if args.mode_or_command in ("agent", "client"):
            # Explicit mode specified
            mode = args.mode_or_command
            if args.args:
                command = args.args[0]
                command_args = args.args[1:]
            else:
                print(f"Error: Mode '{mode}' requires a command to run", file=sys.stderr)
                sys.exit(1)
        else:
            # No explicit mode, command is first arg
            command = args.mode_or_command
            command_args = args.args or []

    # Determine configuration
    config: Optional[AgentConfig] = None

    if args.config:
        # Load from config file
        try:
            config = load_agent_config(args.config)
        except FileNotFoundError:
            print(f"Error: Config file not found: {args.config}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error loading config: {e}", file=sys.stderr)
            sys.exit(1)
    elif command:
        # Create config from command line args
        env = parse_env_vars(args.env)
        config = AgentConfig(
            command=command,
            args=command_args,
            env=env,
            cwd=args.cwd,
        )
    else:
        print("Error: Either --config or command must be specified", file=sys.stderr)
        print("\nQuick examples:", file=sys.stderr)
        print("  # Agent passthrough (for editors):", file=sys.stderr)
        print("  chuk-acp agent python my_agent.py", file=sys.stderr)
        print("\n  # Interactive client:", file=sys.stderr)
        print("  chuk-acp client python my_agent.py", file=sys.stderr)
        print("\n  # Auto-detect mode:", file=sys.stderr)
        print("  chuk-acp python my_agent.py", file=sys.stderr)
        print("\nFor more help: chuk-acp --help", file=sys.stderr)
        sys.exit(1)

    # Auto-detect mode if not explicitly set
    if mode is None:
        if args.interactive:
            mode = "client"
        elif sys.stdin.isatty():
            # Interactive terminal - use client mode
            mode = "client"
        else:
            # Piped input - use agent passthrough mode
            mode = "agent"

    # Route to appropriate mode
    if mode == "agent":
        # Agent passthrough mode - exec the agent directly
        # This does not return - it replaces the current process
        agent_passthrough_mode(config)
    else:
        # Client mode - connect to agent and provide interactive interface
        client_info = ClientInfo(
            name=args.client_name,
            version=args.client_version,
        )

        try:
            async with ACPClient.from_config(config, client_info=client_info) as client:
                if args.prompt:
                    # Single prompt mode
                    await single_prompt_mode(client, args.prompt, args.verbose)
                else:
                    # Interactive mode
                    await interactive_mode(client, args.verbose)

        except FileNotFoundError as e:
            print(f"Error: Agent command not found: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error connecting to agent: {e}", file=sys.stderr)
            if args.verbose:
                import traceback

                traceback.print_exc()
            sys.exit(1)


def cli_entry() -> None:
    """Entry point for console script."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(130)


if __name__ == "__main__":
    cli_entry()
