"""Utility functions for flext-tap-oracle-wms.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Coroutine


def run_async(coro: Coroutine[object, object, object] | Awaitable[object]) -> object:
    """Run async coroutine in sync context.
    This is a shared utility to eliminate the duplicate _run_async methods
    found in tap_client.py and tap_streams.py.

    Args:
      coro: Coroutine or awaitable to run
    Returns:
      Result of the coroutine execution

    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()
