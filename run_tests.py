#!/usr/bin/env python3
"""Comprehensive test runner for tap-oracle-wms.

This script provides multiple test execution strategies for development, CI/CD, and validation.
"""

import argparse
from pathlib import Path
import subprocess
import sys
import time
from typing import Any


class TapTestRunner:
    """Comprehensive test runner for tap-oracle-wms."""

    def __init__(self, verbose: bool = False) -> None:
        self.verbose = verbose
        self.base_cmd = ["python", "-m", "pytest"]

    def run_command(self, cmd: list[str], description: str) -> dict[str, Any]:
        """Run a command and return results."""
        if self.verbose:
            pass

        start_time = time.time()
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent, check=False
            )
            end_time = time.time()

            return {
                "success": result.returncode == 0,
                "duration": end_time - start_time,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except Exception as e:
            return {
                "success": False,
                "duration": time.time() - start_time,
                "error": str(e),
                "returncode": -1
            }

    def unit_tests(self) -> dict[str, Any]:
        """Run unit tests."""
        cmd = [*self.base_cmd, "-m", "unit", "--tb=short", "-v" if self.verbose else "-q"]
        return self.run_command(cmd, "Running Unit Tests")

    def integration_tests(self) -> dict[str, Any]:
        """Run integration tests."""
        cmd = [*self.base_cmd, "-m", "integration", "--tb=short", "-v" if self.verbose else "-q"]
        return self.run_command(cmd, "Running Integration Tests")

    def e2e_tests(self) -> dict[str, Any]:
        """Run end-to-end tests."""
        cmd = [*self.base_cmd, "-m", "e2e", "--tb=short", "-v" if self.verbose else "-q"]
        return self.run_command(cmd, "Running End-to-End Tests")

    def performance_tests(self) -> dict[str, Any]:
        """Run performance tests."""
        cmd = [*self.base_cmd, "-m", "performance", "--tb=short", "-v" if self.verbose else "-q"]
        return self.run_command(cmd, "Running Performance Tests")

    def coverage_tests(self) -> dict[str, Any]:
        """Run tests with coverage."""
        cmd = [*self.base_cmd, "-m", "not live and not slow", "--cov=src/tap_oracle_wms", "--cov-report=term-missing", "--cov-report=html:htmlcov", "--cov-fail-under=85", "--tb=short"]
        return self.run_command(cmd, "Running Tests with Coverage")

    def smoke_tests(self) -> dict[str, Any]:
        """Run smoke tests (fast validation)."""
        cmd = [*self.base_cmd, "-m", "unit", "--maxfail=3", "--tb=line", "-q"]
        return self.run_command(cmd, "Running Smoke Tests")

    def ci_tests(self) -> dict[str, Any]:
        """Run CI/CD appropriate tests."""
        cmd = [*self.base_cmd, "-m", "not live and not slow", "--tb=short", "--junitxml=test-results.xml", "--cov=src/tap_oracle_wms", "--cov-report=xml:coverage.xml", "--cov-fail-under=85", "-v" if self.verbose else "-q"]
        return self.run_command(cmd, "Running CI/CD Tests")

    def discovery_validation(self) -> dict[str, Any]:
        """Validate test discovery."""
        cmd = [*self.base_cmd, "--collect-only", "-q"]
        return self.run_command(cmd, "Validating Test Discovery")

    def run_comprehensive_suite(self) -> dict[str, list[dict[str, Any]]]:
        """Run comprehensive test suite."""
        results = {
            "unit": [],
            "integration": [],
            "e2e": [],
            "performance": [],
            "coverage": []
        }

        # Discovery validation
        discovery_result = self.discovery_validation()
        if not discovery_result["success"]:
            return results

        len([line for line in discovery_result["stdout"].split("\n") if "::" in line])

        # Unit tests
        unit_result = self.unit_tests()
        results["unit"].append(unit_result)
        self._print_result("Unit Tests", unit_result)

        # Integration tests
        integration_result = self.integration_tests()
        results["integration"].append(integration_result)
        self._print_result("Integration Tests", integration_result)

        # E2E tests
        e2e_result = self.e2e_tests()
        results["e2e"].append(e2e_result)
        self._print_result("End-to-End Tests", e2e_result)

        # Performance tests
        performance_result = self.performance_tests()
        results["performance"].append(performance_result)
        self._print_result("Performance Tests", performance_result)

        # Coverage
        coverage_result = self.coverage_tests()
        results["coverage"].append(coverage_result)
        self._print_result("Coverage Tests", coverage_result)

        return results

    def _print_result(self, test_type: str, result: dict[str, Any]) -> None:
        """Print test result summary."""
        if result["success"] or (self.verbose and "stderr" in result):
            pass

    def run_development_workflow(self) -> bool:
        """Run development-friendly test workflow."""
        # 1. Smoke tests first (fastest feedback)
        smoke_result = self.smoke_tests()
        self._print_result("Smoke Tests", smoke_result)

        if not smoke_result["success"]:
            return False

        # 2. Full unit tests
        unit_result = self.unit_tests()
        self._print_result("Unit Tests", unit_result)

        if not unit_result["success"]:
            pass

        # 3. Integration tests
        integration_result = self.integration_tests()
        self._print_result("Integration Tests", integration_result)

        overall_success = smoke_result["success"] and unit_result["success"] and integration_result["success"]

        if overall_success:
            pass
        else:
            pass

        return overall_success


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Comprehensive test runner for tap-oracle-wms")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--type", choices=[
        "unit", "integration", "e2e", "performance", "coverage",
        "smoke", "ci", "comprehensive", "development"
    ], default="development", help="Type of tests to run")

    args = parser.parse_args()

    runner = TapTestRunner(verbose=args.verbose)

    if args.type == "unit":
        result = runner.unit_tests()
    elif args.type == "integration":
        result = runner.integration_tests()
    elif args.type == "e2e":
        result = runner.e2e_tests()
    elif args.type == "performance":
        result = runner.performance_tests()
    elif args.type == "coverage":
        result = runner.coverage_tests()
    elif args.type == "smoke":
        result = runner.smoke_tests()
    elif args.type == "ci":
        result = runner.ci_tests()
    elif args.type == "comprehensive":
        results = runner.run_comprehensive_suite()
        # Print summary

        total_passed = 0
        total_tests = 0

        for test_results in results.values():
            if test_results:
                result = test_results[0]
                "✅ PASSED" if result["success"] else "❌ FAILED"
                if result["success"]:
                    total_passed += 1
                total_tests += 1

        sys.exit(0 if total_passed == total_tests else 1)
    elif args.type == "development":
        success = runner.run_development_workflow()
        sys.exit(0 if success else 1)

    # Single test type
    if isinstance(result, dict):
        runner._print_result(args.type.title(), result)
        sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
