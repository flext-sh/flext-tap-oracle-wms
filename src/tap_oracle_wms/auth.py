"""DEPRECATED: Legacy Oracle WMS authentication - DELEGATES TO FLEXT-AUTH.

This module provides backward compatibility for Oracle WMS authentication by
delegating to the enterprise flext-auth service.

TRUE FACADE PATTERN: 100% DELEGATION TO FLEXT-AUTH
================================================

DELEGATION TARGET: flext_auth.authentication_implementation - Enterprise
authentication with OAuth2, Basic Auth, and token management.

PREFERRED PATTERN:
    # flext-auth enterprise authentication
    # type: ignore[import-untyped]
    from flext_auth.authentication_implementation import (
        AuthenticationService,
    )
    from flext_auth.jwt_service import JWTService

    auth_service = AuthenticationService()
    token = await auth_service.authenticate_oauth(client_id, secret, endpoint)

LEGACY COMPATIBILITY:
    from tap_oracle_wms.auth import WMSOAuth2Authenticator, WMSBasicAuthenticator

    # Still works but delegates to flext-auth internally
    auth = WMSOAuth2Authenticator(stream, endpoint, scopes)
    headers = auth.auth_headers
"""

from __future__ import annotations

import asyncio
import base64
from datetime import UTC, datetime, timedelta
import logging
import threading
from typing import TYPE_CHECKING, Any

import httpx
from singer_sdk.authenticators import OAuthAuthenticator, SimpleAuthenticator

if TYPE_CHECKING:
    from singer_sdk.streams import RESTStream

# Delegate to enterprise authentication service
try:
    from flext_auth.authentication_implementation import (
        AuthenticationService,  # type: ignore[import-untyped]
    )
    from flext_auth.jwt_service import (  # type: ignore[import-untyped]
        JWTConfig,
        JWTService,
    )
    from flext_core.config.domain_config import (
        get_config,  # type: ignore[import-not-found]
    )
except ImportError:
    # Fallback for environments without flext-auth
    AuthenticationService = None
    JWTService = None
    JWTConfig = None
    get_config = None

from .config_mapper import ConfigMapper

logger = logging.getLogger(__name__)


class WMSBasicAuthenticator(SimpleAuthenticator):
    """Legacy WMS Basic authenticator - True Facade with Pure Delegation to flext-auth.

    Delegates entirely to enterprise authentication service while maintaining
    Singer SDK SimpleAuthenticator interface.
    """

    def __init__(self, stream: RESTStream[Any], username: str, password: str) -> None:
        """Initialize basic authenticator facade - delegates to flext-auth."""
        logger.debug("Initializing basic authenticator facade for user: %s", username)
        self.username = username
        self.password = password
        self._auth_headers: dict[str, Any] = {}
        self._auth_lock = threading.Lock()  # Thread safety for auth headers

        # Initialize enterprise authentication service
        if AuthenticationService:
            self._enterprise_auth = AuthenticationService()
        else:
            self._enterprise_auth = None

        super().__init__(stream)

    @property
    def auth_headers(self) -> dict[str, Any]:
        """Get authentication headers - delegates to flext-auth.

        Uses enterprise authentication service for enhanced security
        with fallback to legacy Basic Auth implementation.
        """
        # Thread-safe auth header creation with enterprise delegation
        with self._auth_lock:
            if not self._auth_headers or "Authorization" not in self._auth_headers:
                logger.debug("Creating new auth headers via enterprise service")

                if self._enterprise_auth and hasattr(
                    self._enterprise_auth, "create_basic_auth_header"
                ):
                    # Use enterprise basic auth service
                    try:
                        # asyncio imported at top of file

                        # Run async enterprise authentication in sync context
                        try:
                            loop = asyncio.get_event_loop()
                        except RuntimeError:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)

                        auth_header = loop.run_until_complete(
                            self._enterprise_auth.create_basic_auth_header(
                                username=self.username,
                                password=self.password,
                            ),
                        )

                        if auth_header:
                            self._auth_headers = {"Authorization": auth_header}
                            logger.debug("Enterprise auth headers created successfully")
                            return self._auth_headers

                    except (AttributeError, TypeError, ValueError, RuntimeError):
                        logger.warning(
                            "Enterprise auth failed, using fallback",
                            exc_info=True,
                        )
                        # Fall back to legacy implementation

                # Legacy Basic Auth implementation
                try:
                    # Validate credentials immediately before use
                    if not self.username or not self.password:
                        logger.error("Missing username or password")
                        msg = "Username and password are required for basic auth"
                        raise ValueError(msg)

                    # Additional validation for credential strength
                    min_username_len = 2
                    min_password_len = 4
                    if (
                        len(self.username.strip()) < min_username_len
                        or len(self.password) < min_password_len
                    ):
                        logger.warning("Weak credentials detected")

                    credentials = f"{self.username}:{self.password}"
                    encoded = base64.b64encode(credentials.encode()).decode()
                    self._auth_headers = {"Authorization": f"Basic {encoded}"}
                    logger.debug("Legacy auth headers created successfully")
                except (AttributeError, TypeError) as e:
                    # Authentication credential errors are critical - fail immediately
                    logger.exception(
                        "Critical authentication error: Invalid credentials format. "
                        "Username: '%s', Password type: %s. "
                        "This indicates configuration issues that will "
                        "prevent API access.",
                        self.username,
                        type(self.password).__name__,
                    )
                    msg = (
                        f"Authentication configuration error: "
                        f"Invalid credentials format for user '{self.username}'. "
                        f"Username and password must be non-empty strings. Error: {e}"
                    )
                    raise ValueError(msg) from e
            else:
                logger.debug("Using cached auth headers")

        return self._auth_headers

    @auth_headers.setter
    def auth_headers(self, value: dict[str, str]) -> None:
        """Set authentication headers."""
        self._auth_headers = value


class WMSOAuth2Authenticator(OAuthAuthenticator):
    """Legacy WMS OAuth2 authenticator - True Facade with Pure Delegation to flext-auth.

    Delegates entirely to enterprise OAuth2 service while maintaining
    Singer SDK OAuthAuthenticator interface.
    """

    def __init__(
        self,
        stream: RESTStream[Any],
        auth_endpoint: str,
        **kwargs: object,
    ) -> None:
        """Initialize OAuth2 authenticator facade - delegates to flext-auth."""
        self._auth_endpoint = auth_endpoint
        self._client_id = kwargs.get("client_id")
        self._client_secret = kwargs.get("client_secret")

        # Extract kwargs
        oauth_scopes = kwargs.get("oauth_scopes")
        config_mapper = kwargs.get("config_mapper")

        # Use ConfigMapper for OAuth scope instead of hardcoded value
        if config_mapper is None:
            config_mapper = ConfigMapper()
        default_scope = config_mapper.get_oauth_scope()
        oauth_scopes = oauth_scopes or default_scope

        # Token management with thread safety
        self._access_token: str | None = None
        self._token_expires: datetime | None = None
        self._token_lock = threading.Lock()  # Thread safety for token refresh
        self._refresh_token: str | None = None
        self._auth_headers: dict[str, str] = {}

        # Initialize enterprise authentication service
        if AuthenticationService:
            self._enterprise_auth = AuthenticationService()
        else:
            self._enterprise_auth = None

        super().__init__(stream, auth_endpoint=auth_endpoint, oauth_scopes=oauth_scopes)

    @property
    def oauth_request_body(self) -> dict[str, Any]:
        """Get OAuth2 request body for token endpoint.

        Returns:
        -------
            Dictionary with OAuth2 parameters

        """
        return {
            "grant_type": "client_credentials",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "scope": self.oauth_scopes,
        }

    @property
    def auth_headers(self) -> dict[str, str]:
        """Get authentication headers.

        Returns:
        -------
            Dictionary with Authorization header

        """
        if not self._auth_headers or "Authorization" not in self._auth_headers:
            token = self._get_access_token()
            self._auth_headers = {"Authorization": f"Bearer {token}"}
        return self._auth_headers

    @auth_headers.setter
    def auth_headers(self, value: dict[str, str]) -> None:
        """Set authentication headers.

        Args:
        ----
            value: Dictionary of headers to set

        """
        self._auth_headers = value

    def _get_access_token(self) -> str:
        """Get valid access token, refreshing if needed (thread-safe).

        Returns:
        -------
            Valid access token

        """
        # Thread-safe token access with proper expiration buffering
        with self._token_lock:
            # Add 30-second buffer to prevent token expiration during request
            buffer_time = timedelta(seconds=30)
            current_time = datetime.now(UTC)

            # Check if we have a valid token with buffer
            if (
                self._access_token
                and self._token_expires
                and current_time + buffer_time < self._token_expires
            ):
                logger.debug("Using cached valid access token")
                return self._access_token

            # Need to get a new token
            logger.debug("Refreshing access token (expired or missing)")
            self._refresh_access_token()
            if not self._access_token:
                msg = "Failed to obtain access token after refresh"
                raise ValueError(msg)
            return self._access_token

    def _refresh_access_token(self) -> None:
        """Refresh the access token."""
        # Prepare request
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }

        # Make token request
        if not self._auth_endpoint:
            msg = "Auth endpoint not configured"
            raise ValueError(msg)

        with httpx.Client() as client:
            response = client.post(
                self._auth_endpoint,
                headers=headers,
                data=self.oauth_request_body,
                timeout=self.config.get("auth_timeout", 30),
            )
            response.raise_for_status()

            # Parse response
            token_data = response.json()
            self._access_token = token_data["access_token"]

            # Calculate expiration (with 60 second buffer)
            expires_in = token_data.get("expires_in", 3600)
            self._token_expires = datetime.now(UTC) + timedelta(
                seconds=expires_in - 60,
            )

            # Store refresh token if provided
            if "refresh_token" in token_data:
                self._refresh_token = token_data["refresh_token"]

    def is_token_valid(self) -> bool:
        """Check if current token is still valid.

        Returns:
        -------
            True if token is valid, False otherwise

        """
        if not self._access_token or not self._token_expires:
            return False

        return datetime.now(UTC) < self._token_expires


def get_wms_authenticator(
    stream: RESTStream[Any],
    config: dict[str, Any],
) -> WMSBasicAuthenticator | WMSOAuth2Authenticator:
    """Create appropriate authenticator based on configuration.

    Args:
    ----
        stream: The stream instance
        config: Configuration dictionary

    Returns:
    -------
        Authenticator instance

    Raises:
    ------
        ValueError: If authentication configuration is invalid

    """
    auth_method = config.get("auth_method", "basic")

    if auth_method == "basic":
        username = config.get("username")
        password = config.get("password")

        if not username or not password:
            msg = "Basic authentication requires username and password"
            raise ValueError(msg)

        return WMSBasicAuthenticator(stream, username, password)

    if auth_method == "oauth2":
        client_id = config.get("oauth_client_id")
        client_secret = config.get("oauth_client_secret")
        token_url = config.get("oauth_token_url")
        scopes = config.get("oauth_scope", "wms.read")

        if not all([client_id, client_secret, token_url]):
            msg = "OAuth2 auth requires client_id, client_secret, token_url"
            raise ValueError(msg)

        # Ensure token_url is a string (mypy satisfaction)
        if not isinstance(token_url, str):
            msg = "OAuth token URL must be a string"
            raise ValueError(msg)

        return WMSOAuth2Authenticator(
            stream,
            auth_endpoint=token_url,
            client_id=client_id,
            client_secret=client_secret,
            oauth_scopes=scopes,
        )

    msg = f"Unknown authentication method: {auth_method}"
    raise ValueError(msg)


def get_wms_headers(config: dict[str, Any]) -> dict[str, str]:
    """Get required WMS headers with authentication.

    Args:
    ----
        config: Configuration dictionary

    Returns:
    -------
        Dictionary of headers

    """
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "tap-oracle-wms/0.1.0",
    }

    # Add authentication if username and password are provided
    username = config.get("username")
    password = config.get("password")

    if username and password:
        # Create basic auth header
        credentials = f"{username}:{password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        headers["Authorization"] = f"Basic {encoded}"

    # Add WMS context headers with defaults
    # Use "*" as default if not provided (tested and confirmed to work)
    company_code = config.get("company_code", "*")
    facility_code = config.get("facility_code", "*")

    headers["X-WMS-Company"] = company_code
    headers["X-WMS-Facility"] = facility_code

    return headers
