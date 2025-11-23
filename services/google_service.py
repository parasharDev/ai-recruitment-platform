from utils.google_calendar import get_calendar_service
from google.oauth2.credentials import Credentials
import pickle
import os

TOKEN_FILE = os.path.join(os.path.dirname(__file__), "../token.pickle")

def get_current_service():
    """Returns authenticated Google Calendar API service if token exists."""
    if not os.path.exists(TOKEN_FILE):
        return None

    with open(TOKEN_FILE, "rb") as token:
        credentials = pickle.load(token)

    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

    return get_calendar_service(credentials)
