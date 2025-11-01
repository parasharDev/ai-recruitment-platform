from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from utils.google_calendar import get_google_auth_flow, get_calendar_service
from fastapi import APIRouter, HTTPException

# app = FastAPI()
router = APIRouter()

# --- OAuth Flow Endpoints ---

@router.get("/auth/google")
async def google_auth():
    """Starts the Google OAuth flow."""
    flow = get_google_auth_flow('http://127.0.0.1:8000/api/auth/google/callback')
    auth_url, _ = flow.authorization_url(prompt='consent')
    return RedirectResponse(url=auth_url)

@router.get("/auth/google/callback")
async def google_auth_callback(code: str = None):
    """Handles the callback from Google after user grants permission."""
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code missing")

    flow = get_google_auth_flow('http://127.0.0.1:8000/api/auth/google/callback')
    
    try:
        # Use a dummy request to exchange the code for credentials
        flow.fetch_token(code=code)
        
        # In a real app, you would save flow.credentials (access_token, refresh_token, etc.) 
        # to a secure database associated with the interviewer's user account.
        
        # For this example, we'll store it simply (NOT SECURE FOR PRODUCTION)
        # You'll need a proper database for real-world applications.
        global CREDENTIALS_CACHE
        CREDENTIALS_CACHE = flow.credentials
        
        return JSONResponse(content={"message": "Authentication successful. Credentials stored in cache."}, 
                            status_code=status.HTTP_200_OK)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication failed: {e}")

# --- Event Scheduling Endpoint ---

# Placeholder for credentials (Replace with proper database lookup in production)
CREDENTIALS_CACHE: Credentials = None 

def get_current_service():
    """Dependency to get the authenticated Google Calendar Service."""
    if not CREDENTIALS_CACHE:
        raise HTTPException(status_code=401, detail="Authentication required. Please authenticate via /auth/google.")
    
    # Optional: Logic to refresh token if it's expired
    if CREDENTIALS_CACHE.expired and CREDENTIALS_CACHE.refresh_token:
        CREDENTIALS_CACHE.refresh(Request())
        
    return get_calendar_service(CREDENTIALS_CACHE)


@router.post("/schedule/interview")
async def schedule_interview(
    interviewer_calendar_id: str, # Usually 'primary' or the interviewer's email
    candidate_email: str,
    start_time: str,  # e.g., "2025-12-30T10:00:00"
    end_time: str,    # e.g., "2025-12-30T11:00:00"
    service=Depends(get_current_service)
):
    """Creates a Google Calendar Event with a Google Meet link."""
    
    event = {
        'summary': 'Technical Interview - FastAPI Project',
        'location': 'Virtual Meeting',
        'description': 'Technical Interview with the candidate for the open role.',
        'start': {
            'dateTime': start_time,
            'timeZone': 'Asia/Kolkata', # Use the correct timezone
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'Asia/Kolkata',
        },
        'attendees': [
            {'email': interviewer_calendar_id},
            {'email': candidate_email},
        ],
        # **This is the key to creating the Google Meet link**
        'conferenceData': {
            'createRequest': {
                'requestId': 'fastapi-meet-interview-123', # Unique ID for the creation request
                'conferenceSolutionKey': {
                    'type': 'hangoutsMeet'
                }
            },
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }

    try:
        # Insert the event into the specified calendar
        created_event = service.events().insert(
            calendarId=interviewer_calendar_id, 
            body=event,
            # This parameter ensures the conference data (Google Meet link) is processed
            conferenceDataVersion=1, 
            sendNotifications=True # Sends email invites to attendees
        ).execute()

        meet_link = created_event['conferenceData']['entryPoints'][0]['uri']
        
        return {
            "message": "Interview scheduled successfully!",
            "event_id": created_event['id'],
            "google_meet_link": meet_link,
            "html_link": created_event['htmlLink']
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create event: {e}")