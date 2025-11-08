"""Tests for examples_finder utility."""

import sys
from pathlib import Path
from unittest.mock import patch

from chuk_acp.utils.examples_finder import (
    get_examples_dir,
    get_example_path,
    list_examples,
)


class TestGetExamplesDir:
    """Test get_examples_dir function."""

    def test_finds_examples_in_development_mode(self):
        """Test finding examples directory in development mode."""
        examples_dir = get_examples_dir()

        # Should find the examples directory
        assert examples_dir is not None
        assert examples_dir.exists()
        assert examples_dir.is_dir()
        assert examples_dir.name == "examples"

    def test_examples_dir_contains_expected_files(self):
        """Test that examples directory contains expected files."""
        examples_dir = get_examples_dir()

        assert examples_dir is not None

        # Check for some known example files
        expected_files = [
            "echo_agent.py",
            "code_helper_agent.py",
            "standalone_agent.py",
            "simple_client.py",
        ]

        for filename in expected_files:
            assert (examples_dir / filename).exists(), f"Missing {filename}"

    def test_returns_none_when_not_found(self):
        """Test that None is returned when examples dir not found."""
        # Mock Path to return objects that don't exist
        with patch("chuk_acp.utils.examples_finder.Path") as mock_path_class:
            # Create a mock path object that doesn't exist
            mock_path_obj = mock_path_class.return_value
            mock_path_obj.exists.return_value = False
            mock_path_obj.is_dir.return_value = False
            mock_path_obj.__truediv__.return_value = mock_path_obj
            mock_path_obj.parent.parent.parent = mock_path_obj

            # Also mock sys attributes
            with patch.object(sys, "prefix", "/nonexistent"):
                with patch.object(sys, "base_prefix", "/nonexistent"):
                    result = get_examples_dir()

                    # Should return None when no directory exists
                    assert result is None

    def test_checks_multiple_locations(self):
        """Test that multiple locations are checked."""
        # The function should check:
        # 1. Development mode (relative to source)
        # 2. sys.prefix/share/chuk-acp/examples
        # 3. sys.base_prefix/share/chuk-acp/examples

        examples_dir = get_examples_dir()

        # In development/testing, should find it in development location
        assert examples_dir is not None


class TestGetExamplePath:
    """Test get_example_path function."""

    def test_finds_existing_example(self):
        """Test finding an existing example file."""
        example_path = get_example_path("echo_agent.py")

        assert example_path is not None
        assert example_path.exists()
        assert example_path.is_file()
        assert example_path.name == "echo_agent.py"

    def test_finds_code_helper_agent(self):
        """Test finding code_helper_agent.py."""
        example_path = get_example_path("code_helper_agent.py")

        assert example_path is not None
        assert example_path.exists()
        assert example_path.name == "code_helper_agent.py"

    def test_finds_standalone_agent(self):
        """Test finding standalone_agent.py."""
        example_path = get_example_path("standalone_agent.py")

        assert example_path is not None
        assert example_path.exists()
        assert example_path.name == "standalone_agent.py"

    def test_returns_none_for_nonexistent_file(self):
        """Test that None is returned for non-existent file."""
        example_path = get_example_path("nonexistent_agent.py")

        assert example_path is None

    def test_returns_none_when_examples_dir_not_found(self):
        """Test returns None when examples directory doesn't exist."""
        with patch("chuk_acp.utils.examples_finder.get_examples_dir") as mock_get_dir:
            mock_get_dir.return_value = None

            result = get_example_path("echo_agent.py")

            assert result is None


class TestListExamples:
    """Test list_examples function."""

    def test_lists_example_files(self):
        """Test listing example files."""
        examples = list_examples()

        # Should return a list
        assert isinstance(examples, list)

        # Should contain known examples
        assert "echo_agent.py" in examples
        assert "code_helper_agent.py" in examples
        assert "standalone_agent.py" in examples
        assert "simple_client.py" in examples

    def test_returns_sorted_list(self):
        """Test that examples are sorted."""
        examples = list_examples()

        # Should be sorted alphabetically
        assert examples == sorted(examples)

    def test_only_includes_py_files(self):
        """Test that only .py files are included."""
        examples = list_examples()

        # All should end with .py
        for example in examples:
            assert example.endswith(".py")

    def test_returns_empty_list_when_dir_not_found(self):
        """Test returns empty list when examples dir not found."""
        with patch("chuk_acp.utils.examples_finder.get_examples_dir") as mock_get_dir:
            mock_get_dir.return_value = None

            result = list_examples()

            assert result == []

    def test_list_contains_expected_count(self):
        """Test that we have a reasonable number of examples."""
        examples = list_examples()

        # Should have at least a few examples
        assert len(examples) >= 4  # At least echo, code_helper, standalone, simple_client


class TestExamplesFinderIntegration:
    """Integration tests for examples_finder."""

    def test_can_find_and_list_all_examples(self):
        """Test complete workflow of finding and listing examples."""
        # Get examples directory
        examples_dir = get_examples_dir()
        assert examples_dir is not None

        # List all examples
        examples = list_examples()
        assert len(examples) > 0

        # Verify each listed example can be found individually
        for example_name in examples:
            example_path = get_example_path(example_name)
            assert example_path is not None
            assert example_path.exists()

    def test_all_listed_examples_are_in_examples_dir(self):
        """Test that all listed examples are in the examples directory."""
        examples_dir = get_examples_dir()
        assert examples_dir is not None

        examples = list_examples()

        for example_name in examples:
            expected_path = examples_dir / example_name
            assert expected_path.exists()

    def test_example_paths_are_absolute(self):
        """Test that returned paths are absolute."""
        example_path = get_example_path("echo_agent.py")

        assert example_path is not None
        assert example_path.is_absolute()

    def test_examples_dir_path_is_absolute(self):
        """Test that examples directory path is absolute."""
        examples_dir = get_examples_dir()

        assert examples_dir is not None
        assert examples_dir.is_absolute()


class TestExamplesFinderWithMockedSys:
    """Test examples_finder with mocked sys attributes."""

    def test_pyinstaller_mode(self):
        """Test finding examples in PyInstaller mode."""
        # Create a fake PyInstaller path
        fake_meipass = Path(__file__).parent.parent / "examples"

        with patch.object(sys, "_MEIPASS", str(fake_meipass), create=True):
            examples_dir = get_examples_dir()

            # Should find it via _MEIPASS
            assert examples_dir is not None
            assert examples_dir.exists()

    def test_fallback_to_development_mode(self):
        """Test fallback to development mode when _MEIPASS doesn't exist."""
        # Even without _MEIPASS, should find examples in development
        if hasattr(sys, "_MEIPASS"):
            delattr(sys, "_MEIPASS")

        examples_dir = get_examples_dir()

        # Should still find examples (development mode)
        assert examples_dir is not None
        assert examples_dir.exists()


class TestModuleExports:
    """Test that the module exports the correct functions."""

    def test_exports_get_examples_dir(self):
        """Test that get_examples_dir is exported."""
        from chuk_acp.utils import get_examples_dir as exported_func

        assert callable(exported_func)

    def test_exports_get_example_path(self):
        """Test that get_example_path is exported."""
        from chuk_acp.utils import get_example_path as exported_func

        assert callable(exported_func)

    def test_exports_list_examples(self):
        """Test that list_examples is exported."""
        from chuk_acp.utils import list_examples as exported_func

        assert callable(exported_func)

    def test_all_exports(self):
        """Test __all__ contains expected exports."""
        from chuk_acp.utils import __all__

        assert "get_examples_dir" in __all__
        assert "get_example_path" in __all__
        assert "list_examples" in __all__
