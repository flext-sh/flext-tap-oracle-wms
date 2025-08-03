"""Oracle WMS Authentication Module.

This module provides authentication capabilities for Oracle WMS API integration
using flext-core patterns and Singer SDK compatibility.
"""

import base64

# Removed circular dependency - use DI pattern
import threading
from typing import Any, cast

# Direct imports (ZERO TOLERANCE for fallbacks)
import requests
from flext_core import get_logger

# Import authenticator from Singer SDK directly
from singer_sdk.authenticators import SimpleAuthenticator
from singer_sdk.streams import RESTStream

logger = get_logger(__name__)


class WMSBasicAuthenticator(SimpleAuthenticator):
    """Legacy WMS Basic authenticator - True Facade with Pure Delegation.

    Delegates entirely to enterprise authentication service while maintaining
    Singer SDK SimpleAuthenticator interface.
    """

    def __init__(self, stream: RESTStream[Any], username: str, password: str) -> None:
        """Initialize WMS Basic authenticator.

        Args:
            stream: RESTStream instance (unused in facade)
            username: WMS username
            password: WMS password.

        """
        _ = stream  # Mark as intentionally unused
        logger.debug("Initializing basic authenticator for user: %s", username)
        self.username = username
        self.password = password
        self._auth_headers: dict[str, str] | None = None
        self._auth_lock = threading.RLock()

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        """Apply authentication headers to request.

        Args:
            request: HTTP request to modify
        Returns:
            Modified request with authentication headers.

        """
        with self._auth_lock:
            if not self._auth_headers:
                # Create basic auth header
                credentials = f"{self.username}:{self.password}"
                encoded = base64.b64encode(credentials.encode()).decode()
                self._auth_headers = {"Authorization": f"Basic {encoded}"}
                logger.debug("Basic auth headers created")
            request.headers.update(self._auth_headers)
        return request


def get_wms_authenticator(
    stream: RESTStream[Any],
    config: dict[str, object],
) -> WMSBasicAuthenticator:
    """Get appropriate WMS authenticator based on configuration.

    Args:
        stream: RESTStream instance
        config: Authentication configuration dictionary
    Returns:
        Configured WMS authenticator instance
    Raises:
        ValueError: If authentication configuration is invalid or incomplete.

    """
    username = config.get("username")
    password = config.get("password")
    if not username or not password:
        msg = "Username and password are required for WMS authentication"
        raise ValueError(msg)
    return WMSBasicAuthenticator(stream, cast("str", username), cast("str", password))


def get_wms_headers(config: dict[str, object]) -> dict[str, str]:
    """Get WMS API headers for requests.

    Args:
        config: Configuration dictionary with optional headers
    Returns:
        Dictionary of HTTP headers for WMS API requests.

    """
    headers: dict[str, str] = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "flext-data.taps.flext-data.taps.flext-tap-oracle-wms/1.0",
    }
    # Add any additional headers from config, converting values to strings
    if "headers" in config:
        config_headers = cast("dict[str, Any]", config["headers"])
        for key, value in config_headers.items():
            headers[str(key)] = str(value)
    return headers
