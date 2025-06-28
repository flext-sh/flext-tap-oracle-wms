"""Authentication for Oracle WMS REST API."""
from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
import logging
from typing import TYPE_CHECKING, Any

import httpx
from singer_sdk.authenticators import OAuthAuthenticator, SimpleAuthenticator

from .logging_config import (
    get_logger,
    log_exception_context,
    log_function_entry_exit,
    performance_monitor,
)


if TYPE_CHECKING:
    from singer_sdk.streams import RESTStream


# Use enhanced logger with TRACE support
logger = get_logger(__name__)


class WMSBasicAuthenticator(SimpleAuthenticator):
    """Basic authentication for Oracle WMS."""

    @log_function_entry_exit(log_args=False, log_result=False, level=logging.DEBUG)
    @log_exception_context(reraise=True)
    def __init__(self, stream: RESTStream, username: str, password: str) -> None:
        """Initialize basic authenticator.

        Args:
        ----
            stream: The stream instance
            username: WMS username
            password: WMS password

        """
        logger.info("Initializing WMS Basic Authentication")
        logger.debug("Basic auth setup: username=%s",
                     username[:4] + "***" if username else "None")
        logger.trace("Setting up basic auth instance variables")

        self.username = username
        self.password = password
        self._auth_headers: dict[str, str] | None = None

        logger.trace("Calling parent SimpleAuthenticator.__init__")
        super().__init__(stream)
        logger.debug("WMS Basic Authentication initialized successfully")

    @property
    @log_exception_context(reraise=True)
    @performance_monitor("basic_auth_headers")
    def auth_headers(self) -> dict[str, str]:
        """Get authentication headers.

        Returns:
        -------
            Dictionary with Authorization header

        Raises:
        ------
            ValueError: If username or password are invalid

        """
        logger.trace("Getting basic authentication headers")

        if not self._auth_headers or "Authorization" not in self._auth_headers:
            logger.debug("Generating new basic auth headers")
            logger.trace("Validating credentials before encoding")

            try:
                if not self.username or not self.password:
                    error_msg = "Username and password are required for basic auth"
                    logger.error("Basic auth validation failed: %s", error_msg)
                    raise ValueError(error_msg)

                logger.trace("Encoding basic auth credentials")
                credentials = f"{self.username}:{self.password}"
                encoded = base64.b64encode(credentials.encode()).decode()
                self._auth_headers = {"Authorization": f"Basic {encoded}"}

                logger.debug("Basic auth headers generated successfully")
                logger.trace("Auth header created with length: %d", len(encoded))

            except (AttributeError, TypeError) as e:
                error_msg = "Invalid credentials format"
                logger.exception("Basic auth encoding failed: %s", error_msg)
                raise ValueError(error_msg) from e
        else:
            logger.trace("Using cached basic auth headers")

        return self._auth_headers

    @auth_headers.setter
    @log_exception_context(reraise=True)
    def auth_headers(self, value: dict[str, str]) -> None:
        """Set authentication headers."""
        logger.debug("Setting basic auth headers manually")
        logger.trace("Headers being set: %d items", len(value) if value else 0)
        self._auth_headers = value
        logger.trace("Basic auth headers set successfully")


class WMSOAuth2Authenticator(OAuthAuthenticator):
    """OAuth2 authentication for Oracle WMS."""

    @log_function_entry_exit(log_args=False, log_result=False, level=logging.DEBUG)
    @log_exception_context(reraise=True)
    def __init__(
        self,
        stream: RESTStream,
        auth_endpoint: str,
        oauth_scopes: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
    ) -> None:
        """Initialize OAuth2 authenticator.

        Args:
        ----
            stream: The stream instance
            auth_endpoint: OAuth2 token endpoint URL
            oauth_scopes: OAuth2 scopes (space-separated)
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret

        """
        logger.info("Initializing WMS OAuth2 Authentication")
        logger.debug("OAuth2 setup: endpoint=%s, client_id=%s",
                    auth_endpoint, client_id[:8] + "***" if client_id else "None")
        logger.trace("Setting up OAuth2 instance variables")

        self._auth_endpoint = auth_endpoint
        self._client_id = client_id
        self._client_secret = client_secret

        default_scope = (
            "https://instance.wms.ocs.oraclecloud.com:443/"
            "urn:opc:resource:consumer::all"
        )
        oauth_scopes = oauth_scopes or default_scope
        logger.debug("OAuth2 scopes configured: %s", oauth_scopes)

        # Token management
        self._access_token: str | None = None
        self._token_expires: datetime | None = None
        self._refresh_token: str | None = None
        self._auth_headers: dict[str, str] = {}
        logger.trace("OAuth2 token management variables initialized")

        logger.trace("Calling parent OAuthAuthenticator.__init__")
        super().__init__(stream, auth_endpoint=auth_endpoint, oauth_scopes=oauth_scopes)
        logger.debug("WMS OAuth2 Authentication initialized successfully")

    @property
    @log_exception_context(reraise=True)
    def oauth_request_body(self) -> dict[str, Any]:
        """Get OAuth2 request body for token endpoint.

        Returns:
        -------
            Dictionary with OAuth2 parameters

        """
        logger.trace("Building OAuth2 request body")

        request_body = {
            "grant_type": "client_credentials",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "scope": self.oauth_scopes,
        }

        logger.debug("OAuth2 request body built: grant_type=%s, scope=%s",
                    request_body["grant_type"], request_body["scope"])
        logger.trace("OAuth2 request body has %d parameters", len(request_body))

        return request_body

    @property
    @log_exception_context(reraise=True)
    @performance_monitor("oauth2_auth_headers")
    def auth_headers(self) -> dict[str, str]:
        """Get authentication headers.

        Returns:
        -------
            Dictionary with Authorization header

        """
        logger.trace("Getting OAuth2 authentication headers")

        if not self._auth_headers or "Authorization" not in self._auth_headers:
            logger.debug("Generating new OAuth2 auth headers")
            logger.trace("Obtaining access token for auth headers")

            token = self._get_access_token()
            self._auth_headers = {"Authorization": f"Bearer {token}"}

            logger.debug("OAuth2 auth headers generated successfully")
            logger.trace("Bearer token created with length: %d", len(token))
        else:
            logger.trace("Using cached OAuth2 auth headers")

        return self._auth_headers

    @auth_headers.setter
    @log_exception_context(reraise=True)
    def auth_headers(self, value: dict[str, str]) -> None:
        """Set authentication headers.

        Args:
        ----
            value: Dictionary of headers to set

        """
        logger.debug("Setting OAuth2 auth headers manually")
        logger.trace("Headers being set: %d items", len(value) if value else 0)
        self._auth_headers = value
        logger.trace("OAuth2 auth headers set successfully")

    @log_exception_context(reraise=True)
    @performance_monitor("oauth2_get_access_token")
    def _get_access_token(self) -> str:
        """Get valid access token, refreshing if needed.

        Returns:
        -------
            Valid access token

        """
        logger.trace("Getting OAuth2 access token")

        # Check if we have a valid token
        if (
            self._access_token
            and self._token_expires
            and datetime.now(timezone.utc) < self._token_expires
        ):
            logger.debug("Using cached access token (still valid)")
            time_remaining = self._token_expires - datetime.now(timezone.utc)
            logger.trace("Token expires in: %s seconds", time_remaining.total_seconds())
            return self._access_token

        logger.debug("Access token expired or missing, refreshing")
        logger.trace("Current token state: token_exists=%s, expires=%s",
                    bool(self._access_token), self._token_expires)

        # Need to get a new token
        self._refresh_access_token()
        if not self._access_token:
            error_msg = "Failed to obtain access token"
            logger.error("Token refresh failed: %s", error_msg)
            raise ValueError(error_msg)

        logger.debug("Access token refreshed successfully")
        return self._access_token

    @log_exception_context(reraise=True)
    @performance_monitor("oauth2_refresh_token")
    def _refresh_access_token(self) -> None:
        """Refresh the access token."""
        logger.info("Starting OAuth2 access token refresh process")
        logger.debug("Refreshing OAuth2 access token")
        logger.trace("Token refresh entry point reached")
        logger.trace("Current token state before refresh: expired or missing")
        logger.trace("Preparing token refresh request")

        # Prepare request
        logger.trace("Building token request headers")
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }
        logger.debug("Token request headers prepared: %d items", len(headers))
        logger.trace("Headers configured: %s", list(headers.keys()))

        # Make token request
        logger.trace("Validating auth endpoint configuration")
        if not self._auth_endpoint:
            error_msg = "Auth endpoint not configured"
            logger.critical("Critical OAuth2 error: missing auth endpoint")
            logger.error("Token refresh failed: %s", error_msg)
            logger.trace("Auth endpoint validation failed")
            raise ValueError(error_msg)

        logger.debug("Making token request to: %s", self._auth_endpoint)
        logger.trace("Auth endpoint validated successfully")
        logger.trace("Starting HTTP client for token request")

        try:
            logger.trace("Creating HTTP client instance")
            with httpx.Client() as client:
                logger.trace("HTTP client created, preparing POST request")
                logger.trace("Request body preparation starting")
                request_body = self.oauth_request_body
                logger.trace(
                    "Request body prepared with %d parameters", len(request_body),
                )

                logger.debug("Sending POST request to token endpoint")
                logger.trace("Sending POST request to token endpoint")
                response = client.post(
                    self._auth_endpoint,
                    headers=headers,
                    data=request_body,
                    timeout=30,
                )

                logger.debug("Token request response: status=%d", response.status_code)
                logger.trace("Response received from token endpoint")
                logger.trace("Response status: %d %s", response.status_code,
                           getattr(response, "reason_phrase", "Unknown"))
                logger.trace("Response headers: %d items", len(response.headers))

                response.raise_for_status()
                logger.trace("Response status validation passed")

                # Parse response
                logger.debug("Parsing token response")
                logger.trace("Parsing token response JSON")
                token_data = response.json()
                logger.trace("Token response keys: %s", list(token_data.keys()))

                logger.trace("Extracting access token from response")
                self._access_token = token_data["access_token"]

                logger.debug("Access token extracted from response")
                logger.trace("Token length: %d characters", len(self._access_token))
                token_prefix = (
                    self._access_token[:8] if self._access_token else "None"
                )
                logger.trace("Token prefix: %s***", token_prefix)

                # Calculate expiration (with 60 second buffer)
                logger.trace("Calculating token expiration time")
                expires_in = token_data.get("expires_in", 3600)
                logger.trace("Token expires in: %d seconds (raw)", expires_in)

                self._token_expires = datetime.now(timezone.utc) + timedelta(
                    seconds=expires_in - 60,
                )

                logger.debug("Token expiration calculated: expires_in=%d seconds",
                            expires_in)
                logger.trace("Token expires at: %s", self._token_expires)
                logger.trace("Expiration buffer applied: 60 seconds")

                # Store refresh token if provided
                logger.trace("Checking for refresh token in response")
                if "refresh_token" in token_data:
                    logger.trace("Refresh token found in response")
                    self._refresh_token = token_data["refresh_token"]
                    logger.debug("Refresh token stored")
                    logger.trace("Refresh token length: %d characters",
                                len(self._refresh_token))
                    refresh_prefix = (
                        self._refresh_token[:8] if self._refresh_token else "None"
                    )
                    logger.trace("Refresh token prefix: %s***", refresh_prefix)
                else:
                    logger.trace("No refresh token provided in response")
                    logger.trace("Refresh token not available for future use")

                logger.info("OAuth2 token refresh completed successfully")
                logger.debug("Token refresh process finished")
                logger.trace("Token refresh success - new token active")

        except httpx.HTTPStatusError as e:
            logger.critical(
                "Critical OAuth2 error: HTTP status error during token refresh",
            )
            logger.exception(
                "HTTP error during token refresh: %d %s",
                e.response.status_code,
                e.response.reason_phrase,
            )
            logger.trace("HTTP status error details: %s", str(e))
            response_content = (
                e.response.text[:500] if hasattr(e, "response") else "N/A"
            )
            logger.trace("Response content: %s", response_content)
            raise
        except Exception as e:
            logger.critical(
                "Critical OAuth2 error: unexpected error during token refresh",
            )
            logger.exception("Unexpected error during token refresh")
            logger.trace("Exception type: %s", type(e).__name__)
            logger.trace("Exception details: %s", str(e))
            raise

    def _validate_auth_endpoint(self) -> None:
        """Validate auth endpoint configuration."""
        logger.trace("Validating auth endpoint configuration")
        if not self._auth_endpoint:
            error_msg = "Auth endpoint not configured"
            logger.critical("Critical OAuth2 error: missing auth endpoint")
            logger.error("Token refresh failed: %s", error_msg)
            logger.trace("Auth endpoint validation failed")
            raise ValueError(error_msg)
        logger.trace("Auth endpoint validated successfully")

    def _process_token_response(self, token_data: dict[str, Any]) -> None:
        """Process token response and store tokens."""
        logger.trace("Extracting access token from response")
        self._access_token = token_data["access_token"]
        logger.debug("Access token extracted from response")
        logger.trace("Token length: %d characters", len(self._access_token))

        token_prefix = self._access_token[:8] if self._access_token else "None"
        logger.trace("Token prefix: %s***", token_prefix)

        # Calculate expiration (with 60 second buffer)
        logger.trace("Calculating token expiration time")
        expires_in = token_data.get("expires_in", 3600)
        logger.trace("Token expires in: %d seconds (raw)", expires_in)

        self._token_expires = datetime.now(timezone.utc) + timedelta(
            seconds=expires_in - 60,
        )
        logger.debug("Token expiration calculated: expires_in=%d seconds", expires_in)
        logger.trace("Token expires at: %s", self._token_expires)
        logger.trace("Expiration buffer applied: 60 seconds")

        # Store refresh token if provided
        self._store_refresh_token(token_data)

    def _store_refresh_token(self, token_data: dict[str, Any]) -> None:
        """Store refresh token if provided in response."""
        logger.trace("Checking for refresh token in response")
        if "refresh_token" in token_data:
            logger.trace("Refresh token found in response")
            self._refresh_token = token_data["refresh_token"]
            logger.debug("Refresh token stored")
            logger.trace("Refresh token length: %d characters", len(self._refresh_token))

            refresh_prefix = self._refresh_token[:8] if self._refresh_token else "None"
            logger.trace("Refresh token prefix: %s***", refresh_prefix)
        else:
            logger.trace("No refresh token provided in response")
            logger.trace("Refresh token not available for future use")

    @log_exception_context(reraise=True)
    def is_token_valid(self) -> bool:
        """Check if current token is still valid.

        Returns:
        -------
            True if token is valid, False otherwise

        """
        logger.trace("Checking OAuth2 token validity")

        if not self._access_token or not self._token_expires:
            logger.debug("Token invalid: missing token or expiration")
            logger.trace("Token state: has_token=%s, has_expiry=%s",
                        bool(self._access_token), bool(self._token_expires))
            return False

        is_valid = datetime.now(timezone.utc) < self._token_expires
        time_remaining = self._token_expires - datetime.now(timezone.utc)

        logger.debug("Token validity check: valid=%s, remaining=%s seconds",
                    is_valid, time_remaining.total_seconds())
        logger.trace("Token expires at: %s", self._token_expires)

        return is_valid


@log_function_entry_exit(log_args=False, log_result=True, level=logging.DEBUG)
@log_exception_context(reraise=True)
@performance_monitor("wms_authenticator_creation")
def get_wms_authenticator(
    stream: RESTStream, config: dict[str, Any],
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
    logger.info("Creating WMS authenticator: method=%s", auth_method)
    logger.debug("Authenticator config validation starting")
    logger.trace("Available auth methods: basic, oauth2")

    if auth_method == "basic":
        logger.debug("Setting up basic authentication")
        logger.trace("Validating basic auth credentials")

        username = config.get("username")
        password = config.get("password")

        if not username or not password:
            error_msg = "Basic authentication requires username and password"
            logger.error("Basic auth validation failed: %s", error_msg)
            raise ValueError(error_msg)

        logger.debug("Basic auth credentials validated, creating authenticator")
        logger.trace("Creating WMSBasicAuthenticator instance")
        authenticator = WMSBasicAuthenticator(stream, username, password)
        logger.info("Basic authenticator created successfully")
        return authenticator

    if auth_method == "oauth2":
        logger.debug("Setting up OAuth2 authentication")
        logger.trace("Validating OAuth2 credentials")

        client_id = config.get("oauth_client_id")
        client_secret = config.get("oauth_client_secret")
        token_url = config.get("oauth_token_url")
        scopes = config.get("oauth_scope", "wms.read")

        logger.debug("OAuth2 params: client_id=%s, token_url=%s, scopes=%s",
                    client_id[:8] + "***" if client_id else "None",
                    token_url, scopes)

        if not all([client_id, client_secret, token_url]):
            error_msg = "OAuth2 auth requires client_id, client_secret, token_url"
            logger.error("OAuth2 validation failed: %s", error_msg)
            raise ValueError(error_msg)

        # Ensure token_url is a string (mypy satisfaction)
        if not isinstance(token_url, str):
            error_msg = "OAuth token URL must be a string"
            logger.error("OAuth2 token URL validation failed: %s", error_msg)
            raise ValueError(error_msg)

        logger.debug("OAuth2 credentials validated, creating authenticator")
        logger.trace("Creating WMSOAuth2Authenticator instance")
        authenticator = WMSOAuth2Authenticator(
            stream,
            auth_endpoint=token_url,
            client_id=client_id,
            client_secret=client_secret,
            oauth_scopes=scopes,
        )
        logger.info("OAuth2 authenticator created successfully")
        return authenticator

    error_msg = f"Unknown authentication method: {auth_method}"
    logger.error("Authentication method validation failed: %s", error_msg)
    raise ValueError(error_msg)


@log_function_entry_exit(log_args=False, log_result=True, level=logging.DEBUG)
@log_exception_context(reraise=True)
@performance_monitor("wms_headers_creation")
def get_wms_headers(config: dict[str, Any]) -> dict[str, str]:
    """Get required WMS headers.

    Args:
    ----
        config: Configuration dictionary

    Returns:
    -------
        Dictionary of headers

    """
    logger.debug("Creating WMS headers")
    logger.trace("Setting up standard HTTP headers")

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "tap-oracle-wms/0.1.0",
    }
    logger.trace("Standard headers set: %d items", len(headers))

    # Add WMS context headers with defaults
    # Use "*" as default if not provided (tested and confirmed to work)
    company_code = config.get("company_code", "*")
    facility_code = config.get("facility_code", "*")

    logger.debug("WMS context: company=%s, facility=%s", company_code, facility_code)
    logger.trace("Adding WMS-specific context headers")

    headers["X-WMS-Company"] = company_code
    headers["X-WMS-Facility"] = facility_code

    logger.debug(
        "WMS headers created successfully: %d total headers", len(headers),
    )
    logger.trace("Final headers: %s", list(headers.keys()))

    return headers
