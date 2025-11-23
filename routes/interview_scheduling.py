from fastapi import FastAPI, HTTPException, status, Depends, Query
from fastapi.responses import RedirectResponse, JSONResponse
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from utils.google_calendar import get_google_auth_flow, get_calendar_service
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from datetime import datetime
import pytz
import pickle, os

# app = FastAPI()
router = APIRouter()

# --- OAuth Flow Endpoints ---

@router.get("/auth/google")
async def google_auth():
    """Starts the Google OAuth flow."""
    # flow = get_google_auth_flow('http://127.0.0.1:8000/api/auth/google/callback')
    flow = get_google_auth_flow('https://ai-recruitment-platform-5.onrender.com/api/auth/google/callback')
    auth_url, _ = flow.authorization_url(prompt='consent')
    return RedirectResponse(url=auth_url)

@router.get("/auth/google/callback")
async def google_auth_callback(code: str = None):
    """Handles the callback from Google after user grants permission."""
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code missing")
    # flow = get_google_auth_flow('http://127.0.0.1:8000/api/auth/google/callback')
    flow = get_google_auth_flow('https://ai-recruitment-platform-5.onrender.com/api/auth/google/callback')

    try:
        flow.fetch_token(code=code)
        # global CREDENTIALS_CACHE
        # CREDENTIALS_CACHE = flow.credentials
        TOKEN_FILE = os.path.join(os.path.dirname(__file__), "../token.pickle")
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(flow.credentials, token)
        return JSONResponse(content={"message": "Authentication successful. Credentials stored in cache."}, 
                            status_code=status.HTTP_200_OK)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication failed: {e}")




