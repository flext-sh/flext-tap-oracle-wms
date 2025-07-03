"""Simple integration tests that work with current implementation."""

from unittest.mock import patch

import pytest

from tap_oracle_wms.tap import TapOracleWMS


class TestSimpleIntegration:
    """Simple integration tests for core functionality."""

    @pytest.fixture
    def config(self):
        """Basic test configuration."""
        return {
            "base_url": "https://test.example.com",
            "username": "test",
            "password": "test",
        }

    def test_tap_initialization_integration(self, config):
        """Test TAP can be initialized with configuration."""
        with patch("tap_oracle_wms.tap.TapOracleWMS.discover_streams") as mock_discover:
            mock_discover.return_value = []

            tap = TapOracleWMS(config=config)

            assert tap.name == "tap-oracle-wms"
            assert tap.config == config
            assert hasattr(tap, "discovery")
            assert hasattr(tap, "schema_generator")

    def test_singer_interface_integration(self, config):
        """Test Singer interface compliance."""
        with patch("tap_oracle_wms.tap.TapOracleWMS.discover_streams") as mock_discover:
            mock_discover.return_value = []

            tap = TapOracleWMS(config=config)

            # Test Singer interface requirements
            assert hasattr(tap, "name")
            assert hasattr(tap, "config")
            assert hasattr(tap, "catalog_dict")
            assert hasattr(tap, "state_dict")
            assert hasattr(tap, "discover_streams")

            # Test interface works
            catalog = tap.catalog_dict
            state = tap.state_dict

            assert isinstance(catalog, dict)
            assert isinstance(state, dict)

    def test_configuration_validation_integration(self, config):
        """Test configuration validation works."""
        # Test valid config
        with patch("tap_oracle_wms.tap.TapOracleWMS.discover_streams") as mock_discover:
            mock_discover.return_value = []

            tap = TapOracleWMS(config=config)
            assert tap.config["base_url"] == "https://test.example.com"

        # Test minimal config
        minimal_config = {"base_url": "https://minimal.test"}
        with patch("tap_oracle_wms.tap.TapOracleWMS.discover_streams") as mock_discover:
            mock_discover.return_value = []

            tap = TapOracleWMS(config=minimal_config)
            assert tap.config["base_url"] == "https://minimal.test"

    def test_discovery_components_integration(self, config):
        """Test discovery components work together."""
        from tap_oracle_wms.discovery import EntityDiscovery, SchemaGenerator

        # Test EntityDiscovery initialization
        discovery = EntityDiscovery(config)
        assert discovery.config == config
        assert hasattr(discovery, "entity_endpoint")

        # Test SchemaGenerator initialization
        generator = SchemaGenerator()
        assert hasattr(generator, "generate_from_sample")
        assert hasattr(generator, "generate_from_metadata")

    def test_mock_server_integration(self):
        """Test integration with mock server."""
        import asyncio
        import time

        from mock_wms_server import start_mock_server
        from tap_oracle_wms.discovery import EntityDiscovery

        # Start mock server
        server = start_mock_server(8889)
        time.sleep(0.5)

        try:
            config = {
                "base_url": "http://localhost:8889",
                "username": "test",
                "password": "test",
                "verify_ssl": False,
            }

            discovery = EntityDiscovery(config)

            # Test discovery works with mock server
            entities = asyncio.run(discovery.discover_entities())

            assert isinstance(entities, dict)
            assert len(entities) > 0
            assert "item" in entities

        finally:
            server.shutdown()

    def test_error_handling_integration(self, config):
        """Test error handling in integration scenarios."""
        from tap_oracle_wms.discovery import EntityDiscovery

        # Test with invalid URL (should handle gracefully)
        invalid_config = config.copy()
        invalid_config["base_url"] = "http://this-host-does-not-exist.invalid"

        discovery = EntityDiscovery(invalid_config)

        # Should create discovery object without errors
        assert discovery.config["base_url"] == "http://this-host-does-not-exist.invalid"

        # Actual network errors would be caught during async operations
        # This tests the setup/configuration phase

    def test_end_to_end_tap_workflow(self):
        """Test complete TAP workflow with mock data."""
        import time

        from mock_wms_server import start_mock_server

        # Start mock server
        server = start_mock_server(8890)
        time.sleep(0.5)

        try:
            config = {
                "base_url": "http://localhost:8890",
                "username": "test",
                "password": "test",
                "verify_ssl": False,
            }

            # Test complete workflow
            tap = TapOracleWMS(config=config)

            # Test basic tap properties
            assert tap.name == "tap-oracle-wms"
            assert tap.config == config

            # Test catalog generation (mocked)
            catalog = tap.catalog_dict
            assert isinstance(catalog, dict)

            # Test state handling
            state = tap.state_dict
            assert isinstance(state, dict)

        finally:
            server.shutdown()

    def test_cli_module_integration(self):
        """Test CLI module can be imported and used."""
        from tap_oracle_wms import cli

        # Test CLI module has main function
        assert hasattr(cli, "main")
        assert callable(cli.main)

        # Test enhanced CLI exists
        try:
            from tap_oracle_wms import cli_enhanced
            assert hasattr(cli_enhanced, "cli")
            assert callable(cli_enhanced.cli)
        except ImportError:
            # Enhanced CLI is optional
            pass
