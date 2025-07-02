#!/usr/bin/env python3
"""Validate all configuration files for TAP Oracle WMS."""

import json
import sys
from pathlib import Path


def validate_config_file(config_path: Path) -> tuple[bool, str]:
    """Validate a single configuration file.

    Args:
        config_path: Path to the configuration file

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        with Path(config_path).open(encoding="utf-8") as f:
            config = json.load(f)

        # Check required fields
        required_fields = ["base_url", "username", "password", "auth_method"]
        missing_fields = [field for field in required_fields if field not in config]

        if missing_fields:
            return False, f"Missing required fields: {missing_fields}"

        # Check page_size (now required)
        if "page_size" not in config:
            return False, "Missing required field: page_size"

        # Check for deprecated page_mode="paged"
        if config.get("page_mode") == "paged":
            return False, "page_mode='paged' is deprecated, should be 'sequenced'"

        # Validate simple_date_expressions if present
        if "simple_date_expressions" in config:
            sde = config["simple_date_expressions"]
            if not isinstance(sde, dict):
                return False, "simple_date_expressions must be a dict"

            # Check for valid date expressions

            for filters in sde.values():
                for filter_value in filters.values():
                    if (
                        isinstance(filter_value, str)
                        and not any(
                            pattern in filter_value
                            for pattern in ["today", "yesterday", "tomorrow", "now"]
                        )
                        and not any(op in filter_value for op in ["+", "-"])
                    ):
                        # Basic validation for date expressions
                        return False, f"Invalid date expression: {filter_value}"

        # Validate circuit_breaker if present
        if "circuit_breaker" in config:
            cb = config["circuit_breaker"]
            if not isinstance(cb, dict):
                return False, "circuit_breaker must be a dict"

            if "failure_threshold" in cb and not isinstance(
                cb["failure_threshold"], int
            ):
                return False, "circuit_breaker.failure_threshold must be an integer"

            if "recovery_timeout" in cb and not isinstance(cb["recovery_timeout"], int):
                return False, "circuit_breaker.recovery_timeout must be an integer"

        return True, "Valid"

    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"
    except Exception as e:
        return False, f"Error reading file: {e}"


def main():
    """Validate all configuration files."""
    evidence_dir = Path(__file__).parent
    # Look for config files in examples/configs directory
    examples_dir = evidence_dir.parent / "examples" / "configs"
    config_files = list(examples_dir.glob("*.json"))

    valid_count = 0
    total_count = len(config_files)

    for config_file in sorted(config_files):
        is_valid, message = validate_config_file(config_file)

        if is_valid:
            valid_count += 1

    if valid_count == total_count:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
