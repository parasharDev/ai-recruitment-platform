from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime
from typing import List, Dict
from utils.whatsapp_client import send_slot_buttons
from google.auth.transport.requests import Request
from utils.google_calendar import get_calendar_service
from routes.interview_scheduling import get_current_service  # reuse your dependency

router = APIRouter()

# Simple in-memory cache { whatsapp_number: [ {start, end}, ... ] }
# SLOT_CACHE: Dict[str, List[Dict[str, str]]] = {}
SLOT_CACHE: Dict[str, List[Dict[str, any]]] = {}


@router.post("/whatsapp/propose_slots")
def whatsapp_propose_slots(
    candidate_whatsapp: str = Query(...),
    interviewer_calendar_id: str = Query(...),
    start_date: str = Query(...),
    end_date: str = Query(...),
    job_title: str = Query(...),
    candidate_name: str = Query(...),
    candidate_email: str = Query(...), 
    count: int = Query(3, ge=1, le=3),
    service=Depends(get_current_service)
):
    import pytz
    from datetime import timedelta
    try:
        # FIX 1: Validate Google auth
        if service is None:
            raise Exception("Google authentication not completed. Call /api/auth/google first.")
        tz = pytz.timezone("Asia/Kolkata")
        start_dt = tz.localize(datetime.strptime(start_date, "%Y-%m-%d"))
        end_dt = tz.localize(datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1))

        fb_query = {
            "timeMin": start_dt.isoformat(),
            "timeMax": end_dt.isoformat(),
            "timeZone": "Asia/Kolkata",
            "items": [{"id": interviewer_calendar_id}]
        }

        #  FIX 2: FreeBusy API call is correct
        fb_resp = service.freebusy().query(body=fb_query).execute()

        if interviewer_calendar_id not in fb_resp["calendars"]:
            raise Exception(f"Calendar ID {interviewer_calendar_id} not found.")

        busy_times = fb_resp["calendars"][interviewer_calendar_id].get("busy", [])

        #  Working hours and slot duration
        work_start = 9
        work_end = 17
        slot_dur = timedelta(hours=1)

        day_start = start_dt.replace(hour=work_start, minute=0, second=0)
        day_end = start_dt.replace(hour=work_end, minute=0, second=0)

        slots = []
        cursor = day_start

        while cursor + slot_dur <= day_end:
            s_start = cursor
            s_end = cursor + slot_dur

            overlap = False
            for b in busy_times:
                b_start = datetime.fromisoformat(b["start"])
                b_end = datetime.fromisoformat(b["end"])
                if s_start < b_end and s_end > b_start:
                    overlap = True
                    break

            if not overlap:
                slots.append({
                    "start": s_start.strftime("%Y-%m-%dT%H:%M:%S"),
                    "end": s_end.strftime("%Y-%m-%dT%H:%M:%S")
                })

            cursor += slot_dur

        if not slots:
            raise Exception("No free slots found.")

        #  Reduce to top N
        top_slots = slots[:count]

        #  Convert to WhatsApp button labels
        labels = []
        for s in top_slots:
            st = datetime.strptime(s["start"], "%Y-%m-%dT%H:%M:%S")
            en = datetime.strptime(s["end"], "%Y-%m-%dT%H:%M:%S")

    # Short button label (always <20 chars)
            start_label = st.strftime("%I:%M%p")   # e.g., 10:00AM
            end_label = en.strftime("%I:%M%p")     # e.g., 11:00AM

            labels.append(f"{start_label}-{end_label}")  # e.g., "10:00AM-11:00AM"


        # Cache for webhook selection
        # SLOT_CACHE[candidate_whatsapp] = top_slots
        SLOT_CACHE[candidate_whatsapp] = {
            "slots": top_slots,
            "candidate_email": candidate_email,
            "candidate_name": candidate_name,
            "job_title": job_title,
            "status": "proposed",
            "selected_slot": None,
            "meet_link": None,
            "html_link": None
        }

        # Send WhatsApp interactive message
        message_text = (
        f"Hello *{candidate_name}*,\n\n"
        f"Greetings from ABC Company!\n"
        f"We are impressed with your profile for the *{job_title}* position.\n"
        "We would like to invite you for a virtual interview.\n\n"
        "Please choose one of the following available slots that works best for you:"
        )

        send_slot_buttons(candidate_whatsapp, message_text, labels)

        # send_slot_buttons(candidate_whatsapp, "Hello {candidate_name}.We are impressed with your profile for the {job_title} position and would like to invite you for a virtual interview.Please choose one of the following available slots that works best for you:", labels)

        return {
            "message": "Slots sent to WhatsApp!",
            "sent": labels
        }

    except Exception as e:
        import traceback
        print("ERROR in /whatsapp/propose_slots:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
    

    #  — Get scheduled meeting status
@router.get("/whatsapp/slot_status")
def slot_status(whatsapp_number: str):
    """
    Returns slot + meeting details stored in SLOT_CACHE
    for a given candidate WhatsApp number.
    """
    return SLOT_CACHE.get(whatsapp_number, {})




