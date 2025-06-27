#!/usr/bin/env python3
"""Validation script for modern Singer SDK 0.46.4+ patterns in tap-oracle-wms.

This script validates that all modern Singer SDK patterns have been properly
implemented and are working correctly.
"""

from pathlib import Path
import sys


# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def test_modern_imports() -> bool:
    """Test that modern Singer SDK imports work correctly."""
    try:
        # Test modern pagination import
        # Test capabilities import
        from singer_sdk.helpers.capabilities import TapCapabilities
        from singer_sdk.pagination import BaseHATEOASPaginator

        # Test modern stream import
        from tap_oracle_wms.streams import WMSAdvancedPaginator, WMSAdvancedStream

        # Test tap import with modern patterns
        from tap_oracle_wms.tap import TapOracleWMS

        return True

    except ImportError:
        return False


def test_modern_paginator() -> bool:
    """Test the modern HATEOAS paginator implementation."""
    try:
        from tap_oracle_wms.streams import WMSAdvancedPaginator

        # Create paginator instance
        paginator = WMSAdvancedPaginator()

        # Test that it inherits from BaseHATEOASPaginator
        from singer_sdk.pagination import BaseHATEOASPaginator
        assert isinstance(paginator, BaseHATEOASPaginator)

        # Test get_next_url method exists
        assert hasattr(paginator, "get_next_url")

        # Test has_more method exists
        assert hasattr(paginator, "has_more")

        return True

    except Exception:
        return False


def test_modern_capabilities() -> bool:
    """Test the modern capabilities declaration."""
    try:
        from singer_sdk.helpers.capabilities import TapCapabilities

        from tap_oracle_wms.tap import TapOracleWMS

        # Check that capabilities are declared
        assert hasattr(TapOracleWMS, "capabilities")
        capabilities = TapOracleWMS.capabilities

        # Check for required capabilities
        required_caps = [
            TapCapabilities.DISCOVER,
            TapCapabilities.STATE,
            TapCapabilities.CATALOG,
            TapCapabilities.PROPERTIES,
        ]

        for cap in required_caps:
            assert cap in capabilities, f"Missing capability: {cap}"

        return True

    except Exception:
        return False


def test_modern_config_schema() -> bool:
    """Test the modern configuration schema patterns."""
    try:
        from tap_oracle_wms.config import config_schema

        # Ensure config_schema exists
        assert config_schema is not None

        # Convert to dict to check structure
        schema_dict = config_schema if isinstance(config_schema, dict) else config_schema.to_dict()
        assert isinstance(schema_dict, dict)

        # Check for required properties
        properties = schema_dict.get("properties", {})
        required_props = ["base_url"]

        for prop in required_props:
            assert prop in properties, f"Missing required property: {prop}"

        # Check for modern JSON Schema features
        base_url_prop = properties.get("base_url", {})
        if "pattern" in base_url_prop:
            pass
        if "examples" in base_url_prop:
            pass

        return True

    except Exception:
        return False


def test_modern_stream_implementation() -> bool:
    """Test the modern stream implementation."""
    try:
        from singer_sdk.streams import RESTStream

        from tap_oracle_wms.streams import WMSAdvancedStream

        # Check inheritance
        assert issubclass(WMSAdvancedStream, RESTStream)

        # Check for required modern methods
        required_methods = [
            "get_new_paginator",
            "get_url_params",
            "parse_response",
            "validate_response",
        ]

        for method in required_methods:
            assert hasattr(WMSAdvancedStream, method)

        return True

    except Exception:
        return False


def validate_pyproject_toml() -> bool:
    """Validate the modern pyproject.toml configuration."""
    try:
        import tomllib

        with open("pyproject.toml", "rb") as f:
            pyproject = tomllib.load(f)

        # Check build system
        build_system = pyproject.get("build-system", {})
        assert "hatchling" in str(build_system.get("requires", []))

        # Check project section
        project = pyproject.get("project", {})
        assert project.get("name") == "tap-oracle-wms"

        # Check dependencies
        dependencies = project.get("dependencies", [])
        has_modern_sdk = any("singer-sdk[" in dep for dep in dependencies)
        assert has_modern_sdk, "Modern Singer SDK with extras not found"

        # Check entry points
        entry_points = project.get("entry-points", {})
        assert "console_scripts" in entry_points
        assert "singer_sdk.taps" in entry_points

        # Check tool configuration
        tool_section = pyproject.get("tool", {})
        assert "hatch" in tool_section

        return True

    except Exception:
        return False


def main() -> None:
    """Run all validation tests."""
    tests = [
        test_modern_imports,
        test_modern_paginator,
        test_modern_capabilities,
        test_modern_config_schema,
        test_modern_stream_implementation,
        validate_pyproject_toml,
    ]

    passed = 0
    total = len(tests)

    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception:
            pass

    if passed == total:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
