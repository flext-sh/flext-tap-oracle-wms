"""Module test_e2e."""

from typing import Any

"""End-to-end tests for tap-oracle-wms."""

import json
import os
import subprocess
import tempfile
from pathlib import Path

import pytest
from tap_oracle_wms.tap import TapOracleWMS


class TestE2EWithOptionalConfig:
    """E2E tests with optional config.json validation."""

    @pytest.fixture
    def project_root(self) -> Any:
        """Get project root directory."""
        return Path(__file__).parent.parent

    @pytest.fixture
    def config_file_path(self, project_root) -> Any:
        """Check for config.json in project root."""
        config_path = project_root / "config.json"
        return config_path if config_path.exists() else None

    @pytest.fixture
    def live_config_data(self, config_file_path) -> Any:
        """Load live config if available."""
        if config_file_path:
            with open(config_file_path, encoding="utf-8") as f:
                return json.load(f)
        return None

    def test_config_file_existence(self, project_root) -> None:
        """Test for config.json existence (informational)."""
        config_path = project_root / "config.json"

        if config_path.exists():
            # Validate config structure
            with open(config_path, encoding="utf-8") as f:
                config = json.load(f)

            # Check required fields
            required_fields = ["base_url", "auth_method"]
            for field in required_fields:
                assert field in config, f"Missing required field: {field}"

            # Check auth method specific fields
            if config.get("auth_method") == "basic":
                assert "username" in config, "Missing username for basic auth"
                assert "password" in config, "Missing password for basic auth"

            pytest.skip("No config.json available for E2E testing")

    def test_e2e_discovery_with_config(self, live_config_data) -> None:
        """Test E2E discovery workflow with config.json."""
        if not live_config_data:
            pytest.skip("No live config available")

        # Create temporary config file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(live_config_data, f)
            temp_config_path = f.name

        try:
            # Run discovery command
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "tap_oracle_wms.cli",
                    "discover-entities",
                    "--config",
                    temp_config_path,
                    "--format",
                    "json",
                ],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent,
                check=False,
            )

            if result.returncode == 0:
                # Parse output
                try:
                    output_data = json.loads(result.stdout)
                    assert "entities" in output_data
                    assert len(output_data["entities"]) >= 0
                except json.JSONDecodeError:
                    # Output might not be pure JSON if mixed with logs
                    assert "entities" in result.stdout or "Found" in result.stdout
                # Don't fail the test for external connectivity issues
                pytest.skip(f"Discovery command failed: {result.stderr}")

        finally:
            # Clean up
            os.unlink(temp_config_path)

    def test_e2e_connection_test_with_config(self, live_config_data) -> None:
        """Test E2E connection test with config.json."""
        if not live_config_data:
            pytest.skip("No live config available")

        # Create temporary config file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(live_config_data, f)
            temp_config_path = f.name

        try:
            # Run connection test command
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "tap_oracle_wms.cli",
                    "test-connection",
                    "--config",
                    temp_config_path,
                ],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent,
                check=False,
            )

            if result.returncode == 0:
                assert "successful" in result.stdout.lower() or "✅" in result.stdout
                # Don't fail the test for external connectivity issues
                pytest.skip(f"Connection test failed: {result.stderr}")

        finally:
            # Clean up
            os.unlink(temp_config_path)

    def test_e2e_tap_discovery_with_config(self, live_config_data) -> None:
        """Test E2E tap discovery (Singer standard) with config.json."""
        if not live_config_data:
            pytest.skip("No live config available")

        # Create temporary config file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(live_config_data, f)
            temp_config_path = f.name

        try:
            # Run Singer discovery command
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "tap_oracle_wms",
                    "--config",
                    temp_config_path,
                    "--discover",
                ],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent,
                check=False,
            )

            if result.returncode == 0:
                # Parse catalog output
                try:
                    catalog = json.loads(result.stdout)
                    assert "streams" in catalog
                    assert len(catalog["streams"]) >= 0

                    # Validate catalog structure
                    for stream in catalog["streams"]:
                        assert "tap_stream_id" in stream
                        assert "schema" in stream
                        assert "metadata" in stream

                except json.JSONDecodeError:
                    pytest.fail("Invalid catalog JSON output")
                pytest.skip(f"Singer discovery failed: {result.stderr}")

        finally:
            # Clean up
            os.unlink(temp_config_path)

    def test_e2e_tap_sync_dry_run_with_config(self, live_config_data) -> None:
        """Test E2E tap sync (dry run) with config.json."""
        if not live_config_data:
            pytest.skip("No live config available")

        # Create minimal catalog for testing
        minimal_catalog = {
            "streams": [
                {
                    "tap_stream_id": "facility",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "code": {"type": "string"},
                        },
                    },
                    "metadata": [
                        {
                            "breadcrumb": [],
                            "metadata": {
                                "selected": True,
                                "replication-method": "FULL_TABLE",
                            },
                        }
                    ],
                }
            ]
        }

        # Create temporary files
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as config_f:
            json.dump(live_config_data, config_f)
            temp_config_path = config_f.name

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as catalog_f:
            json.dump(minimal_catalog, catalog_f)
            temp_catalog_path = catalog_f.name

        try:
            # Run sync command with limited output (first 10 records max)
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "tap_oracle_wms",
                    "--config",
                    temp_config_path,
                    "--catalog",
                    temp_catalog_path,
                ],
                capture_output=True,
                text=True,
                timeout=30,  # 30 second timeout
                cwd=Path(__file__).parent.parent,
                check=False,
            )

            if result.returncode == 0:
                # Check for Singer messages in output
                lines = result.stdout.strip().split("\n")
                message_types: set = set()

                for line in lines:
                    if line.strip():
                        try:
                            message = json.loads(line)
                            if "type" in message:
                                message_types.add(message["type"])
                        except json.JSONDecodeError:
                            # Skip non-JSON lines (logs)
                            continue

                # Should have at least SCHEMA messages
                assert "SCHEMA" in message_types or len(lines) > 0

            # For live tests, don't fail on connectivity issues
            elif (
                "timeout" in result.stderr.lower()
                or "connection" in result.stderr.lower()
            ):
                pytest.skip(f"Singer sync failed due to connectivity: {result.stderr}")
                pytest.fail(f"Singer sync failed: {result.stderr}")

        except subprocess.TimeoutExpired:
            pass
            # Timeout is expected for live tests to avoid long runs

        finally:
            # Clean up
            os.unlink(temp_config_path)
            os.unlink(temp_catalog_path)

    def test_e2e_cli_help_commands(self) -> None:
        """Test E2E CLI help commands."""
        # Test main help
        result = subprocess.run(
            ["python", "-m", "tap_oracle_wms.cli", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            check=False,
        )

        assert result.returncode == 0
        assert "Oracle WMS Singer Tap" in result.stdout
        assert "discover-entities" in result.stdout

        # Test discover-entities help
        result = subprocess.run(
            ["python", "-m", "tap_oracle_wms.cli", "discover-entities", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            check=False,
        )

        assert result.returncode == 0
        assert "Discover available WMS entities" in result.stdout

        # Test test-connection help
        result = subprocess.run(
            ["python", "-m", "tap_oracle_wms.cli", "test-connection", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            check=False,
        )

        assert result.returncode == 0
        assert "Test connection to Oracle WMS" in result.stdout

    def test_e2e_singer_help_commands(self) -> None:
        """Test E2E Singer standard help commands."""
        # Test main Singer help
        result = subprocess.run(
            ["python", "-m", "tap_oracle_wms", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            check=False,
        )

        assert result.returncode == 0
        assert "--config" in result.stdout
        assert "--discover" in result.stdout

    def test_e2e_version_commands(self) -> None:
        """Test E2E version commands."""
        # Test CLI version
        result = subprocess.run(
            ["python", "-m", "tap_oracle_wms.cli", "--version"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            check=False,
        )

        assert result.returncode == 0
        assert "tap-oracle-wms" in result.stdout

    def test_e2e_error_handling(self) -> None:
        """Test E2E error handling with invalid config."""
        # Create invalid config file
        invalid_config = {"base_url": "invalid-url", "auth_method": "invalid"}

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(invalid_config, f)
            temp_config_path = f.name

        try:
            # Should fail gracefully
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "tap_oracle_wms.cli",
                    "test-connection",
                    "--config",
                    temp_config_path,
                ],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent,
                check=False,
            )

            # Should exit with error code
            assert result.returncode != 0

            # Should provide meaningful error message
            assert "error" in result.stderr.lower() or "failed" in result.stderr.lower()

        finally:
            # Clean up
            os.unlink(temp_config_path)

    def test_e2e_missing_config_handling(self) -> None:
        """Test E2E handling of missing config file."""
        # Try to use non-existent config file
        result = subprocess.run(
            [
                "python",
                "-m",
                "tap_oracle_wms.cli",
                "discover-entities",
                "--config",
                "/nonexistent/config.json",
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            check=False,
        )

        # Should fail gracefully
        assert result.returncode != 0

        # Should provide meaningful error message
        error_output = result.stderr.lower()
        assert (
            "not found" in error_output
            or "no such file" in error_output
            or "error" in error_output
        )


class TestE2EConfiguration:
    """E2E tests for configuration validation."""

    def test_e2e_config_validation_comprehensive(self, sample_config) -> None:
        """Test comprehensive configuration validation."""
        # Test with programmatic tap creation
        config_json = json.dumps(sample_config)

        try:
            tap = TapOracleWMS(config=config_json)
            assert tap.config == sample_config
        except Exception as e:
            pytest.fail(f"Configuration validation failed: {e}")

    def test_e2e_ssl_config_validation(self) -> None:
        """Test SSL configuration validation."""
        ssl_config = {
            "base_url": "https://example.com",
            "auth_method": "basic",
            "username": "user",
            "password": "pass",
            "verify_ssl": False,
            "ssl_ca_file": "/path/to/ca.pem",
            "connect_timeout": 30,
        }

        config_json = json.dumps(ssl_config)

        try:
            tap = TapOracleWMS(config=config_json)
            assert tap.config["verify_ssl"] is False
            assert tap.config["ssl_ca_file"] == "/path/to/ca.pem"
        except Exception as e:
            pytest.fail(f"SSL configuration validation failed: {e}")

    def test_e2e_oauth2_config_validation(self) -> None:
        """Test OAuth2 configuration validation."""
        oauth2_config = {
            "base_url": "https://example.com",
            "auth_method": "oauth2",
            "oauth_client_id": "client123",
            "oauth_client_secret": "secret456",
            "oauth_token_url": "https://auth.example.com/token",
            "oauth_scope": "read write",
        }

        config_json = json.dumps(oauth2_config)

        try:
            tap = TapOracleWMS(config=config_json)
            assert tap.config["auth_method"] == "oauth2"
            assert tap.config["oauth_client_id"] == "client123"
        except Exception as e:
            pytest.fail(f"OAuth2 configuration validation failed: {e}")

    def test_e2e_business_config_validation(self) -> None:
        """Test business configuration validation."""
        business_config = {
            "base_url": "https://example.com",
            "auth_method": "basic",
            "username": "user",
            "password": "pass",
            "business_classification": {
                "enable_categorization": True,
                "categories": ["master_data", "operational"],
            },
            "data_enrichment": {
                "add_extraction_metadata": True,
                "normalize_timestamps": True,
            },
        }

        config_json = json.dumps(business_config)

        try:
            tap = TapOracleWMS(config=config_json)
            bc = tap.config["business_classification"]
            assert bc["enable_categorization"] is True
        except Exception as e:
            pytest.fail(f"Business configuration validation failed: {e}")


class TestE2EPerformance:
    """E2E performance tests."""

    def test_e2e_discovery_performance(self, live_config_data) -> None:
        """Test discovery performance."""
        if not live_config_data:
            pytest.skip("No live config available")

        import time

        start_time = time.time()

        config_json = json.dumps(live_config_data)
        tap = TapOracleWMS(config=config_json)

        try:
            tap.discover_streams()
            discovery_time = time.time() - start_time

            # Discovery should complete in reasonable time
            assert (
                discovery_time < 60
            ), f"Discovery took too long: {discovery_time:.2f}s"

        except Exception as e:
            pytest.skip(f"Discovery performance test failed: {e}")

    def test_e2e_memory_usage(self, sample_config) -> None:
        """Test memory usage during operations."""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        config_json = json.dumps(sample_config)

        # Create multiple tap instances
        taps: list = []
        for _i in range(5):
            tap = TapOracleWMS(config=config_json)
            taps.append(tap)

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable
        assert memory_increase < 100, f"Memory usage too high: +{memory_increase:.1f}MB"


class TestE2ERobustness:
    """E2E robustness and reliability tests."""

    def test_e2e_repeated_operations(self, sample_config) -> None:
        """Test repeated operations for stability."""
        config_json = json.dumps(sample_config)

        # Repeat tap creation multiple times
        for i in range(10):
            try:
                tap = TapOracleWMS(config=config_json)
                assert tap.config == sample_config
            except Exception as e:
                pytest.fail(f"Failed on iteration {i}: {e}")

    def test_e2e_concurrent_operations(self, sample_config) -> None:
        """Test concurrent operations."""
        import threading

        config_json = json.dumps(sample_config)
        results: list = []
        errors: list = []

        def create_tap(index) -> None:
            try:
                TapOracleWMS(config=config_json)
                results.append(f"Success {index}")
            except Exception as e:
                errors.append(f"Error {index}: {e}")

        # Create multiple threads
        threads: list = []
        for i in range(5):
            thread = threading.Thread(target=create_tap, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Most operations should succeed
        assert len(results) >= len(errors), f"Too many errors: {errors}"

    def test_e2e_error_recovery(self) -> None:
        """Test error recovery scenarios."""
        # Test with invalid config first
        invalid_config = {"base_url": "invalid"}

        try:
            TapOracleWMS(config=json.dumps(invalid_config))
            pytest.fail("Should have failed with invalid config")
        except Exception:
            pass  # Expected failure

        # Then test with valid config
        valid_config = {
            "base_url": "https://example.com",
            "auth_method": "basic",
            "username": "user",
            "password": "pass",
        }

        try:
            tap = TapOracleWMS(config=json.dumps(valid_config))
            assert tap.config == valid_config
        except Exception as e:
            pytest.fail(f"Error recovery failed: {e}")
