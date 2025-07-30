"""Comprehensive test suite for critical_validation module."""
# Copyright (c) 2025 FLEXT Team
# Licensed under the MIT License

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from flext_tap_oracle_wms.critical_validation import (
    enforce_mandatory_environment_variables,
    validate_schema_discovery_mode,
)


class TestEnforceMandatoryEnvironmentVariables:
    """Test enforce_mandatory_environment_variables function."""

    def test_enforce_with_correct_environment_variables(self) -> None:
        """Test enforcement passes with correct environment variables."""
        with (
            patch.dict(
                os.environ,
                {
                    "TAP_ORACLE_WMS_USE_METADATA_ONLY": "true",
                    "TAP_ORACLE_WMS_DISCOVERY_SAMPLE_SIZE": "0",
                },
                clear=False,
            ),
            patch(
                "flext_tap_oracle_wms.critical_validation.logger",
            ) as mock_logger,
        ):
            # Should not raise an exception
            enforce_mandatory_environment_variables()

            # Should log success message
            mock_logger.info.assert_called_with(
                "🚨 CRITICAL VALIDATION PASSED: Mandatory Oracle WMS tap environment variables validated",
            )
            mock_logger.error.assert_not_called()

    def test_enforce_fails_with_missing_use_metadata_only(self) -> None:
        """Test enforcement fails when USE_METADATA_ONLY is missing."""
        with patch.dict(
            os.environ,
            {"TAP_ORACLE_WMS_DISCOVERY_SAMPLE_SIZE": "0"},
            clear=False,
        ):
            # Remove the USE_METADATA_ONLY variable if it exists
            if "TAP_ORACLE_WMS_USE_METADATA_ONLY" in os.environ:
                del os.environ["TAP_ORACLE_WMS_USE_METADATA_ONLY"]

            with patch(
                "flext_tap_oracle_wms.critical_validation.logger",
            ) as mock_logger:
                with pytest.raises(SystemExit) as excinfo:
                    enforce_mandatory_environment_variables()

                # Should log error and exit
                if "TAP_ORACLE_WMS_USE_METADATA_ONLY must be 'true'" not in str(
                    excinfo.value,
                ):
                    msg = f"Expected {'TAP_ORACLE_WMS_USE_METADATA_ONLY must be true'} in {excinfo.value!s}"
                    raise AssertionError(
                        msg,
                    )
                mock_logger.error.assert_called_once()
                mock_logger.info.assert_not_called()

    def test_enforce_fails_with_incorrect_use_metadata_only(self) -> None:
        """Test enforcement fails when USE_METADATA_ONLY is incorrect."""
        test_values = ["false", "False", "1", "0", "yes", "no", ""]

        for value in test_values:
            with (
                patch.dict(
                    os.environ,
                    {
                        "TAP_ORACLE_WMS_USE_METADATA_ONLY": value,
                        "TAP_ORACLE_WMS_DISCOVERY_SAMPLE_SIZE": "0",
                    },
                    clear=False,
                ),
                patch(
                    "flext_tap_oracle_wms.critical_validation.logger",
                ) as mock_logger,
            ):
                with pytest.raises(SystemExit) as excinfo:
                    enforce_mandatory_environment_variables()

                # Should log error and exit (value is converted to lowercase)
                if f"but got '{value.lower()}'" not in str(excinfo.value):
                    msg = f"Expected {'but got {value.lower()}'} in {excinfo.value!s}"
                    raise AssertionError(
                        msg,
                    )
                mock_logger.error.assert_called_once()

    def test_enforce_fails_with_missing_discovery_sample_size(self) -> None:
        """Test enforcement fails when DISCOVERY_SAMPLE_SIZE is missing."""
        with patch.dict(
            os.environ,
            {"TAP_ORACLE_WMS_USE_METADATA_ONLY": "true"},
            clear=False,
        ):
            # Remove the DISCOVERY_SAMPLE_SIZE variable if it exists
            if "TAP_ORACLE_WMS_DISCOVERY_SAMPLE_SIZE" in os.environ:
                del os.environ["TAP_ORACLE_WMS_DISCOVERY_SAMPLE_SIZE"]

            with patch(
                "flext_tap_oracle_wms.critical_validation.logger",
            ) as mock_logger:
                with pytest.raises(SystemExit) as excinfo:
                    enforce_mandatory_environment_variables()

                # Should log error and exit (defaults to -1 when missing)
                assert (
                    "TAP_ORACLE_WMS_DISCOVERY_SAMPLE_SIZE must be exactly '0'"
                    in str(
                        excinfo.value,
                    )
                )
                if "but got '-1'" not in str(excinfo.value):
                    msg = f"Expected {'but got -1'} in {excinfo.value!s}"
                    raise AssertionError(
                        msg,
                    )
                mock_logger.error.assert_called_once()

    def test_enforce_fails_with_incorrect_discovery_sample_size(self) -> None:
        """Test enforcement fails when DISCOVERY_SAMPLE_SIZE is incorrect."""
        test_values = ["1", "10", "100", "-1", "5"]

        for value in test_values:
            with (
                patch.dict(
                    os.environ,
                    {
                        "TAP_ORACLE_WMS_USE_METADATA_ONLY": "true",
                        "TAP_ORACLE_WMS_DISCOVERY_SAMPLE_SIZE": value,
                    },
                    clear=False,
                ),
                patch(
                    "flext_tap_oracle_wms.critical_validation.logger",
                ) as mock_logger,
            ):
                with pytest.raises(SystemExit) as excinfo:
                    enforce_mandatory_environment_variables()

                # Should log error and exit
                if f"but got '{value}'" not in str(excinfo.value):
                    msg = f"Expected {f'but got {value}'} in {excinfo.value!s}"
                    raise AssertionError(
                        msg,
                    )
                mock_logger.error.assert_called_once()

    def test_enforce_passes_with_non_numeric_discovery_sample_size(self) -> None:
        """Test enforcement passes when DISCOVERY_SAMPLE_SIZE is non-numeric (centralized validator behavior)."""
        test_values = ["abc", "true", "false", "1.5", "null", "undefined"]

        for value in test_values:
            with (
                patch.dict(
                    os.environ,
                    {
                        "TAP_ORACLE_WMS_USE_METADATA_ONLY": "true",
                        "TAP_ORACLE_WMS_DISCOVERY_SAMPLE_SIZE": value,
                    },
                    clear=False,
                ),
                patch(
                    "flext_tap_oracle_wms.critical_validation.logger",
                ) as mock_logger,
            ):
                # Should not raise - centralized validator is more lenient
                enforce_mandatory_environment_variables()

                # Should log success message
                mock_logger.info.assert_called_with(
                    "🚨 CRITICAL VALIDATION PASSED: Mandatory Oracle WMS tap environment variables validated",
                )
                mock_logger.error.assert_not_called()

    def test_enforce_case_insensitive_use_metadata_only(self) -> None:
        """Test that USE_METADATA_ONLY is case-insensitive for 'true' check."""
        # All variations of 'true' should pass (function converts to lowercase)
        for value in ["true", "TRUE", "True", "tRuE"]:
            with patch.dict(
                os.environ,
                {
                    "TAP_ORACLE_WMS_USE_METADATA_ONLY": value,
                    "TAP_ORACLE_WMS_DISCOVERY_SAMPLE_SIZE": "0",
                },
                clear=False,
            ):
                # Should not raise
                enforce_mandatory_environment_variables()

        # Other values should fail
        for value in ["false", "FALSE", "False", "yes", "no", "1", "0"]:
            with (
                patch.dict(
                    os.environ,
                    {
                        "TAP_ORACLE_WMS_USE_METADATA_ONLY": value,
                        "TAP_ORACLE_WMS_DISCOVERY_SAMPLE_SIZE": "0",
                    },
                    clear=False,
                ),
                pytest.raises(SystemExit),
            ):
                enforce_mandatory_environment_variables()

    def test_enforce_error_messages_format(self) -> None:
        """Test that error messages contain required elements."""
        with patch.dict(
            os.environ,
            {"TAP_ORACLE_WMS_USE_METADATA_ONLY": "false"},
            clear=False,
        ):
            with pytest.raises(SystemExit) as excinfo:
                enforce_mandatory_environment_variables()

            error_msg = str(excinfo.value)
            if "❌ CRITICAL FAILURE:" not in error_msg:
                msg = f"Expected {'❌ CRITICAL FAILURE:'} in {error_msg}"
                raise AssertionError(
                    msg,
                )
            assert "NON-NEGOTIABLE" in error_msg
            # Note: actual error message format from flext-core Oracle validator

        with patch.dict(
            os.environ,
            {
                "TAP_ORACLE_WMS_USE_METADATA_ONLY": "true",
                "TAP_ORACLE_WMS_DISCOVERY_SAMPLE_SIZE": "1",
            },
            clear=False,
        ):
            with pytest.raises(SystemExit) as excinfo:
                enforce_mandatory_environment_variables()

            error_msg = str(excinfo.value)
            if "❌ CRITICAL FAILURE:" not in error_msg:
                msg = f"Expected {'❌ CRITICAL FAILURE:'} in {error_msg}"
                raise AssertionError(
                    msg,
                )
            # Note: actual error message format from flext-core Oracle validator

    def test_enforce_both_validations_fail_reports_all_errors(self) -> None:
        """Test that when both validations fail, all errors are reported.

        The centralized validator collects and reports all validation errors.
        """
        with patch.dict(
            os.environ,
            {
                "TAP_ORACLE_WMS_USE_METADATA_ONLY": "false",
                "TAP_ORACLE_WMS_DISCOVERY_SAMPLE_SIZE": "1",
            },
            clear=False,
        ):
            with pytest.raises(SystemExit) as excinfo:
                enforce_mandatory_environment_variables()

            # Should include both validation errors
            error_msg = str(excinfo.value)
            if "TAP_ORACLE_WMS_USE_METADATA_ONLY must be 'true'" not in error_msg:
                msg = f"Expected {'TAP_ORACLE_WMS_USE_METADATA_ONLY must be true'} in {error_msg}"
                raise AssertionError(
                    msg,
                )
            assert "DISCOVERY_SAMPLE_SIZE" in error_msg

    def test_enforce_logging_behavior(self) -> None:
        """Test logging behavior during enforcement."""
        # Test successful case
        with (
            patch.dict(
                os.environ,
                {
                    "TAP_ORACLE_WMS_USE_METADATA_ONLY": "true",
                    "TAP_ORACLE_WMS_DISCOVERY_SAMPLE_SIZE": "0",
                },
                clear=False,
            ),
            patch(
                "flext_tap_oracle_wms.critical_validation.logger",
            ) as mock_logger,
        ):
            enforce_mandatory_environment_variables()

            # Should only call info, not error
            mock_logger.info.assert_called_once()
            mock_logger.error.assert_not_called()

        # Test failure case
        with (
            patch.dict(
                os.environ,
                {"TAP_ORACLE_WMS_USE_METADATA_ONLY": "false"},
                clear=False,
            ),
            patch(
                "flext_tap_oracle_wms.critical_validation.logger",
            ) as mock_logger,
        ):
            with pytest.raises(SystemExit):
                enforce_mandatory_environment_variables()

            # Should only call error, not info
            mock_logger.error.assert_called_once()
            mock_logger.info.assert_not_called()


class TestValidateSchemaDiscoveryMode:
    """Test validate_schema_discovery_mode function."""

    def test_validate_with_correct_configuration(self) -> None:
        """Test validation with correct configuration."""
        with patch.dict(
            os.environ,
            {
                "TAP_ORACLE_WMS_USE_METADATA_ONLY": "true",
                "TAP_ORACLE_WMS_DISCOVERY_SAMPLE_SIZE": "0",
            },
            clear=False,
        ):
            result = validate_schema_discovery_mode()

            # Should succeed with correct configuration
            assert result.success

    def test_validate_with_incorrect_configuration(self) -> None:
        """Test validation with incorrect configuration."""
        test_cases = [
            {
                "TAP_ORACLE_WMS_USE_METADATA_ONLY": "false",
                "TAP_ORACLE_WMS_DISCOVERY_SAMPLE_SIZE": "0",
            },
            {
                "TAP_ORACLE_WMS_USE_METADATA_ONLY": "true",
                "TAP_ORACLE_WMS_DISCOVERY_SAMPLE_SIZE": "1",
            },
            {
                "TAP_ORACLE_WMS_USE_METADATA_ONLY": "false",
                "TAP_ORACLE_WMS_DISCOVERY_SAMPLE_SIZE": "1",
            },
        ]

        for env_vars in test_cases:
            with (
                patch.dict(os.environ, env_vars, clear=False),
                patch(
                    "flext_tap_oracle_wms.critical_validation.logger",
                ),
            ):
                # Should return failure result for invalid configuration
                result = validate_schema_discovery_mode()
                assert not result.success
                assert result.error is not None

    def test_validate_with_missing_environment_variables(self) -> None:
        """Test validation with missing environment variables."""
        # Remove environment variables if they exist
        env_backup = {}
        for var in [
            "TAP_ORACLE_WMS_USE_METADATA_ONLY",
            "TAP_ORACLE_WMS_DISCOVERY_SAMPLE_SIZE",
        ]:
            if var in os.environ:
                env_backup[var] = os.environ[var]
                del os.environ[var]

        try:
            result = validate_schema_discovery_mode()

            # Should return failure result for missing variables
            assert not result.success
            assert result.error is not None
        finally:
            # Restore environment variables
            for var, value in env_backup.items():
                os.environ[var] = value

    def test_validate_case_sensitivity(self) -> None:
        """Test that validation is case-insensitive for 'true' check."""
        test_cases = [
            ("TRUE", "0", True),  # Should succeed (converted to lowercase)
            ("True", "0", True),  # Should succeed (converted to lowercase)
            ("true", "0", True),  # Should succeed
            ("false", "0", False),  # Should fail
            ("TRUE", "1", False),  # Should fail (sample size wrong)
        ]

        for use_metadata, sample_size, should_succeed in test_cases:
            with patch.dict(
                os.environ,
                {
                    "TAP_ORACLE_WMS_USE_METADATA_ONLY": use_metadata,
                    "TAP_ORACLE_WMS_DISCOVERY_SAMPLE_SIZE": sample_size,
                },
                clear=False,
            ):
                result = validate_schema_discovery_mode()

                if should_succeed:
                    assert result.success
                else:
                    assert not result.success

    def test_validate_logging_format(self) -> None:
        """Test that validation returns proper FlextResult for invalid config."""
        with patch.dict(
            os.environ,
            {
                "TAP_ORACLE_WMS_USE_METADATA_ONLY": "custom_value",
                "TAP_ORACLE_WMS_DISCOVERY_SAMPLE_SIZE": "custom_size",
            },
            clear=False,
        ):
            result = validate_schema_discovery_mode()

            # Should return failure result for invalid configuration
            assert not result.success
            assert result.error is not None

    def test_validate_does_not_raise_exceptions(self) -> None:
        """Test that validate function never raises exceptions."""
        test_cases = [
            {},  # No env vars
            {"TAP_ORACLE_WMS_USE_METADATA_ONLY": "true"},  # Partial
            {"TAP_ORACLE_WMS_DISCOVERY_SAMPLE_SIZE": "0"},  # Partial
            {
                "TAP_ORACLE_WMS_USE_METADATA_ONLY": "invalid",
                "TAP_ORACLE_WMS_DISCOVERY_SAMPLE_SIZE": "invalid",
            },
        ]

        for env_vars in test_cases:
            with patch.dict(os.environ, env_vars, clear=True):
                # Should never raise an exception
                validate_schema_discovery_mode()

    def test_validate_empty_string_values(self) -> None:
        """Test validation with empty string values."""
        with patch.dict(
            os.environ,
            {
                "TAP_ORACLE_WMS_USE_METADATA_ONLY": "",
                "TAP_ORACLE_WMS_DISCOVERY_SAMPLE_SIZE": "",
            },
            clear=False,
        ):
            result = validate_schema_discovery_mode()

            # Should fail validation for empty values
            assert not result.success
            assert result.error is not None


class TestCriticalValidationIntegration:
    """Test integration between critical validation functions."""

    def test_enforce_and_validate_together(self) -> None:
        """Test that enforce and validate work correctly together."""
        with patch.dict(
            os.environ,
            {
                "TAP_ORACLE_WMS_USE_METADATA_ONLY": "true",
                "TAP_ORACLE_WMS_DISCOVERY_SAMPLE_SIZE": "0",
            },
            clear=False,
        ):
            # Both should succeed without issues
            enforce_mandatory_environment_variables()
            validate_schema_discovery_mode()

    def test_enforce_fails_but_validate_continues(self) -> None:
        """Test that validate can run even if enforce would fail."""
        with patch.dict(
            os.environ,
            {
                "TAP_ORACLE_WMS_USE_METADATA_ONLY": "false",
                "TAP_ORACLE_WMS_DISCOVERY_SAMPLE_SIZE": "1",
            },
            clear=False,
        ):
            # Enforce should fail
            with pytest.raises(SystemExit):
                enforce_mandatory_environment_variables()

            # But validate should not raise exceptions
            validate_schema_discovery_mode()

    def test_module_imports_correctly(self) -> None:
        """Test that the module imports and functions are accessible."""
        # Verify functions are importable and callable
        assert callable(enforce_mandatory_environment_variables)
        assert callable(validate_schema_discovery_mode)

        # Verify they have docstrings
        assert enforce_mandatory_environment_variables.__doc__ is not None
        assert validate_schema_discovery_mode.__doc__ is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
