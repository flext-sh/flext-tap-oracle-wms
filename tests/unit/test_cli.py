"""Test CLI module functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from unittest.mock import Mock, patch

from flext_tap_oracle_wms import FlextTapOracleWmsService, cli as cli_module, main


class TestCLI:
    """Test CLI functionality."""

    @patch("flext_tap_oracle_wms.cli.FlextTapOracleWmsService.get_instance")
    def test_main_returns_service_exit_code(self, mock_get_instance: Mock) -> None:
        """Main returns the exit code produced by the service CLI."""
        mock_get_instance.return_value.cli_main.return_value = 7
        assert main() == 7
        mock_get_instance.return_value.cli_main.assert_called_once_with()

    @patch("flext_tap_oracle_wms.cli.FlextTapOracleWmsService.get_instance")
    def test_main_function_callable(self, mock_get_instance: Mock) -> None:
        """Main remains a callable project entry point."""
        assert callable(main)
        mock_get_instance.return_value.cli_main.return_value = 0
        assert main() == 0

    def test_cli_module_structure(self) -> None:
        """CLI module exposes the service-based entry point."""
        assert callable(cli_module.main)
        assert cli_module.__doc__ is not None
        assert main.__doc__ is not None
        assert "service CLI bridge" in (main.__doc__ or "")

    def test_module_imports(self) -> None:
        """CLI module re-exports the service facade it dispatches through."""
        assert cli_module.FlextTapOracleWmsService is FlextTapOracleWmsService
