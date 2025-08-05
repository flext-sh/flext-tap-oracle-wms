"""Custom exceptions for FLEXT Tap Oracle WMS.

Follows FLEXT exception hierarchy patterns with specific Oracle WMS tap errors.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flext_core.flext_types import TAnyDict, TValue


@dataclass
class ValidationContext:
    """Context information for validation errors."""

    stream_name: str | None = None
    field_name: str | None = None
    expected_type: str | None = None
    actual_value: object = None


class FlextTapOracleWMSError(Exception):
    """Base exception for Oracle WMS tap errors.

    All tap-specific exceptions inherit from this base class.
    """

    def __init__(
        self,
        message: str,
        error_code: str = "TAP_ERROR",
        context: TAnyDict | None = None,
    ) -> None:
        """Initialize tap exception.

        Args:
            message: Error message
            error_code: Error code for categorization
            context: Additional error context

        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        self.timestamp = datetime.now(UTC)

    def __str__(self) -> str:
        """String representation of the error."""
        return f"[{self.error_code}] {self.message}"


class FlextTapOracleWMSConfigurationError(FlextTapOracleWMSError):
    """Configuration-related errors."""

    def __init__(
        self,
        message: str,
        field: str | None = None,
        value: TValue = None,
        context: TAnyDict | None = None,
    ) -> None:
        """Initialize configuration error.

        Args:
            message: Error message
            field: Configuration field that caused the error
            value: Invalid value
            context: Additional context

        """
        if field:
            message = f"Configuration error in '{field}': {message}"

        super().__init__(
            message=message,
            error_code="CONFIG_ERROR",
            context=context or {},
        )

        self.field = field
        self.value = value

        # Add to context
        if field:
            self.context["field"] = field
        if value is not None:
            self.context["value"] = str(value)


class FlextTapOracleWMSConnectionError(FlextTapOracleWMSError):
    """Connection-related errors."""

    def __init__(
        self,
        message: str,
        url: str | None = None,
        status_code: int | None = None,
        response_body: str | None = None,
        context: TAnyDict | None = None,
    ) -> None:
        """Initialize connection error.

        Args:
            message: Error message
            url: URL that failed
            status_code: HTTP status code
            response_body: Response body if available
            context: Additional context

        """
        super().__init__(
            message=message,
            error_code="CONNECTION_ERROR",
            context=context or {},
        )

        self.url = url
        self.status_code = status_code
        self.response_body = response_body

        # Add to context
        if url:
            self.context["url"] = url
        if status_code:
            self.context["status_code"] = status_code
        if response_body:
            self.context["response_body"] = response_body[:500]  # Limit size


class FlextTapOracleWMSAuthenticationError(FlextTapOracleWMSError):
    """Authentication-related errors."""

    def __init__(
        self,
        message: str,
        username: str | None = None,
        auth_method: str = "basic",
        context: TAnyDict | None = None,
    ) -> None:
        """Initialize authentication error.

        Args:
            message: Error message
            username: Username that failed authentication
            auth_method: Authentication method used
            context: Additional context

        """
        super().__init__(
            message=message,
            error_code="AUTH_ERROR",
            context=context or {},
        )

        self.username = username
        self.auth_method = auth_method

        # Add to context (don't log password)
        if username:
            self.context["username"] = username
        self.context["auth_method"] = auth_method


class FlextTapOracleWMSDiscoveryError(FlextTapOracleWMSError):
    """Schema discovery errors."""

    def __init__(
        self,
        message: str,
        entity_name: str | None = None,
        field_name: str | None = None,
        sample_data: object = None,
        context: TAnyDict | None = None,
    ) -> None:
        """Initialize discovery error.

        Args:
            message: Error message
            entity_name: Entity being discovered
            field_name: Field that caused the error
            sample_data: Sample data that caused the error
            context: Additional context

        """
        super().__init__(
            message=message,
            error_code="DISCOVERY_ERROR",
            context=context or {},
        )

        self.entity_name = entity_name
        self.field_name = field_name
        self.sample_data = sample_data

        # Add to context
        if entity_name:
            self.context["entity"] = entity_name
        if field_name:
            self.context["field"] = field_name
        if sample_data is not None:
            self.context["sample_data_type"] = type(sample_data).__name__


class FlextTapOracleWMSStreamError(FlextTapOracleWMSError):
    """Stream processing errors."""

    def __init__(
        self,
        message: str,
        stream_name: str | None = None,
        record_count: int | None = None,
        last_record: TAnyDict | None = None,
        context: TAnyDict | None = None,
    ) -> None:
        """Initialize stream error.

        Args:
            message: Error message
            stream_name: Stream that failed
            record_count: Number of records processed before failure
            last_record: Last record processed
            context: Additional context

        """
        super().__init__(
            message=message,
            error_code="STREAM_ERROR",
            context=context or {},
        )

        self.stream_name = stream_name
        self.record_count = record_count
        self.last_record = last_record

        # Add to context
        if stream_name:
            self.context["stream"] = stream_name
        if record_count is not None:
            self.context["records_processed"] = record_count
        if last_record:
            # Only include record ID if available
            for id_field in ["id", "Id", "ID", "_id"]:
                if id_field in last_record:
                    self.context["last_record_id"] = last_record[id_field]
                    break


class FlextTapOracleWMSPaginationError(FlextTapOracleWMSError):
    """Pagination-related errors."""

    def __init__(
        self,
        message: str,
        stream_name: str | None = None,
        page_number: int | None = None,
        next_url: str | None = None,
        context: TAnyDict | None = None,
    ) -> None:
        """Initialize pagination error.

        Args:
            message: Error message
            stream_name: Stream being paginated
            page_number: Current page number
            next_url: Next page URL if available
            context: Additional context

        """
        super().__init__(
            message=message,
            error_code="PAGINATION_ERROR",
            context=context or {},
        )

        self.stream_name = stream_name
        self.page_number = page_number
        self.next_url = next_url

        # Add to context
        if stream_name:
            self.context["stream"] = stream_name
        if page_number is not None:
            self.context["page"] = page_number
        if next_url:
            self.context["next_url"] = next_url


class FlextTapOracleWMSRateLimitError(FlextTapOracleWMSError):
    """Rate limiting errors."""

    def __init__(
        self,
        message: str,
        retry_after: int | None = None,
        requests_made: int | None = None,
        limit: int | None = None,
        context: TAnyDict | None = None,
    ) -> None:
        """Initialize rate limit error.

        Args:
            message: Error message
            retry_after: Seconds to wait before retry
            requests_made: Number of requests made
            limit: Rate limit threshold
            context: Additional context

        """
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_ERROR",
            context=context or {},
        )

        self.retry_after = retry_after
        self.requests_made = requests_made
        self.limit = limit

        # Add to context
        if retry_after is not None:
            self.context["retry_after_seconds"] = retry_after
        if requests_made is not None:
            self.context["requests_made"] = requests_made
        if limit is not None:
            self.context["rate_limit"] = limit


class FlextTapOracleWMSDataValidationError(FlextTapOracleWMSError):
    """Data validation errors with structured context."""

    def __init__(
        self,
        message: str,
        validation_context: ValidationContext | None = None,
        context: TAnyDict | None = None,
    ) -> None:
        """Initialize data validation error.

        Args:
            message: Error message
            validation_context: Structured validation context information
            context: Additional context

        """
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            context=context or {},
        )

        self.validation_context = validation_context or ValidationContext()

        # Add validation context to error context for backward compatibility
        if self.validation_context.stream_name:
            self.context["stream"] = self.validation_context.stream_name
        if self.validation_context.field_name:
            self.context["field"] = self.validation_context.field_name
        if self.validation_context.expected_type:
            self.context["expected_type"] = self.validation_context.expected_type
        if self.validation_context.actual_value is not None:
            self.context["actual_type"] = type(
                self.validation_context.actual_value,
            ).__name__
            # Only include value if it's safe to log
            if isinstance(
                self.validation_context.actual_value, (str, int, float, bool),
            ):
                self.context["actual_value"] = str(
                    self.validation_context.actual_value,
                )[:100]

    # Backward compatibility properties
    @property
    def stream_name(self) -> str | None:
        """Get stream name for backward compatibility."""
        return self.validation_context.stream_name

    @property
    def field_name(self) -> str | None:
        """Get field name for backward compatibility."""
        return self.validation_context.field_name

    @property
    def expected_type(self) -> str | None:
        """Get expected type for backward compatibility."""
        return self.validation_context.expected_type

    @property
    def actual_value(self) -> object:
        """Get actual value for backward compatibility."""
        return self.validation_context.actual_value


class FlextTapOracleWMSRetryableError(FlextTapOracleWMSError):
    """Base class for retryable errors."""

    def __init__(
        self,
        message: str,
        error_code: str = "RETRYABLE_ERROR",
        retry_count: int = 0,
        max_retries: int | None = None,
        context: TAnyDict | None = None,
    ) -> None:
        """Initialize retryable error.

        Args:
            message: Error message
            error_code: Specific error code
            retry_count: Current retry attempt
            max_retries: Maximum retries allowed
            context: Additional context

        """
        super().__init__(
            message=message,
            error_code=error_code,
            context=context or {},
        )

        self.retry_count = retry_count
        self.max_retries = max_retries

        # Add to context
        self.context["retry_count"] = retry_count
        if max_retries is not None:
            self.context["max_retries"] = max_retries
            self.context["retries_remaining"] = max_retries - retry_count
