"""Test CLI module functionality.

``main()`` delegates to the service CLI, which runs the tap against a live
Oracle WMS Cloud endpoint. With no local WMS container that end-to-end
invocation is covered by real runs rather than by mocking the service; the
unit contract here is that the entry point stays importable and callable.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tap_oracle_wms import main
from flext_tests import tm


class TestsFlextTapOracleWmsCli:
    """Test CLI entry-point contract."""

    def test_main_is_callable_entry_point(self) -> None:
        """Main remains a callable project entry point."""
        tm.that(callable(main), eq=True)
