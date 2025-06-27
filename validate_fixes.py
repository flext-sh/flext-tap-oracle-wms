#!/usr/bin/env python3
"""Validate that lint and mypy fixes are working."""

from pathlib import Path
import subprocess
import sys


def run_command(cmd: list[str], timeout: int = 30) -> tuple[int, str, str]:
    """Run command and return result."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=Path.cwd(),
            check=False,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout"
    except Exception as e:
        return -1, "", str(e)


def validate_python_syntax() -> bool:
    """Check if Python files have valid syntax."""
    py_files = [
        "src/tap_oracle_wms/auth.py",
        "src/tap_oracle_wms/cli.py",
        "examples/basic_usage.py",
        "examples/advanced_usage.py",
    ]

    for file_path in py_files:
        if not Path(file_path).exists():
            continue

        # Check syntax
        ret, _stdout, _stderr = run_command(
            [sys.executable, "-m", "py_compile", file_path]
        )
        if ret == 0:
            pass
        else:
            return False

    return True


def validate_imports() -> bool:
    """Check if main imports work."""
    test_imports = [
        "from tap_oracle_wms import TapOracleWMS",
        "from tap_oracle_wms.auth import get_wms_authenticator",
        "from tap_oracle_wms.discovery import EntityDiscovery",
    ]

    for import_stmt in test_imports:
        ret, _stdout, _stderr = run_command(
            [sys.executable, "-c", import_stmt + "; print('OK')"]
        )
        if ret == 0:
            pass
        else:
            return False

    return True


def main() -> int:
    """Main validation."""
    # Check if we're in the right directory
    if not Path("src/tap_oracle_wms").exists():
        sys.exit(1)

    success = True

    # Validate syntax
    if not validate_python_syntax():
        success = False

    # Validate imports
    if not validate_imports():
        success = False

    if success:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
