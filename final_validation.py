#!/usr/bin/env python3
"""Final validation of all fixes applied."""

from pathlib import Path
from typing import Any
import ast
import sys


def validate_file_syntax(file_path: str) -> dict[str, Any]:
    """Validate Python file syntax."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Parse AST to check syntax
        ast.parse(content)

        return {"file": file_path, "status": "✅ PASS", "syntax": "Valid", "issues": []}

    except SyntaxError as e:
        return {
            "file": file_path,
            "status": "❌ FAIL",
            "syntax": "Invalid",
            "issues": [f"Syntax error line {e.lineno}: {e.msg}"],
        }
    except Exception as e:
        return {
            "file": file_path,
            "status": "❌ ERROR",
            "syntax": "Unknown",
            "issues": [f"Error: {e}"],
        }


def check_critical_fixes() -> dict[str, Any]:
    """Check if critical fixes are in place."""
    fixes_verified = []

    # Check auth.py type annotations
    try:
        with open("src/tap_oracle_wms/auth.py", encoding="utf-8") as f:
            auth_content = f.read()

        if "stream: RESTStream" in auth_content:
            fixes_verified.append("✅ auth.py - RESTStream type annotation applied")
        else:
            fixes_verified.append("❌ auth.py - RESTStream type annotation missing")

        if "WMSBasicAuthenticator | WMSOAuth2Authenticator" in auth_content:
            fixes_verified.append("✅ auth.py - Union return type applied")
        else:
            fixes_verified.append("❌ auth.py - Union return type missing")

    except Exception as e:
        fixes_verified.append(f"❌ auth.py - Could not verify: {e}")

    # Check basic_usage.py refactoring
    try:
        with open("examples/basic_usage.py", encoding="utf-8") as f:
            basic_content = f.read()

        if "_setup_extraction_config" in basic_content:
            fixes_verified.append("✅ basic_usage.py - Function refactoring applied")
        else:
            fixes_verified.append("❌ basic_usage.py - Function refactoring missing")

        if "Path(" in basic_content:
            fixes_verified.append("✅ basic_usage.py - pathlib.Path usage applied")
        else:
            fixes_verified.append("❌ basic_usage.py - pathlib.Path usage missing")

    except Exception as e:
        fixes_verified.append(f"❌ basic_usage.py - Could not verify: {e}")

    # Check CLI docstring fix
    try:
        with open("src/tap_oracle_wms/cli.py", encoding="utf-8") as f:
            cli_content = f.read()

        if (
            'def safe_print(
                message: str,
                style: str | None = None,
            ) -> None:\n    """Safely print'
            in cli_content
        ):
            fixes_verified.append("✅ cli.py - Docstring fix applied")
        else:
            fixes_verified.append("❌ cli.py - Docstring fix missing")

    except Exception as e:
        fixes_verified.append(f"❌ cli.py - Could not verify: {e}")

    return {
        "total_checks": len(fixes_verified),
        "passed": len([f for f in fixes_verified if f.startswith("✅")]),
        "failed": len([f for f in fixes_verified if f.startswith("❌")]),
        "details": fixes_verified,
    }


def main() -> int:
    """Main validation function."""
    # Files to validate
    critical_files = [
        "src/tap_oracle_wms/auth.py",
        "src/tap_oracle_wms/cli.py",
        "src/tap_oracle_wms/tap.py",
        "src/tap_oracle_wms/streams.py",
        "examples/basic_usage.py",
        "examples/advanced_usage.py",
    ]

    syntax_results = []
    for file_path in critical_files:
        if Path(file_path).exists():
            result = validate_file_syntax(file_path)
            syntax_results.append(result)
        else:
            pass

    fixes_result = check_critical_fixes()
    for _detail in fixes_result["details"]:
        pass

    syntax_passed = len([r for r in syntax_results if r["status"] == "✅ PASS"])
    syntax_total = len(syntax_results)

    # Overall success calculation
    syntax_success = syntax_passed == syntax_total
    fixes_success = (
        fixes_result["passed"] >= fixes_result["total_checks"] * 0.8
    )  # 80% threshold

    if syntax_success and fixes_success:
        return 0
    if not syntax_success:
        pass
    if not fixes_success:
        pass
    return 1


if __name__ == "__main__":
    sys.exit(main())
