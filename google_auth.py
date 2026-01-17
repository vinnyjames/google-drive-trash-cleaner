# Reusable Google OAuth 2.0 Authentication Module
#
# This module provides a portable authentication helper for Google APIs.
# Copy this file to any project that needs Google OAuth 2.0 authentication.
#
# Usage:
#   from google_auth import GoogleAuth
#
#   auth = GoogleAuth(
#       scopes=['https://www.googleapis.com/auth/drive'],
#       client_secrets_file='client_secrets.json',
#       credentials_file='~/.credentials/my-app.json'
#   )
#   credentials = auth.get_credentials()
#   service = discovery.build('drive', 'v3', credentials=credentials)

import os
import sys

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError


class GoogleAuth:
    """Reusable Google OAuth 2.0 authentication for desktop applications.

    Handles the complete OAuth flow including:
    - Loading existing credentials from file
    - Refreshing expired credentials
    - Running the OAuth flow for new authentication
    - Saving credentials for future use

    Args:
        scopes: List of OAuth scopes to request
        client_secrets_file: Path to OAuth client secrets JSON file
        credentials_file: Path to store/load credential tokens
        app_name: Application name (used in error messages)
    """

    def __init__(
        self,
        scopes: list[str],
        client_secrets_file: str = 'client_secrets.json',
        credentials_file: str = None,
        app_name: str = 'Google API Application'
    ):
        self.scopes = scopes
        self.client_secrets_file = os.path.realpath(client_secrets_file)
        self.app_name = app_name

        # Default credentials location: ~/.credentials/<app-name>.json
        if credentials_file is None:
            safe_name = app_name.lower().replace(' ', '-')
            credentials_file = os.path.join(
                os.path.expanduser('~'), '.credentials', f'{safe_name}.json'
            )
        self.credentials_file = os.path.realpath(os.path.expanduser(credentials_file))

    def get_credentials(
        self,
        use_local_server: bool = True,
        host: str = 'localhost',
        port: int = 8080
    ) -> Credentials:
        """Get valid user credentials, authenticating if necessary.

        If stored credentials exist and are valid, returns them.
        If credentials are expired, attempts to refresh them.
        If no valid credentials exist, runs the OAuth flow.

        Args:
            use_local_server: If True, use local server for OAuth callback.
                              If False, use console-based authentication.
            host: Host for local OAuth server
            port: Port for local OAuth server

        Returns:
            Valid Google OAuth2 Credentials object

        Raises:
            FileNotFoundError: If client_secrets_file doesn't exist
            RefreshError: If credential refresh fails and re-auth is needed
        """
        credentials = self._load_credentials()

        if credentials and credentials.valid:
            return credentials

        if credentials and credentials.expired and credentials.refresh_token:
            credentials = self._refresh_credentials(credentials)
            if credentials:
                self._save_credentials(credentials)
                return credentials

        # Need to run full OAuth flow
        credentials = self._run_oauth_flow(use_local_server, host, port)
        self._save_credentials(credentials)
        return credentials

    def _load_credentials(self) -> Credentials | None:
        """Load credentials from file if it exists."""
        if os.path.exists(self.credentials_file):
            try:
                return Credentials.from_authorized_user_file(
                    self.credentials_file, self.scopes
                )
            except Exception:
                return None
        return None

    def _refresh_credentials(self, credentials: Credentials) -> Credentials | None:
        """Attempt to refresh expired credentials."""
        try:
            credentials.refresh(Request())
            return credentials
        except RefreshError:
            return None

    def _run_oauth_flow(
        self,
        use_local_server: bool,
        host: str,
        port: int
    ) -> Credentials:
        """Run the OAuth flow to get new credentials."""
        if not os.path.exists(self.client_secrets_file):
            raise FileNotFoundError(
                f"Client secrets file not found: {self.client_secrets_file}\n\n"
                f"To use {self.app_name}, you need to create OAuth 2.0 credentials:\n"
                f"1. Go to https://console.cloud.google.com/\n"
                f"2. Create a project and enable the required Google API\n"
                f"3. Create OAuth 2.0 credentials (Desktop app type)\n"
                f"4. Download the JSON file and save it as '{self.client_secrets_file}'"
            )

        flow = InstalledAppFlow.from_client_secrets_file(
            self.client_secrets_file, self.scopes
        )

        if use_local_server:
            credentials = flow.run_local_server(host=host, port=port)
        else:
            credentials = flow.run_console()

        return credentials

    def _save_credentials(self, credentials: Credentials) -> None:
        """Save credentials to file for future use."""
        os.makedirs(os.path.dirname(self.credentials_file), exist_ok=True)
        with open(self.credentials_file, 'w') as f:
            f.write(credentials.to_json())

    def clear_credentials(self) -> bool:
        """Delete stored credentials file.

        Returns:
            True if file was deleted, False if it didn't exist
        """
        if os.path.exists(self.credentials_file):
            os.remove(self.credentials_file)
            return True
        return False
