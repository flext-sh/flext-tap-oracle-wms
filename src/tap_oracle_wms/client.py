"""Enterprise HTTP client for Oracle WMS - Clean, simple, performant."""

from __future__ import annotations

from http import HTTPStatus
import logging
from typing import TYPE_CHECKING, Any, Self

import httpx

if TYPE_CHECKING:
    from types import TracebackType

    from .models import TapMetrics, WMSConfig

logger = logging.getLogger(__name__)


class WMSClientError(Exception):
    """Base WMS client error."""


class AuthenticationError(WMSClientError):
    """Authentication failed."""


class WMSConnectionError(WMSClientError):
    """Connection to WMS failed."""


class WMSClient:
    """Clean, simple Oracle WMS HTTP client.

    Replaces the over-engineered multi-layer authentication and request system
    with a single, focused client using modern httpx.
    """

    def __init__(self, config: WMSConfig, metrics: TapMetrics) -> None:
        """Initialize WMS client with configuration and metrics."""
        self.config = config
        self.metrics = metrics

        # Create httpx client with sensible defaults
        self.client = httpx.Client(
            base_url=str(config.base_url),
            timeout=config.request_timeout,
            verify=config.verify_ssl,
            auth=(config.username, config.password),  # Basic auth
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "flext-tap-oracle-wms/1.0",
            },
        )

    def __enter__(self) -> Self:
        """Enter context manager."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit context manager."""
        self.client.close()

    def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make GET request to WMS API.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            JSON response data

        Raises:
            AuthenticationError: If auth fails
            WMSConnectionError: If connection fails
            WMSClientError: For other API errors

        """
        self.metrics.add_api_call()

        try:
            response = self.client.get(endpoint, params=params or {})

            # Handle common HTTP status codes
            self._handle_response_errors(response)

            response.raise_for_status()
            result = response.json()
            return result if isinstance(result, dict) else {"data": result}

        except httpx.ConnectError as e:
            msg = f"Failed to connect to WMS: {e}"
            raise WMSConnectionError(msg) from e
        except httpx.TimeoutException as e:
            msg = f"Request timeout: {e}"
            raise WMSConnectionError(msg) from e
        except Exception as e:
            if isinstance(
                e,
                AuthenticationError | WMSConnectionError | WMSClientError,
            ):
                raise
            msg = f"Unexpected error: {e}"
            raise WMSClientError(msg) from e

    def discover_entities(self) -> list[dict[str, Any]]:
        """Discover available entities from WMS API.

        Simplified from the complex multi-layer discovery system.
        """
        logger.info("Discovering WMS entities")

        # Try common WMS entity discovery endpoints
        for endpoint in ["/entities", "/api/entities", "/rest/entities"]:
            try:
                result = self.get(endpoint)
                # Check if result contains data key with list
                # (from wrapped list response)
                if "data" in result and isinstance(result["data"], list):
                    entities_list = result["data"]
                    if entities_list:
                        logger.info(
                            "Found %d entities via %s", len(entities_list), endpoint
                        )
                        return entities_list
                elif "entities" in result:
                    entities = result["entities"]
                    if isinstance(entities, list):
                        logger.info("Found %d entities via %s", len(entities), endpoint)
                        return entities
            except WMSClientError:
                continue

        logger.warning("No entities discovered - will try common WMS endpoints")
        return []

    def get_entity_data(
        self,
        entity_name: str,
        params: dict[str, str | int | float | bool] | None = None,
    ) -> dict[str, Any]:
        """Get data for specific entity.

        Args:
            entity_name: Name of the WMS entity
            params: Query parameters (filters, pagination, etc.)

        Returns:
            Entity data response

        """
        endpoint = f"/api/{entity_name}"

        # Add WMS scoping parameters
        query_params = {
            "company_code": self.config.company_code,
            "facility_code": self.config.facility_code,
            "page_size": self.config.page_size,
            **(params or {}),
        }

        return self.get(endpoint, query_params)

    def test_connection(self) -> bool:
        """Test connection to WMS API.

        Returns:
            True if connection successful, False otherwise

        """
        try:
            # Try a simple endpoint to test connectivity
            self.get("/api/ping")
        except (AuthenticationError, WMSConnectionError, WMSClientError):
            # Try alternative health check endpoints
            for endpoint in ["/health", "/status", "/api/health"]:
                try:
                    self.get(endpoint)
                except (AuthenticationError, WMSConnectionError, WMSClientError):
                    continue
                else:
                    return True
            return False
        else:
            return True

    def _handle_response_errors(self, response: httpx.Response) -> None:
        """Handle HTTP response errors.

        Args:
            response: HTTP response to check

        Raises:
            AuthenticationError: For 401/403 errors
            WMSConnectionError: For 5xx errors
            WMSClientError: For other 4xx errors

        """
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            msg = "Invalid credentials"
            raise AuthenticationError(msg)
        if response.status_code == HTTPStatus.FORBIDDEN:
            msg = "Access forbidden"
            raise AuthenticationError(msg)
        if response.status_code >= HTTPStatus.INTERNAL_SERVER_ERROR:
            msg = f"Server error: {response.status_code}"
            raise WMSConnectionError(msg)
        if response.status_code >= HTTPStatus.BAD_REQUEST:
            msg = f"Client error: {response.status_code} - {response.text}"
            raise WMSClientError(msg)
