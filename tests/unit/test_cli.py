"""Test CLI module functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from unittest.mock import Mock, patch

from flext_tap_oracle_wms import main
from flext_tests import tm


class TestsFlextTapOracleWmsCli:
    """Test CLI functionality."""

    @patch("flext_tap_oracle_wms.cli.FlextTapOracleWmsService")
    def test_main_returns_service_exit_code(self, mock_service_cls: Mock) -> None:
        """Main returns the exit code produced by the service CLI."""
        mock_service_cls.return_value.cli_main.return_value = 7
        tm.that(main(), eq=7)
        mock_service_cls.return_value.cli_main.assert_called_once_with()

    @patch("flext_tap_oracle_wms.cli.FlextTapOracleWmsService")
    def test_main_function_callable(self, mock_service_cls: Mock) -> None:
        """Main remains a callable project entry point."""
        assert callable(main)
        mock_service_cls.return_value.cli_main.return_value = 0
        tm.that(main(), eq=0)
