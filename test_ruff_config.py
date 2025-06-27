#!/usr/bin/env python3
"""Test ruff configuration."""

from pathlib import Path
import subprocess
import sys
from typing import Optional


def test_ruff_config() -> Optional[bool]:
    """Test if ruff configuration is working."""
    try:
        # Test if ruff can read the config
        result = subprocess.run(
            ["python", "-c", "import ruff"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

        if result.returncode != 0:
            return False

        # Check if pyproject.toml exists
        if Path("pyproject.toml").exists():
            # Check if our configuration is present
            with open("pyproject.toml", encoding="utf-8") as f:
                content = f.read()

            if "[tool.ruff.lint]" in content:
                return bool("ignore = [" in content and "ANN401" in content)
            return False
        return False

    except Exception:
        return False


if __name__ == "__main__":
    success = test_ruff_config()

    if success:
        sys.exit(0)
    else:
        sys.exit(1)
