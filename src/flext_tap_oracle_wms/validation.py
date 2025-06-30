"""Configuration validation and connection testing for Oracle WMS TAP."""

from __future__ import annotations

from datetime import datetime
import re
from typing import Any
from urllib.parse import urlparse

from .config import config_schema, validate_auth_config, validate_pagination_config


def validate_url_format(url: str) -> tuple[bool, str]:
    """Validate URL format without network connection.

    Args:
    ----
        url: URL to validate

    Returns:
    -------
        Tuple of (is_valid, error_message)

    """
    try:
        parsed = urlparse(url)

        if not parsed.scheme:
            return False, "URL must include scheme (http/https)"

        if parsed.scheme not in {"http", "https"}:
            return False, "URL scheme must be http or https"

        if not parsed.netloc:
            return False, "URL must include hostname"

        # Basic hostname validation
        hostname_pattern = r"^[a-zA-Z0-9]([a-zA-Z0-9\-\.]*[a-zA-Z0-9])?$"
        hostname = parsed.netloc.split(":")[0]  # Remove port if present

        if not re.match(hostname_pattern, hostname):
            return False, "Invalid hostname format"

        return True, ""

    except Exception as e:  # noqa: BLE001
        return False, f"URL validation error: {e}"


def validate_credentials(config: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate authentication credentials format.

    Args:
    ----
        config: Configuration dictionary

    Returns:
    -------
        Tuple of (is_valid, list_of_errors)

    """
    errors = []

    # Validate auth configuration
    auth_error = validate_auth_config(config)
    if auth_error:
        errors.append(auth_error)

    # Additional credential format validation
    auth_method = config.get("auth_method", "basic")

    if auth_method == "basic":
        username = config.get("username", "")
        password = config.get("password", "")

        if len(username) < 3:
            errors.append("Username must be at least 3 characters")

        if len(password) < 6:
            errors.append("Password must be at least 6 characters")

    elif auth_method == "oauth2":
        client_id = config.get("oauth_client_id", "")
        client_secret = config.get("oauth_client_secret", "")
        token_url = config.get("oauth_token_url", "")

        if len(client_id) < 10:
            errors.append("OAuth client ID seems too short")

        if len(client_secret) < 20:
            errors.append("OAuth client secret seems too short")

        url_valid, url_error = validate_url_format(token_url)
        if not url_valid:
            errors.append(f"OAuth token URL: {url_error}")

    return len(errors) == 0, errors


def validate_performance_settings(config: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate performance and pagination settings.

    Args:
    ----
        config: Configuration dictionary

    Returns:
    -------
        Tuple of (is_valid, list_of_errors)

    """
    errors = []

    # Validate pagination
    page_error = validate_pagination_config(config)
    if page_error:
        errors.append(page_error)

    # Validate timeouts
    request_timeout = config.get("request_timeout", 7200)
    if request_timeout < 30:
        errors.append("Request timeout should be at least 30 seconds")
    elif request_timeout > 14400:  # 4 hours
        errors.append("Request timeout should not exceed 4 hours")

    connect_timeout = config.get("connect_timeout", 30)
    if connect_timeout < 5:
        errors.append("Connect timeout should be at least 5 seconds")
    elif connect_timeout > 300:
        errors.append("Connect timeout should not exceed 5 minutes")

    # Validate parallel streams
    max_streams = config.get("max_parallel_streams", 5)
    if max_streams < 1:
        errors.append("Must have at least 1 parallel stream")
    elif max_streams > 20:
        errors.append("Too many parallel streams may overwhelm the server")

    return len(errors) == 0, errors


def validate_business_settings(config: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate business-specific settings.

    Args:
    ----
        config: Configuration dictionary

    Returns:
    -------
        Tuple of (is_valid, list_of_errors)

    """
    errors = []

    # Validate company and facility codes
    company_code = config.get("company_code", "*")
    facility_code = config.get("facility_code", "*")

    if company_code != "*" and len(company_code) < 2:
        errors.append("Company code must be '*' or at least 2 characters")

    if facility_code != "*" and len(facility_code) < 2:
        errors.append("Facility code must be '*' or at least 2 characters")

    # Validate entity patterns if specified
    entities = config.get("entities")
    if entities and not isinstance(entities, list):
        errors.append("Entities must be a list of strings")
    elif entities and len(entities) == 0:
        errors.append("Entities list cannot be empty")

    # Validate date ranges if specified
    start_date = config.get("start_date")
    end_date = config.get("end_date")

    if start_date and end_date:
        try:

            start_dt = datetime.fromisoformat(str(start_date).replace("Z", "+00:00"))
            end_dt = datetime.fromisoformat(str(end_date).replace("Z", "+00:00"))

            if start_dt >= end_dt:
                errors.append("Start date must be before end date")

        except ValueError:
            errors.append("Invalid date format (use ISO 8601)")

    return len(errors) == 0, errors


def validate_complete_config(
    config: dict[str, Any],
) -> tuple[bool, dict[str, list[str]]]:
    """Perform complete configuration validation.

    Args:
    ----
        config: Configuration dictionary

    Returns:
    -------
        Tuple of (is_valid, errors_by_category)

    """
    all_errors: dict[str, list[str]] = {}

    # Validate base URL
    base_url = config.get("base_url", "")
    if not base_url:
        all_errors["connection"] = ["Base URL is required"]
    else:
        url_valid, url_error = validate_url_format(base_url)
        if not url_valid:
            all_errors["connection"] = [f"Base URL: {url_error}"]

    # Validate credentials
    cred_valid, cred_errors = validate_credentials(config)
    if not cred_valid:
        all_errors["authentication"] = cred_errors

    # Validate performance settings
    perf_valid, perf_errors = validate_performance_settings(config)
    if not perf_valid:
        all_errors["performance"] = perf_errors

    # Validate business settings
    biz_valid, biz_errors = validate_business_settings(config)
    if not biz_valid:
        all_errors["business"] = biz_errors

    is_valid = len(all_errors) == 0
    return is_valid, all_errors


def create_validation_report(config: dict[str, Any]) -> dict[str, Any]:
    """Create a comprehensive validation report.

    Args:
    ----
        config: Configuration dictionary

    Returns:
    -------
        Validation report with status and recommendations

    """
    is_valid, errors = validate_complete_config(config)

    report = {
        "valid": is_valid,
        "timestamp": "2025-06-29T12:00:00Z",
        "config_hash": hash(str(sorted(config.items()))),
        "errors": errors,
        "warnings": [],
        "recommendations": [],
    }

    # Add warnings for sub-optimal settings
    if config.get("page_size", 1000) > 2000:
        report["warnings"].append("Large page size may impact performance")

    if config.get("verify_ssl", True) is False:
        report["warnings"].append("SSL verification disabled - security risk")

    if config.get("request_timeout", 7200) > 7200:
        report["warnings"].append("Very long timeout may cause operational issues")

    # Add recommendations
    if not config.get("monitoring", {}).get("enabled", False):
        report["recommendations"].append("Enable monitoring for production use")

    if config.get("log_level", "INFO") == "DEBUG":
        report["recommendations"].append("Use INFO log level for production")

    if not config.get("circuit_breaker", {}).get("enabled", True):
        report["recommendations"].append("Enable circuit breaker for resilience")

    return report


def test_config_without_connection(config: dict[str, Any]) -> dict[str, Any]:
    """Test configuration thoroughly without external connections.

    Args:
    ----
        config: Configuration dictionary

    Returns:
    -------
        Test results with detailed analysis

    """
    start_time = datetime.now()

    # Generate validation report
    report = create_validation_report(config)

    # Test configuration parsing and schema validation
    try:

        # This validates against the Singer SDK schema
        schema_properties = config_schema.get("properties", {})
        missing_required = []
        invalid_types = []

        for prop_name, prop_def in schema_properties.items():
            if prop_def.get("required", False) and prop_name not in config:
                missing_required.append(prop_name)

            if prop_name in config:
                expected_type = prop_def.get("type")
                actual_value = config[prop_name]

                # Basic type checking
                if expected_type == "string" and not isinstance(actual_value, str):
                    invalid_types.append(
                        f"{prop_name}: expected string, got {type(actual_value).__name__}"
                    )
                elif expected_type == "integer" and not isinstance(actual_value, int):
                    invalid_types.append(
                        f"{prop_name}: expected integer, got {type(actual_value).__name__}"
                    )
                elif expected_type == "boolean" and not isinstance(actual_value, bool):
                    invalid_types.append(
                        f"{prop_name}: expected boolean, got {type(actual_value).__name__}"
                    )

        if missing_required:
            report["errors"]["schema"] = [
                f"Missing required fields: {', '.join(missing_required)}"
            ]

        if invalid_types:
            if "schema" not in report["errors"]:
                report["errors"]["schema"] = []
            report["errors"]["schema"].extend(invalid_types)

    except Exception as e:  # noqa: BLE001
        report["errors"]["schema"] = [f"Schema validation error: {e}"]

    # Calculate test duration
    end_time = datetime.now()
    duration_ms = (end_time - start_time).total_seconds() * 1000

    # Final test results
    return {
        "config_valid": report["valid"],
        "test_duration_ms": duration_ms,
        "validation_report": report,
        "ready_for_connection": report["valid"] and len(report["warnings"]) < 3,
        "summary": {
            "total_errors": sum(len(errs) for errs in report["errors"].values()),
            "total_warnings": len(report["warnings"]),
            "categories_with_errors": list(report["errors"].keys()),
        },
    }
