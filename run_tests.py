#!/usr/bin/env python3
"""Test runner script for Oracle WMS tap.

This script provides an easy way to run different test suites.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n🔥 {description}")
    print(f"Command: {' '.join(cmd)}")
    print("=" * 60)

    try:
        result = subprocess.run(cmd, check=True, cwd=Path(__file__).parent)
        print(f"✅ {description} - PASSED")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED (exit code: {e.returncode})")
        return False


def main():
    """Main test runner."""
    if len(sys.argv) < 2:
        print("Usage: python run_tests.py [unit|integration|e2e|all|lint|quick]")
        print("\nTest suites:")
        print("  unit        - Run unit tests only")
        print("  integration - Run integration tests only")
        print("  e2e         - Run E2E tests (requires WMS config)")
        print("  all         - Run all tests")
        print("  lint        - Run ruff and mypy checks")
        print("  quick       - Run unit + integration tests")
        sys.exit(1)

    test_type = sys.argv[1].lower()
    success = True

    # Activate virtual environment command prefix
    venv_cmd = ["python", "-m"]

    if test_type == "unit":
        success = run_command(
            venv_cmd + ["pytest", "tests/unit/", "-v"],
            "Unit Tests",
        )

    elif test_type == "integration":
        success = run_command(
            venv_cmd + ["pytest", "tests/integration/", "-v"],
            "Integration Tests",
        )

    elif test_type == "e2e":
        print("\n⚠️  E2E tests require real WMS configuration in .env file")
        success = run_command(
            venv_cmd + ["pytest", "tests/e2e/", "-v", "--run-e2e"],
            "End-to-End Tests",
        )

    elif test_type == "all":
        tests = [
            (venv_cmd + ["pytest", "tests/unit/", "-v"], "Unit Tests"),
            (venv_cmd + ["pytest", "tests/integration/", "-v"], "Integration Tests"),
            (venv_cmd + ["pytest", "tests/e2e/", "-v"], "E2E Tests (skipped without config)"),
        ]
        for cmd, desc in tests:
            if not run_command(cmd, desc):
                success = False

    elif test_type == "lint":
        lint_tests = [
            (["ruff", "check", "src/", "tests/"], "Ruff Linting (ZERO TOLERANCE)"),
            (["mypy", "src/tap_oracle_wms/", "tests/"], "MyPy Type Checking (STRICT MODE)"),
        ]
        for cmd, desc in lint_tests:
            if not run_command(cmd, desc):
                success = False

    elif test_type == "quick":
        quick_tests = [
            (venv_cmd + ["pytest", "tests/unit/", "-v"], "Unit Tests"),
            (venv_cmd + ["pytest", "tests/integration/", "-v"], "Integration Tests"),
        ]
        for cmd, desc in quick_tests:
            if not run_command(cmd, desc):
                success = False

    else:
        print(f"❌ Unknown test type: {test_type}")
        sys.exit(1)

    # Final status
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("💥 SOME TESTS FAILED!")
        sys.exit(1)


if __name__ == "__main__":
    main()
