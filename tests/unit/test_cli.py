"""Test CLI module functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from flext_tap_oracle_wms import FlextTapOracleWms, cli as cli_module, main


class TestCLI:
    """Test CLI functionality."""

    @patch("flext_tap_oracle_wms.cli.FlextTapOracleWms")
    def test_main_calls_tap_cli(self, mock_tap_class: Mock) -> None:
        """Test that main() calls FlextTapOracleWms.cli()."""
        main()
        mock_tap_class.assert_called_once_with()
        mock_tap_class.return_value.cli.assert_called_once_with()

    @patch("flext_tap_oracle_wms.cli.FlextTapOracleWms")
    def test_main_function_callable(self, mock_tap_class: Mock) -> None:
        """Test that main function exists and is callable."""
        assert callable(main)
        main()
        mock_tap_class.return_value.cli.assert_called_once_with()

    def test_cli_module_structure(self) -> None:
        """Test CLI module has expected structure."""
        assert hasattr(cli_module, "main")
        assert callable(cli_module.main)
        assert cli_module.__doc__ is not None
        if "Singer SDK CLI Integration" not in cli_module.__doc__:
            msg: str = (
                f"Expected {'Singer SDK CLI Integration'} in {cli_module.__doc__}"
            )
            raise AssertionError(msg)
        assert main.__doc__ is not None
        if "Execute Oracle WMS tap" not in main.__doc__:
            main_msg: str = f"Expected {'Execute Oracle WMS tap'} in {main.__doc__}"
            raise AssertionError(main_msg)

    @patch("flext_tap_oracle_wms.cli.main")
    def test_cli_main_script_execution(self, mock_main: Mock) -> None:
        """Test CLI main execution when run as script."""
        assert hasattr(cli_module, "main")
        assert callable(cli_module.main)
        cli_module.main()
        mock_main.assert_called_once()

    @patch("flext_tap_oracle_wms.cli.FlextTapOracleWms")
    def test_main_exception_handling(self, mock_tap_class: Mock) -> None:
        """Test main function handles exceptions properly."""
        mock_tap_class.return_value.cli.side_effect = SystemExit(0)
        with pytest.raises(SystemExit):
            main()
        mock_tap_class.return_value.cli.assert_called_once_with()

    @patch("flext_tap_oracle_wms.cli.FlextTapOracleWms")
    def test_main_function_return_value(self, mock_tap_class: Mock) -> None:
        """Test main function return value."""
        mock_tap_class.return_value.cli.return_value = None
        main()
        mock_tap_class.return_value.cli.assert_called_once_with()

    def test_module_imports(self) -> None:
        """Test that CLI module imports are correct."""
        assert hasattr(cli_module, "FlextTapOracleWms")
        assert cli_module.FlextTapOracleWms is FlextTapOracleWms


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
