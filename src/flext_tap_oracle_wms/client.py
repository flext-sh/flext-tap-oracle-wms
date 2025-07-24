"""Oracle WMS Client Module.

This module provides HTTP client functionality for Oracle WMS API integration
using flext-core patterns and Singer SDK compatibility.
"""

# Use centralized logger from flext-infrastructure.monitoring.flext-observability - NO FALLBACKS
# Removed circular dependency - use DI pattern

import logging
from http import HTTPStatus
from types import TracebackType
from typing import (
    Any,
    Self,
)

import httpx

from flext_tap_oracle_wms.models import WMSConfig

logger = logging.getLogger(__name__)


class WMSClientError(Exception):
    """Base exception for WMS client errors."""


class AuthenticationError(WMSClientError):
    """Exception raised for authentication errors."""


class WMSConnectionError(WMSClientError):
    """Exception raised for connection errors."""


class WMSClient:
    """HTTP client for Oracle WMS API operations."""

    def __init__(self, config: WMSConfig, metrics: Any = None) -> None:
        """Initialize WMS client.

        Args:
            config: WMS configuration
            metrics: Metrics tracking instance

        """
        self.config = config
        self.metrics = metrics

        # Create HTTP client with configuration
        self.client = httpx.Client(
            base_url=str(config.base_url).rstrip("/"),
            timeout=config.timeout,
            verify=getattr(config, "verify_ssl", True),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "flext-data.taps.flext-data.taps.flext-tap-oracle-wms/1.0",
            },
        )

        # Apply authentication if configured
        if config.username and config.password:
            import base64

            credentials = f"{config.username}:{config.password}"
            encoded = base64.b64encode(credentials.encode()).decode()
            self.client.headers["Authorization"] = f"Basic {encoded}"

        logger.debug("WMS client initialized for %s", config.base_url)

    def __enter__(self) -> Self:
        """Context manager entry."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Context manager exit - close client."""
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
            API response data

        Raises:
            WMSConnectionError: Connection or timeout errors
            WMSClientError: Other API errors

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
            msg = f"Connection failed: {e}"
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
        """Discover available WMS entities.

        Returns:
            List of discovered entity definitions

        """
        logger.info("Discovering WMS entities")

        # Try common WMS entity discovery endpoints
        endpoints = [
            "/api/entities",
            "/api/v1/entities",
            "/wms/lgfapi/v10/entity",
            "/wms/lgfapi/v11/entity",
        ]

        for endpoint in endpoints:
            try:
                result = self.get(endpoint)
                # Check if result contains data key with list:
                # (from wrapped list response)
                if "data" in result and isinstance(result["data"], list):
                    entities_list = result["data"]
                    if entities_list:
                        logger.info(
                            "Found %d entities via %s",
                            len(entities_list),
                            endpoint,
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
        """Get data for a specific WMS entity.

        Args:
            entity_name: Name of the entity to retrieve
            params: Additional query parameters

        Returns:
            Entity data from WMS API

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
            return True
        except (AuthenticationError, WMSConnectionError, WMSClientError):
            return False

    @staticmethod
    def _handle_response_errors(response: httpx.Response) -> None:
        """Handle HTTP response errors.

        Args:
            response: HTTP response to check

        Raises:
            AuthenticationError: For 401/403 errors
            WMSConnectionError: For server errors
            WMSClientError: For client errors

        """
        if response.status_code == HTTPStatus.UNAUTHORIZED:
            msg = "Authentication failed: Invalid credentials"
            raise AuthenticationError(msg)
        if response.status_code == HTTPStatus.FORBIDDEN:
            msg = "Authentication failed: Access denied"
            raise AuthenticationError(msg)
        if response.status_code >= HTTPStatus.INTERNAL_SERVER_ERROR:
            msg = f"Server error: {response.status_code}"
            raise WMSConnectionError(msg)
        if response.status_code >= HTTPStatus.BAD_REQUEST:
            msg = f"Client error: {response.status_code}"
            raise WMSClientError(msg)
