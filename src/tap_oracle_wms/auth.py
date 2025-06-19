"""Authentication for Oracle WMS REST API."""

import base64
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import httpx
from singer_sdk.authenticators import OAuthAuthenticator, SimpleAuthenticator


class WMSBasicAuthenticator(SimpleAuthenticator):
    """Basic authentication for Oracle WMS."""

    def __init__(self, stream: Any, username: str, password: str) -> None:
        """Initialize basic authenticator.

        Args:
        ----
            stream: The stream instance
            username: WMS username
            password: WMS password

        """
        self.username = username
        self.password = password
        self._auth_headers = None
        super().__init__(stream)

    @property
    def auth_headers(self) -> dict[str, str]:
        """Get authentication headers.

        Returns
        -------
            Dictionary with Authorization header

        Raises
        ------
            ValueError: If username or password are invalid

        """
        if not self._auth_headers or "Authorization" not in self._auth_headers:
            try:
                if not self.username or not self.password:
                    msg = "Username and password are required for basic auth"
                    raise ValueError(msg)

                credentials = f"{self.username}:{self.password}"
                encoded = base64.b64encode(credentials.encode()).decode()
                self._auth_headers = {"Authorization": f"Basic {encoded}"}
            except (AttributeError, TypeError) as e:
                msg = "Invalid credentials format"
                raise ValueError(msg) from e

        return self._auth_headers

    @auth_headers.setter
    def auth_headers(self, value: dict[str, str]) -> None:
        """Set authentication headers."""
        self._auth_headers = value


class WMSOAuth2Authenticator(OAuthAuthenticator):
    """OAuth2 authentication for Oracle WMS."""

    def __init__(
        self,
        stream: Any,
        auth_endpoint: str,
        oauth_scopes: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
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
        self._auth_endpoint = auth_endpoint
        self._client_id = client_id
        self._client_secret = client_secret
        default_scope = (
            "https://instance.wms.ocs.oraclecloud.com:443/"
            "urn:opc:resource:consumer::all"
        )
        oauth_scopes = oauth_scopes or default_scope

        # Token management
        self._access_token: Optional[str] = None
        self._token_expires: Optional[datetime] = None
        self._refresh_token: Optional[str] = None
        self._auth_headers: dict[str, str] = {}

        super().__init__(stream, auth_endpoint=auth_endpoint, oauth_scopes=oauth_scopes)

    @property
    def oauth_request_body(self) -> dict[str, Any]:
        """Get OAuth2 request body for token endpoint.

        Returns
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

        Returns
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
        """Get valid access token, refreshing if needed.

        Returns
        -------
            Valid access token

        """
        # Check if we have a valid token
        if (
            self._access_token
            and self._token_expires
            and datetime.now(timezone.utc) < self._token_expires
        ):
            return self._access_token

        # Need to get a new token
        self._refresh_access_token()
        return self._access_token

    def _refresh_access_token(self) -> None:
        """Refresh the access token."""
        # Prepare request
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }

        # Make token request
        with httpx.Client() as client:
            response = client.post(
                self._auth_endpoint,
                headers=headers,
                data=self.oauth_request_body,
                timeout=30,
            )
            response.raise_for_status()

            # Parse response
            token_data = response.json()
            self._access_token = token_data["access_token"]

            # Calculate expiration (with 60 second buffer)
            expires_in = token_data.get("expires_in", 3600)
            self._token_expires = datetime.now(timezone.utc) + timedelta(
                seconds=expires_in - 60
            )

            # Store refresh token if provided
            if "refresh_token" in token_data:
                self._refresh_token = token_data["refresh_token"]

    def is_token_valid(self) -> bool:
        """Check if current token is still valid.

        Returns
        -------
            True if token is valid, False otherwise

        """
        if not self._access_token or not self._token_expires:
            return False

        return datetime.now(timezone.utc) < self._token_expires


def get_wms_authenticator(stream: Any, config: dict[str, Any]) -> Any:
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
    """Get required WMS headers.

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

    # Add WMS context headers with defaults
    # Use "*" as default if not provided (tested and confirmed to work)
    company_code = config.get("company_code", "*")
    facility_code = config.get("facility_code", "*")

    headers["X-WMS-Company"] = company_code
    headers["X-WMS-Facility"] = facility_code

    return headers
