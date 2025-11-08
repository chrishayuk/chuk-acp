"""Helper utilities for accessing bundled examples."""

import sys
from pathlib import Path
from typing import Optional


def get_examples_dir() -> Optional[Path]:
    """Get the path to bundled examples.

    Returns:
        Path to examples directory, or None if not found
    """
    # Try different possible locations
    locations = []

    # 1. Development mode - examples/ in repo root
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller bundle
        locations.append(Path(getattr(sys, "_MEIPASS")) / "examples")
    else:
        # Try relative to this file (for development)
        src_path = Path(__file__).parent.parent.parent
        locations.append(src_path / "examples")

    # 2. Installed via pip/uvx - in share/chuk-acp/examples
    if hasattr(sys, "prefix"):
        locations.append(Path(sys.prefix) / "share" / "chuk-acp" / "examples")

    # 3. User site packages
    if hasattr(sys, "base_prefix"):
        locations.append(Path(sys.base_prefix) / "share" / "chuk-acp" / "examples")

    # Check each location
    for location in locations:
        if location.exists() and location.is_dir():
            return location

    return None


def get_example_path(name: str) -> Optional[Path]:
    """Get path to a specific example file.

    Args:
        name: Example name (e.g., "echo_agent.py" or "code_helper_agent.py")

    Returns:
        Path to example file, or None if not found
    """
    examples_dir = get_examples_dir()
    if not examples_dir:
        return None

    example_path = examples_dir / name
    if example_path.exists():
        return example_path

    return None


def list_examples() -> list[str]:
    """List all available examples.

    Returns:
        List of example file names
    """
    examples_dir = get_examples_dir()
    if not examples_dir:
        return []

    examples = []
    for path in examples_dir.glob("*.py"):
        examples.append(path.name)

    return sorted(examples)
