import os
import pickle
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build



# Define scopes (should match what you configured in Step 1)
SCOPES = ['https://www.googleapis.com/auth/calendar','https://www.googleapis.com/auth/calendar.events']
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), 'credentials.json')

def get_google_auth_flow(redirect_uri: str) -> Flow:
    """Initializes and returns the OAuth flow."""
    return Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )

def get_calendar_service(credentials):
    """Builds and returns the Google Calendar API service."""
    return build('calendar', 'v3', credentials=credentials)