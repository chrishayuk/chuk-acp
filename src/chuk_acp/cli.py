"""Command-line interface for interacting with ACP agents."""

import argparse
import asyncio
import sys
from typing import Optional

from chuk_acp.client import ACPClient, AgentConfig, load_agent_config
from chuk_acp.protocol.types import ClientInfo


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for CLI."""
    parser = argparse.ArgumentParser(
        description="Interactive client for Agent Client Protocol (ACP) agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode with echo agent
  chuk-acp python examples/echo_agent.py

  # Single prompt
  chuk-acp python examples/echo_agent.py --prompt "Hello!"

  # Using a config file
  chuk-acp --config agent_config.json

  # Connect to Kimi
  chuk-acp kimi --acp

  # With working directory
  chuk-acp python agent.py --cwd /tmp

  # With environment variables
  chuk-acp python agent.py --env DEBUG=true --env LOG_LEVEL=info
        """,
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
        "command",
        type=str,
        nargs="?",
        help="Command to run the agent (e.g., 'python', 'kimi')",
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


async def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Determine how to create the client
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
    elif args.command:
        # Create config from command line args
        env = parse_env_vars(args.env)
        config = AgentConfig(
            command=args.command,
            args=args.args or [],
            env=env,
            cwd=args.cwd,
        )
    else:
        print("Error: Either --config or command must be specified", file=sys.stderr)
        print("\nQuick examples:", file=sys.stderr)
        print("  # Try the echo agent:", file=sys.stderr)
        print("  chuk-acp python -m chuk_acp.examples.echo_agent", file=sys.stderr)
        print("\n  # Or connect to an external agent:", file=sys.stderr)
        print("  chuk-acp kimi --acp", file=sys.stderr)
        print("\n  # Or use a config file:", file=sys.stderr)
        print("  chuk-acp --config agent_config.json", file=sys.stderr)
        print("\nFor more help: chuk-acp --help", file=sys.stderr)
        sys.exit(1)

    # Create client info
    client_info = ClientInfo(
        name=args.client_name,
        version=args.client_version,
    )

    # Connect to agent
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
