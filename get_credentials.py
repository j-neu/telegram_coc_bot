"""Helper to get Google credentials from environment or file."""
import os
import json


def get_google_credentials_path():
    """
    Get path to Google credentials.
    Supports both local file and environment variable (for Railway/Render).

    Returns:
        str: Path to credentials.json file
    """
    # Check if credentials are in environment variable (Railway/Render deployment)
    creds_json = os.getenv('GOOGLE_CREDENTIALS')

    if creds_json:
        # Write credentials from env var to temporary file
        credentials_path = 'credentials.json'
        try:
            # Parse to validate it's valid JSON
            creds_data = json.loads(creds_json)

            # Write to file
            with open(credentials_path, 'w') as f:
                json.dump(creds_data, f)

            return credentials_path
        except json.JSONDecodeError:
            raise ValueError("GOOGLE_CREDENTIALS environment variable contains invalid JSON")

    # Otherwise use local credentials.json file
    credentials_path = 'credentials.json'
    if not os.path.exists(credentials_path):
        raise FileNotFoundError(
            "credentials.json not found. Please either:\n"
            "1. Place credentials.json in the project directory, or\n"
            "2. Set GOOGLE_CREDENTIALS environment variable with the JSON content"
        )

    return credentials_path
