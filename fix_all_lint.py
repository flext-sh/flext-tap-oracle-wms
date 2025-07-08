#!/usr/bin/env python3
"""Script to fix all lint and type issues systematically."""

from __future__ import annotations

from pathlib import Path
import subprocess


def run_command(cmd: list[str]) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def fix_file(file_path: Path) -> bool:
    """Fix a single file's lint issues."""
    print(f"\n{'=' * 60}")
    print(f"Fixing: {file_path}")
    print("=" * 60)

    # First run ruff fix
    cmd = ["ruff", "check", "--config", ".ruff_strict.toml", str(file_path), "--fix"]
    returncode, stdout, stderr = run_command(cmd)

    if returncode == 0:
        print(f"✅ {file_path} is clean!")
        return True

    # Show remaining issues
    cmd = ["ruff", "check", "--config", ".ruff_strict.toml", str(file_path)]
    returncode, stdout, stderr = run_command(cmd)

    print("Remaining issues:")
    print(stderr if stderr else stdout)

    return False


def main():
    """Main function."""
    src_dir = Path("src/tap_oracle_wms")

    # Get all Python files
    py_files = sorted(src_dir.glob("*.py"))

    # Skip modern files that are already clean
    modern_files = {
        "models.py",
        "client.py",
        "discovery_modern.py",
        "stream_modern.py",
        "tap_modern.py",
        "__init___modern.py",
    }

    files_to_fix = [f for f in py_files if f.name not in modern_files]

    print(f"Found {len(files_to_fix)} files to fix")

    clean_files = []
    remaining_files = []

    for file_path in files_to_fix:
        if fix_file(file_path):
            clean_files.append(file_path)
        else:
            remaining_files.append(file_path)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"✅ Clean files: {len(clean_files)}")
    print(f"❌ Files with issues: {len(remaining_files)}")

    if remaining_files:
        print("\nFiles still needing manual fixes:")
        for f in remaining_files:
            print(f"  - {f}")


if __name__ == "__main__":
    main()
