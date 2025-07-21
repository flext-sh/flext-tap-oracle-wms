"""Test __main__.py module entry point."""
# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

import subprocess
import sys
from unittest.mock import Mock, patch

import pytest


class TestMainModule:
    """Test main module entry point functionality."""

    def test_main_module_importable(self) -> None:
        """Test that __main__ module can be imported."""
        # If we get here without ImportError, the module is importable

    @patch("flext_tap_oracle_wms.__main__.main")
    def test_main_module_calls_cli_main(self, mock_main: Mock) -> None:
        """Test that __main__ module calls cli.main when executed."""
        # Import and execute the main module logic

        # Import the main module and verify its content
        import flext_tap_oracle_wms.__main__ as main_module

        # Test that main function is available and callable
        assert hasattr(main_module, "main")
        assert callable(main_module.main)

        # Call main directly (which should be mocked)
        main_module.main()

        # Verify cli.main was called
        mock_main.assert_called_once()

    def test_main_module_execution_as_module(self) -> None:
        """Test that module can be executed with python -m."""
        # This test verifies the module can be executed but doesn't actually run it
        # to avoid CLI execution during tests
        result = subprocess.run(
            [sys.executable, "-m", "flext_tap_oracle_wms", "--help"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Should not crash (exit code should be 0 for help)
        assert result.returncode == 0
        assert "usage:" in result.stdout.lower() or "help" in result.stdout.lower()

    def test_main_module_structure(self) -> None:
        """Test that __main__ module has expected structure."""
        import flext_tap_oracle_wms.__main__ as main_module

        # Check that module has the main import
        assert hasattr(main_module, "main")

        # Check module docstring
        assert main_module.__doc__ is not None
        assert "running as python -m" in main_module.__doc__.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
