# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Integration package."""

from __future__ import annotations

from flext_core.lazy import install_lazy_exports

_LAZY_IMPORTS = {
    "test_functional": "tests.integration.test_functional",
    "test_streams_functional": "tests.integration.test_streams_functional",
    "test_wms": "tests.integration.test_wms",
    "test_wms_connection": "tests.integration.test_wms_connection",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)
