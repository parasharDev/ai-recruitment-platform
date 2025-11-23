# utils/feedback_email.py

import os
from services.google_service import get_current_service

INTERVIEWER_EMAIL = "parasharghosh123@gmail.com"
FEEDBACK_FORM = os.getenv("FEEDBACK_FORM")   

def send_feedback_email(candidate_name, job_title, selected_slot):
    """
    Sending feedback request email to interviewer after meeting is scheduled.
    """
    service = get_current_service()
    if not service:
        print("⚠ Google authentication not completed — cannot send feedback email.")
        return

    subject = f"Feedback Required — {candidate_name} | {job_title}"
    body = f"""
Hi,

The interview has been completed / scheduled for the following candidate:

👤 Candidate: {candidate_name}
🧠 Position: {job_title}
🗓 Slot: {selected_slot['start']} → {selected_slot['end']}


Please submit your feedback using the below Google Form:
{FEEDBACK_FORM}

Thank you.
    """

    # Sending email to interviewer
    event = {
        "summary": subject,
        "description": body,
        "attendees": [{"email": INTERVIEWER_EMAIL}],
        "start": {"dateTime": selected_slot["start"], "timeZone": "Asia/Kolkata"},
        "end": {"dateTime": selected_slot["end"], "timeZone": "Asia/Kolkata"},
    }

    service.events().insert(
        calendarId="primary",
        body=event,
        sendUpdates="all",
        sendNotifications=True
    ).execute()

    print("📩 Feedback email sent successfully to interviewer.")
