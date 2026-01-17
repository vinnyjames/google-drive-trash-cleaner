# Authentication Flow

This skill explains how Google OAuth 2.0 authentication works in the Google Drive Trash Cleaner.

## Overview

The cleaner uses **OAuth 2.0 for Desktop Applications** via the reusable [google_auth.py](../../google_auth.py) module. This requires:
1. A `client_secrets.json` file (OAuth client credentials you create)
2. A stored credential token (created after first successful authentication)

## Portable Authentication Module

The authentication logic is extracted into [google_auth.py](../../google_auth.py) for easy reuse in other projects.

### Usage in This Project

```python
from google_auth import GoogleAuth

auth = GoogleAuth(
    scopes=SCOPES,
    client_secrets_file=CLIENT_SECRETS_FILE,
    credentials_file=flags.credfile,
    app_name='Google Drive Trash Cleaner'
)
credentials = auth.get_credentials(
    use_local_server=not flags.noauth_local_webserver,
    host=flags.auth_host_name,
    port=flags.auth_host_port[0]
)
service = discovery.build('drive', 'v3', credentials=credentials)
```

### Porting to Another Project

1. Copy `google_auth.py` to your project
2. Install dependencies: `pip install google-auth google-auth-oauthlib`
3. Use the `GoogleAuth` class:

```python
from google_auth import GoogleAuth

auth = GoogleAuth(
    scopes=['https://www.googleapis.com/auth/gmail.readonly'],
    client_secrets_file='client_secrets.json',
    app_name='My Gmail App'
)
credentials = auth.get_credentials()
```

## Key Files and Locations

| File | Default Location | Purpose |
|------|------------------|---------|
| `client_secrets.json` | Same directory as `cleaner.py` | OAuth client credentials (you create this) |
| Credential token | `~/.credentials/google-drive-trash-cleaner.json` | Stores access/refresh tokens |

Both locations can be customized via command line flags.

## Authentication Flow

The `GoogleAuth.get_credentials()` method handles the complete flow:

### 1. Load Existing Credentials
```python
credentials = Credentials.from_authorized_user_file(credentials_file, scopes)
```

### 2. Refresh If Expired
If credentials exist but are expired, attempt to refresh using the stored refresh token:
```python
credentials.refresh(Request())
```

### 3. New Authentication (If Needed)
If no valid credentials exist, run the OAuth flow:
```python
flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
credentials = flow.run_local_server(host=host, port=port)
```

This opens a browser for the user to authorize the application.

### 4. Save Credentials
After successful authentication, credentials are saved for future use:
```python
with open(credentials_file, 'w') as f:
    f.write(credentials.to_json())
```

## OAuth Scope

The application requests full Google Drive access:
```python
SCOPES = ['https://www.googleapis.com/auth/drive']
```

This scope is required because permanently deleting files needs write access.

## Authentication Flags

| Flag | Description |
|------|-------------|
| `--credfile PATH` | Custom location for credential token file |
| `--noauth_local_webserver` | Use console-based auth instead of browser |
| `--auth_host_name` | Host for local OAuth server (default: localhost) |
| `--auth_host_port` | Ports for local OAuth server (default: 8080, 8090) |

## Error Handling

- **RefreshError**: Caught in `main()` at line 123. If token refresh fails, the user sees "Authentication error" and the flow retries.
- **FileNotFoundError**: Raised by `GoogleAuth` if `client_secrets.json` is missing, with setup instructions.

## Setting Up OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create/select a project
3. Enable the Google Drive API
4. Go to "APIs & Services" > "Credentials"
5. Create OAuth 2.0 credentials (Desktop app type)
6. Download JSON and save as `client_secrets.json`

See [client_secrets.json.template](../../client_secrets.json.template) for the expected format.

## First-Time Authentication

On first run:
1. Browser opens to Google's authorization page
2. User logs in and grants permission
3. Google redirects to local server (localhost:8080)
4. Credentials are captured and saved
5. Subsequent runs use the saved token, refreshing automatically when needed

## Security Notes

- The credential token file contains sensitive data (refresh token)
- It's stored in the user's home directory by default (`~/.credentials/`)
- Users may see "unverified app" warning since they created their own OAuth credentials

## GoogleAuth API Reference

| Method | Description |
|--------|-------------|
| `get_credentials(use_local_server, host, port)` | Get valid credentials, authenticating if needed |
| `clear_credentials()` | Delete stored credentials file |
