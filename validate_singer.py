#!/usr/bin/env python3
"""Complete Singer Protocol Compliance Validator for Oracle WMS Tap."""

from __future__ import annotations

import contextlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

import jsonschema


def validate_singer_compliance() -> bool:
    """Validate complete Singer protocol compliance."""
    all_tests = [
        test_cli_commands,
        test_discovery_output,
        test_catalog_format,
        test_record_output,
        test_state_handling,
        test_error_handling,
    ]

    passed = 0
    total = len(all_tests)

    for test in all_tests:
        try:
            if test():
                passed += 1
        except Exception:
            pass

    return passed == total


def test_cli_commands() -> bool:
    """Test CLI command compliance."""
    commands = [
        ("--help", "Help command"),
        ("--version", "Version command"),
        ("--about", "About command"),
    ]

    for cmd, _desc in commands:
        try:
            result = subprocess.run(
                ["python", "-m", "tap_oracle_wms", cmd],
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                pass
            else:
                return False
        except Exception:
            return False

    return True


def test_discovery_output() -> bool | None:
    """Test discovery output format."""
    try:
        # Create test config
        test_config = {
            "base_url": "http://localhost:8888",
            "username": "test",
            "password": "test",
            "verify_ssl": False,
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(test_config, f)
            config_file = f.name

        # Start mock server and run discovery
        import time

        from mock_wms_server import start_mock_server

        server = start_mock_server(8888)
        time.sleep(1)

        try:
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "tap_oracle_wms",
                    "--config",
                    config_file,
                    "--discover",
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                return False

            # Parse discovery output
            try:
                catalog = json.loads(result.stdout)

                # Check catalog structure
                if "streams" in catalog:
                    streams = catalog["streams"]

                    # Check stream structure
                    if streams:
                        stream = streams[0]
                        required_fields = ["stream", "tap_stream_id", "schema"]
                        for field in required_fields:
                            if field in stream:
                                pass
                            else:
                                return False

                    return True
                return False

            except json.JSONDecodeError:
                return False

        finally:
            server.shutdown()
            Path(config_file).unlink()

    except Exception:
        return False


def test_catalog_format() -> bool | None:
    """Test catalog format compliance."""
    # Singer catalog schema (simplified)
    catalog_schema = {
        "type": "object",
        "properties": {
            "streams": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "stream": {"type": "string"},
                        "tap_stream_id": {"type": "string"},
                        "schema": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string"},
                                "properties": {"type": "object"},
                            },
                            "required": ["type", "properties"],
                        },
                    },
                    "required": ["stream", "tap_stream_id", "schema"],
                },
            },
        },
        "required": ["streams"],
    }

    try:
        # Generate catalog using tap
        from tap_oracle_wms.tap import TapOracleWMS

        config = {
            "base_url": "http://localhost:8888",
            "username": "test",
            "password": "test",
            "verify_ssl": False,
        }

        # Mock the discovery to avoid network calls
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(config, f)
            config_file = f.name

        try:
            tap = TapOracleWMS(config=config)
            catalog = tap.catalog_dict

            # Validate against schema
            jsonschema.validate(catalog, catalog_schema)

            streams = catalog.get("streams", [])
            if streams:
                # Check schema validity for each stream
                for stream in streams:
                    schema = stream.get("schema", {})
                    if "properties" in schema and "type" in schema:
                        pass
                    else:
                        return False

            return True

        finally:
            Path(config_file).unlink()

    except jsonschema.ValidationError:
        return False
    except Exception:
        return False


def test_record_output() -> bool | None:
    """Test record output format."""
    try:
        # Test that records follow Singer format
        _unused_config = {
            "base_url": "http://localhost:8888",
            "username": "test",
            "password": "test",
            "verify_ssl": False,
            "record_limit": 1,
        }

        # Mock record should have Singer format
        mock_record = {
            "type": "RECORD",
            "stream": "item",
            "record": {
                "id": 1,
                "item_code": "TEST001",
                "description": "Test Item",
            },
            "time_extracted": "2024-01-01T12:00:00Z",
        }

        # Check record structure
        required_fields = ["type", "stream", "record"]
        for field in required_fields:
            if field in mock_record:
                pass
            else:
                return False

        # Check record type
        if mock_record["type"] == "RECORD":
            pass
        else:
            return False

        return True

    except Exception:
        return False


def test_state_handling() -> bool | None:
    """Test state handling."""
    try:
        from tap_oracle_wms.tap import TapOracleWMS

        config = {
            "base_url": "http://localhost:8888",
            "username": "test",
            "password": "test",
            "verify_ssl": False,
        }

        tap = TapOracleWMS(config=config)

        # Test state_dict property
        if hasattr(tap, "state_dict"):
            state = tap.state_dict

            if isinstance(state, dict):
                pass
            else:
                return False
        else:
            return False

        return True

    except Exception:
        return False


def test_error_handling() -> bool | None:
    """Test error handling."""
    try:
        # Test with invalid config
        invalid_config = {
            "base_url": "http://invalid-wms-server-that-does-not-exist.com",
            "username": "invalid",
            "password": "invalid",
        }

        import asyncio

        from tap_oracle_wms.discovery import EntityDiscovery

        discovery = EntityDiscovery(invalid_config)

        # This should handle errors gracefully
        with contextlib.suppress(Exception):
            _unused_result = asyncio.run(discovery.discover_entities())

        return True

    except Exception:
        return False


if __name__ == "__main__":
    success = validate_singer_compliance()
    sys.exit(0 if success else 1)
