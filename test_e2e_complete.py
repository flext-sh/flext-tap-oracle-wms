#!/usr/bin/env python3
"""Comprehensive End-to-End Testing for tap-oracle-wms.

This script performs complete E2E testing using .env configuration:
- Configuration generation from .env
- Discovery functionality testing
- Data extraction testing
- CLI functionality testing
- Error handling validation
- Performance testing
"""

from datetime import UTC, datetime
import json
import logging
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback
from typing import Any


# Load .env file manually
def load_env_file(env_path: Path = Path(".env")) -> None:
    """Load environment variables from .env file."""
    if not env_path.exists():
        return

    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()


# Load .env immediately
load_env_file()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)8s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class E2ETestRunner:
    """Complete End-to-End test runner for tap-oracle-wms."""

    def __init__(self) -> None:
        """Initialize E2E test runner."""
        self.test_results: list[dict[str, Any]] = []
        self.config_file = Path("config_e2e.json")
        self.catalog_file = Path("catalog_e2e.json")
        self.state_file = Path("state_e2e.json")
        self.test_data_dir = Path("e2e_test_data")
        self.test_data_dir.mkdir(exist_ok=True)

    def load_env_config(self) -> dict[str, Any]:
        """Generate tap configuration from .env variables."""
        logger.info("🔧 Generating configuration from .env variables")

        # Read environment variables
        config = {
            "base_url": os.getenv("WMS_BASE_URL", "").rstrip("/"),
            "auth_method": "basic",
            "username": os.getenv("WMS_USERNAME", ""),
            "password": os.getenv("WMS_PASSWORD", ""),
            "api_version": os.getenv("WMS_API_VERSION", "v10"),
            "start_date": os.getenv("WMS_START_DATE", "2024-01-01T00:00:00Z"),
            "test_mode": os.getenv("WMS_TEST_MODE", "false").lower() == "true",
            # Connection settings
            "request_timeout": int(os.getenv("HTTP_TIMEOUT", "600")),
            "max_retries": int(os.getenv("HTTP_MAX_RETRIES", "1")),
            "retry_delay": int(os.getenv("HTTP_RETRY_DELAY", "2")),
            "verify_ssl": os.getenv("HTTP_VERIFY_SSL", "true").lower() == "true",
            # Business settings for testing
            "page_size": 100,
            "pagination_mode": "offset",
            "company_code": "DEMO",
            "facility_code": "DC01",
            # Testing configuration
            "entities": ["allocation"],  # Start with known entity
            "debug_mode": True,
            "stream_maps": {},
            "stream_map_config": {},
        }

        # Validate required configuration
        required_fields = ["base_url", "username", "password"]
        missing_fields = [field for field in required_fields if not config.get(field)]

        if missing_fields:
            msg = f"Missing required configuration: {missing_fields}"
            raise ValueError(msg)

        logger.info(f"✅ Configuration generated with base URL: {config['base_url']}")
        return config

    def save_config(self, config: dict[str, Any]) -> None:
        """Save configuration to file."""
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        logger.info(f"📝 Configuration saved to {self.config_file}")

    def run_command(self, cmd: list[str], timeout: int = 120) -> dict[str, Any]:
        """Run command and capture output."""
        logger.info(f"🔧 Running command: {' '.join(cmd)}")
        start_time = time.time()

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=Path.cwd(),
                check=False,
            )

            elapsed_time = time.time() - start_time

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "elapsed_time": elapsed_time,
                "command": " ".join(cmd),
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds",
                "elapsed_time": timeout,
                "command": " ".join(cmd),
            }
        except Exception as e:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "elapsed_time": time.time() - start_time,
                "command": " ".join(cmd),
            }

    def test_basic_import(self) -> dict[str, Any]:
        """Test basic Python import functionality."""
        logger.info("🧪 Testing basic Python import")

        try:
            cmd = [
                sys.executable,
                "-c",
                "from tap_oracle_wms import TapOracleWMS; print('✅ Import successful')",
            ]
            result = self.run_command(cmd, timeout=30)

            test_result = {
                "test_name": "basic_import",
                "success": result["success"]
                and "Import successful" in result["stdout"],
                "duration": result["elapsed_time"],
                "details": {
                    "stdout": result["stdout"],
                    "stderr": result["stderr"],
                },
            }

            if test_result["success"]:
                logger.info("✅ Basic import test passed")
            else:
                logger.error(f"❌ Basic import test failed: {result['stderr']}")

            return test_result

        except Exception as e:
            logger.exception("❌ Basic import test error")
            return {
                "test_name": "basic_import",
                "success": False,
                "duration": 0,
                "details": {"error": str(e)},
            }

    def test_cli_help(self) -> dict[str, Any]:
        """Test CLI help functionality."""
        logger.info("🧪 Testing CLI help commands")

        try:
            cmd = [sys.executable, "-m", "tap_oracle_wms", "--help"]
            result = self.run_command(cmd, timeout=30)

            test_result = {
                "test_name": "cli_help",
                "success": result["success"]
                and "Oracle WMS Singer Tap" in result["stdout"],
                "duration": result["elapsed_time"],
                "details": {
                    "stdout": result["stdout"],
                    "stderr": result["stderr"],
                },
            }

            if test_result["success"]:
                logger.info("✅ CLI help test passed")
            else:
                logger.error("❌ CLI help test failed")

            return test_result

        except Exception as e:
            logger.exception("❌ CLI help test error")
            return {
                "test_name": "cli_help",
                "success": False,
                "duration": 0,
                "details": {"error": str(e)},
            }

    def test_discovery(self) -> dict[str, Any]:
        """Test discovery functionality."""
        logger.info("🧪 Testing discovery functionality")

        try:
            cmd = [
                sys.executable,
                "-m",
                "tap_oracle_wms",
                "--config",
                str(self.config_file),
                "--discover",
            ]
            result = self.run_command(cmd, timeout=180)

            catalog_data = None
            if result["success"] and result["stdout"]:
                try:
                    # Parse catalog output
                    catalog_data = json.loads(result["stdout"])

                    # Save catalog for later use
                    with open(self.catalog_file, "w", encoding="utf-8") as f:
                        json.dump(catalog_data, f, indent=2)

                except json.JSONDecodeError as e:
                    logger.warning(f"Could not parse catalog JSON: {e}")

            test_result = {
                "test_name": "discovery",
                "success": result["success"] and catalog_data is not None,
                "duration": result["elapsed_time"],
                "details": {
                    "streams_discovered": len(catalog_data.get("streams", []))
                    if catalog_data
                    else 0,
                    "catalog_saved": self.catalog_file.exists(),
                    "stdout_length": len(result["stdout"]),
                    "stderr": result["stderr"],
                },
            }

            if test_result["success"]:
                logger.info(
                    f"✅ Discovery test passed - \
                        found {test_result['details']['streams_discovered']} streams"
                )
            else:
                logger.error(f"❌ Discovery test failed: {result['stderr']}")

            return test_result

        except Exception as e:
            logger.exception("❌ Discovery test error")
            return {
                "test_name": "discovery",
                "success": False,
                "duration": 0,
                "details": {"error": str(e)},
            }

    def test_data_extraction(self) -> dict[str, Any]:
        """Test data extraction functionality."""
        logger.info("🧪 Testing data extraction")

        if not self.catalog_file.exists():
            return {
                "test_name": "data_extraction",
                "success": False,
                "duration": 0,
                "details": {"error": "No catalog file available for extraction test"},
            }

        try:
            # Limit extraction for testing
            output_file = self.test_data_dir / "extracted_data.jsonl"

            cmd = [
                sys.executable,
                "-m",
                "tap_oracle_wms",
                "--config",
                str(self.config_file),
                "--catalog",
                str(self.catalog_file),
            ]

            result = self.run_command(cmd, timeout=300)

            # Save output for analysis
            if result["stdout"]:
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(result["stdout"])

            # Analyze extraction results
            records_count = 0
            if result["stdout"]:
                lines = result["stdout"].strip().split("\n")
                for line in lines:
                    try:
                        data = json.loads(line)
                        if data.get("type") == "RECORD":
                            records_count += 1
                    except json.JSONDecodeError:
                        continue

            test_result = {
                "test_name": "data_extraction",
                "success": result["success"] and records_count > 0,
                "duration": result["elapsed_time"],
                "details": {
                    "records_extracted": records_count,
                    "output_file": str(output_file),
                    "output_size": len(result["stdout"]),
                    "stderr": result["stderr"],
                },
            }

            if test_result["success"]:
                logger.info(
                    f"✅ Data extraction test passed - extracted {records_count} records"
                )
            else:
                logger.error(f"❌ Data extraction test failed: {result['stderr']}")

            return test_result

        except Exception as e:
            logger.exception("❌ Data extraction test error")
            return {
                "test_name": "data_extraction",
                "success": False,
                "duration": 0,
                "details": {"error": str(e)},
            }

    def test_cli_subcommands(self) -> dict[str, Any]:
        """Test CLI subcommands functionality."""
        logger.info("🧪 Testing CLI subcommands")

        subcommands_to_test = [
            ["discover", "entities", "--config", str(self.config_file)],
            ["monitor", "health", "--config", str(self.config_file)],
            ["sync", "test-connection", "--config", str(self.config_file)],
        ]

        subcommand_results = []
        overall_success = True
        total_duration = 0

        for subcommand in subcommands_to_test:
            try:
                cmd = [sys.executable, "-m", "tap_oracle_wms", *subcommand]
                result = self.run_command(cmd, timeout=120)

                subcommand_results.append(
                    {
                        "subcommand": " ".join(subcommand),
                        "success": result["success"],
                        "duration": result["elapsed_time"],
                        "stdout": result["stdout"][:200] + "..."
                        if len(result["stdout"]) > 200
                        else result["stdout"],
                        "stderr": result["stderr"][:200] + "..."
                        if len(result["stderr"]) > 200
                        else result["stderr"],
                    }
                )

                total_duration += result["elapsed_time"]
                if not result["success"]:
                    overall_success = False

            except Exception as e:
                subcommand_results.append(
                    {
                        "subcommand": " ".join(subcommand),
                        "success": False,
                        "duration": 0,
                        "error": str(e),
                    }
                )
                overall_success = False

        test_result = {
            "test_name": "cli_subcommands",
            "success": overall_success,
            "duration": total_duration,
            "details": {
                "subcommands_tested": len(subcommands_to_test),
                "subcommands_passed": sum(
                    1 for r in subcommand_results if r["success"]
                ),
                "results": subcommand_results,
            },
        }

        if test_result["success"]:
            logger.info(
                f"✅ CLI subcommands test passed - \
                    {test_result['details']['subcommands_passed']}/{test_result['details']['subcommands_tested']} passed"
            )
        else:
            logger.error(
                f"❌ CLI subcommands test failed - \
                    {test_result['details']['subcommands_passed']}/{test_result['details']['subcommands_tested']} passed"
            )

        return test_result

    def test_error_handling(self) -> dict[str, Any]:
        """Test error handling with invalid configurations."""
        logger.info("🧪 Testing error handling")

        # Create invalid config
        invalid_config = {
            "base_url": "https://invalid-url-for-testing.com",
            "auth_method": "basic",
            "username": "invalid_user",
            "password": "invalid_password",
        }

        invalid_config_file = Path("config_invalid.json")
        with open(invalid_config_file, "w", encoding="utf-8") as f:
            json.dump(invalid_config, f, indent=2)

        try:
            cmd = [
                sys.executable,
                "-m",
                "tap_oracle_wms",
                "--config",
                str(invalid_config_file),
                "--discover",
            ]
            result = self.run_command(cmd, timeout=60)

            # For error handling test, we expect failure
            expected_failure = not result["success"]

            test_result = {
                "test_name": "error_handling",
                "success": expected_failure,
                "duration": result["elapsed_time"],
                "details": {
                    "expected_failure": True,
                    "actual_failure": not result["success"],
                    "stderr": result["stderr"],
                },
            }

            if test_result["success"]:
                logger.info(
                    "✅ Error handling test passed - properly handled invalid config"
                )
            else:
                logger.error(
                    "❌ Error handling test failed - \
                        should have failed with invalid config"
                )

            return test_result

        except Exception as e:
            logger.exception("❌ Error handling test error")
            return {
                "test_name": "error_handling",
                "success": False,
                "duration": 0,
                "details": {"error": str(e)},
            }
        finally:
            # Cleanup
            if invalid_config_file.exists():
                invalid_config_file.unlink()

    def run_all_tests(self) -> dict[str, Any]:
        """Run all E2E tests."""
        logger.info("🚀 Starting comprehensive E2E testing for tap-oracle-wms")
        start_time = time.time()

        # Generate and save configuration
        try:
            config = self.load_env_config()
            self.save_config(config)
        except Exception as e:
            logger.exception(f"❌ Failed to generate configuration: {e}")
            return {
                "success": False,
                "error": f"Configuration generation failed: {e}",
                "tests": [],
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "total_duration": 0,
                "environment": {
                    "base_url": "N/A",
                    "test_mode": False,
                    "timestamp": datetime.now(UTC).isoformat(),
                },
            }

        # Define test sequence
        tests = [
            self.test_basic_import,
            self.test_cli_help,
            self.test_discovery,
            self.test_data_extraction,
            self.test_cli_subcommands,
            self.test_error_handling,
        ]

        test_results = []

        for test_func in tests:
            try:
                logger.info(f"▶️ Running {test_func.__name__}")
                result = test_func()
                test_results.append(result)
                self.test_results.append(result)

                if result["success"]:
                    logger.info(
                        f"✅ {test_func.__name__} passed in {result['duration']:.2f}s"
                    )
                else:
                    logger.error(
                        f"❌ {test_func.__name__} failed in {result['duration']:.2f}s"
                    )

            except Exception as e:
                logger.exception(f"❌ {test_func.__name__} crashed")
                error_result = {
                    "test_name": test_func.__name__,
                    "success": False,
                    "duration": 0,
                    "details": {"error": str(e), "traceback": traceback.format_exc()},
                }
                test_results.append(error_result)
                self.test_results.append(error_result)

        # Calculate summary
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results if result["success"])
        total_duration = time.time() - start_time

        summary = {
            "success": passed_tests == total_tests,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "total_duration": total_duration,
            "tests": test_results,
            "environment": {
                "base_url": config.get("base_url"),
                "test_mode": config.get("test_mode"),
                "timestamp": datetime.now(UTC).isoformat(),
            },
        }

        # Save detailed results
        results_file = self.test_data_dir / "e2e_test_results.json"
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        logger.info(
            f"📊 E2E Testing completed: {passed_tests}/{total_tests} tests passed in {total_duration:.2f}s"
        )
        logger.info(f"📝 Detailed results saved to {results_file}")

        return summary

    def generate_report(self, summary: dict[str, Any]) -> str:
        """Generate human-readable test report."""
        report_lines = [
            "# tap-oracle-wms End-to-End Test Report",
            "",
            f"**Generated**: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"**Environment**: {summary['environment']['base_url']}",
            f"**Test Mode**: {summary['environment']['test_mode']}",
            "",
            "## Summary",
            "",
            f"- **Total Tests**: {summary['total_tests']}",
            f"- **Passed**: {summary['passed_tests']} ✅",
            f"- **Failed**: {summary['failed_tests']} ❌",
            f"- **Success Rate**: {(summary['passed_tests'] / summary['total_tests'] * 100):.1f}%",
            f"- **Total Duration**: {summary['total_duration']:.2f}s",
            "",
            "## Test Details",
            "",
        ]

        for test in summary["tests"]:
            status = "✅ PASS" if test["success"] else "❌ FAIL"
            report_lines.extend(
                [
                    f"### {test['test_name']} - {status}",
                    "",
                    f"- **Duration**: {test['duration']:.2f}s",
                    "",
                ]
            )

            if "details" in test:
                for key, value in test["details"].items():
                    if isinstance(value, str) and len(value) > 100:
                        value = value[:100] + "..."
                    report_lines.append(f"- **{key}**: {value}")
                report_lines.append("")

        return "\n".join(report_lines)


def main() -> None:
    """Main function to run E2E tests."""
    try:
        # Ensure we have .env file
        env_file = Path(".env")
        if not env_file.exists():
            logger.error(
                "❌ .env file not found. Please create one with required configuration."
            )
            sys.exit(1)

        # Run E2E tests
        runner = E2ETestRunner()
        summary = runner.run_all_tests()

        # Generate and save report
        report = runner.generate_report(summary)
        report_file = Path("e2e_test_data/test_report.md")
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)

        # Exit with appropriate code
        sys.exit(0 if summary["success"] else 1)

    except Exception:
        logger.exception("❌ E2E testing failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
