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


# Placeholder for credentials 

CREDENTIALS_CACHE: Credentials = None 

# def get_current_service():
#     """Dependency to get the authenticated Google Calendar Service."""
#     if not CREDENTIALS_CACHE:
#         raise HTTPException(status_code=401, detail="Authentication required. Please authenticate via /auth/google.")
    
#     # Optional: Logic to refresh token if it's expired
#     if CREDENTIALS_CACHE.expired and CREDENTIALS_CACHE.refresh_token:
#         CREDENTIALS_CACHE.refresh(Request())
        
#     return get_calendar_service(CREDENTIALS_CACHE)


# @router.post("/schedule/interview")
# async def schedule_interview(
#     interviewer_calendar_id: str, # Usually 'primary' or the interviewer's email
#     candidate_email: str,
#     start_time: str,  # e.g., "2025-12-30T10:00:00"
#     end_time: str,    # e.g., "2025-12-30T11:00:00"
#     service=Depends(get_current_service)
# ):
#     """Creates a Google Calendar Event with a Google Meet link."""
    
#     event = {
#         'summary': 'Technical Interview - FastAPI Project',
#         'location': 'Virtual Meeting',
#         'description': 'Technical Interview with the candidate for the open role.',
#         'start': {
#             'dateTime': start_time,
#             'timeZone': 'Asia/Kolkata', # Use the correct timezone
#         },
#         'end': {
#             'dateTime': end_time,
#             'timeZone': 'Asia/Kolkata',
#         },
#         'attendees': [
#             {'email': interviewer_calendar_id},
#             {'email': candidate_email},
#         ],
#         # **This is the key to creating the Google Meet link**
#         'conferenceData': {
#             'createRequest': {
#                 'requestId': 'fastapi-meet-interview-123', # Unique ID for the creation request
#                 'conferenceSolutionKey': {
#                     'type': 'hangoutsMeet'
#                 }
#             },
#         },
#         'reminders': {
#             'useDefault': False,
#             'overrides': [
#                 {'method': 'email', 'minutes': 30},
#                 {'method': 'popup', 'minutes': 10},
#             ],
#         },
#     }

#     try:
#         # Insert the event into the specified calendar
#         created_event = service.events().insert(
#             calendarId=interviewer_calendar_id, 
#             body=event,
#             # This parameter ensures the conference data (Google Meet link) is processed
#             conferenceDataVersion=1, 
#             sendNotifications=True # Sends email invites to attendees
#         ).execute()

#         meet_link = created_event['conferenceData']['entryPoints'][0]['uri']
        
#         return {
#             "message": "Interview scheduled successfully!",
#             "event_id": created_event['id'],
#             "google_meet_link": meet_link,
#             "html_link": created_event['htmlLink']
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to create event: {e}")
    


# @router.get("/free-slots")
# async def get_free_slots(
#     interviewer_calendar_id: str = Query(..., description="Calendar ID or 'primary'"),
#     start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
#     end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
#     service=Depends(get_current_service)
# ):
#     """
#     Fetch free 1-hour slots between start_date and end_date
#     excluding any busy events in Google Calendar.
#     """

#     try:
#         tz = pytz.timezone("Asia/Kolkata")
#         start_dt = tz.localize(datetime.strptime(start_date, "%Y-%m-%d"))
#         end_dt = tz.localize(datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1))  # include full day

#         # Step 1: Query busy times from Google Calendar
#         freebusy_query = {
#             "timeMin": start_dt.isoformat(),
#             "timeMax": end_dt.isoformat(),
#             "timeZone": "Asia/Kolkata",
#             "items": [{"id": interviewer_calendar_id}]
#         }

#         response = service.freebusy().query(body=freebusy_query).execute()
#         busy_times = response['calendars'][interviewer_calendar_id].get('busy', [])

#         # Step 2: Define working hours (customize if needed)
#         work_start = 9   # 9 AM
#         work_end = 17    # 5 PM
#         slot_duration = timedelta(hours=1)

#         # Step 3: Generate potential 1-hour slots
#         available_slots = []
#         current = tz.localize(datetime.strptime(start_date, "%Y-%m-%d").replace(hour=work_start))
#         day_end = tz.localize(datetime.strptime(start_date, "%Y-%m-%d").replace(hour=work_end))

#         while current + slot_duration <= day_end:
#             slot_start = current
#             slot_end = current + slot_duration

#             # Step 4: Check overlap with busy events
#             overlap = False
#             for busy in busy_times:
#                 busy_start = datetime.fromisoformat(busy['start'])
#                 busy_end = datetime.fromisoformat(busy['end'])
#                 if slot_start < busy_end and slot_end > busy_start:
#                     overlap = True
#                     break

#             if not overlap:
#                 available_slots.append({
#                     "start": slot_start.strftime("%Y-%m-%dT%H:%M:%S"),
#                     "end": slot_end.strftime("%Y-%m-%dT%H:%M:%S")
#                 })

#             current += slot_duration

#         return {
#             "message": "Available free slots fetched successfully",
#             "free_slots": available_slots
#         }

#     except Exception as e:
#         print("Error fetching free slots:", e)
#         raise HTTPException(status_code=500, detail=f"Failed to fetch free slots: {e}")