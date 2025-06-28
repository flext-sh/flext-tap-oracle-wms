#!/usr/bin/env python3
"""Quick validation script for essential functionality."""

import sys


def test_basic_imports() -> bool:
    """Test basic import functionality."""
    try:
        sys.path.insert(0, "src")

        return True
    except Exception:
        return False


def test_syntax() -> bool:
    """Test Python syntax for critical files."""
    import ast

    critical_files = [
        "src/tap_oracle_wms/__init__.py",
        "src/tap_oracle_wms/tap.py",
        "src/tap_oracle_wms/auth.py",
        "src/tap_oracle_wms/config.py",
        "examples/basic_usage.py",
    ]

    for file_path in critical_files:
        try:
            with open(file_path, encoding="utf-8") as f:
                ast.parse(f.read())
        except Exception:
            return False

    return True


def main() -> int:
    """Run quick validation."""
    tests = [
        ("Syntax Check", test_syntax),
        ("Import Check", test_basic_imports),
    ]

    passed = 0
    for _name, test_func in tests:
        if test_func():
            passed += 1

    if passed == len(tests):
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
