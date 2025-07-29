"""Test CLI module functionality."""

import flext_tap_oracle_wms.cli as cli_module
import flext_tap_oracle_wms.cli as cli_module
import flext_tap_oracle_wms.cli as cli_module
from flext_tap_oracle_wms.tap import TapOracleWMS

# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from flext_tap_oracle_wms.cli import main


class TestCLI:
    """Test CLI functionality."""

    @patch("flext_tap_oracle_wms.tap.TapOracleWMS.cli")
    def test_main_calls_tap_cli(self, mock_cli: Mock) -> None:
        """Test that main() calls TapOracleWMS.cli()."""
        main()
        mock_cli.assert_called_once()

    @patch("flext_tap_oracle_wms.tap.TapOracleWMS.cli")
    def test_main_function_exists(self, mock_cli: Mock) -> None:
        """Test that main function exists and is callable."""
        assert callable(main)

        # Call main and verify it delegates to tap CLI
        main()
        mock_cli.assert_called_once()

    def test_cli_module_structure(self) -> None:
        """Test CLI module has expected structure."""


        # Check main function exists
        assert hasattr(cli_module, "main")
        assert callable(cli_module.main)

        # Check docstring
        assert cli_module.__doc__ is not None
        if "CLI entry point" not in cli_module.__doc__:
            raise AssertionError(f"Expected {"CLI entry point"} in {cli_module.__doc__}")

        # Check main function docstring
        assert main.__doc__ is not None
        if "CLI entry point" not in main.__doc__:
            raise AssertionError(f"Expected {"CLI entry point"} in {main.__doc__}")

    @patch("flext_tap_oracle_wms.cli.main")
    def test_cli_main_execution(self, mock_main: Mock) -> None:
        """Test CLI main execution when run as script."""
        # Import the CLI module


        # Test that main function is available
        assert hasattr(cli_module, "main")
        assert callable(cli_module.main)

        # Call main directly (which should be mocked)
        cli_module.main()

        # Verify main was called
        mock_main.assert_called_once()

    @patch("flext_tap_oracle_wms.tap.TapOracleWMS.cli")
    def test_main_with_exception_handling(self, mock_cli: Mock) -> None:
        """Test main function handles exceptions properly."""
        # Configure mock to raise an exception
        mock_cli.side_effect = SystemExit(0)

        # Should propagate SystemExit (normal CLI behavior)
        with pytest.raises(SystemExit):
            main()

        mock_cli.assert_called_once()

    @patch("flext_tap_oracle_wms.tap.TapOracleWMS.cli")
    def test_main_return_value(self, mock_cli: Mock) -> None:
        """Test main function return value."""
        mock_cli.return_value = None

        main()  # main() returns None, no need to check return value
        mock_cli.assert_called_once()

    def test_module_imports(self) -> None:
        """Test that CLI module imports are correct."""


        # Check that TapOracleWMS is imported
        assert hasattr(cli_module, "TapOracleWMS")


        assert cli_module.TapOracleWMS is TapOracleWMS


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
