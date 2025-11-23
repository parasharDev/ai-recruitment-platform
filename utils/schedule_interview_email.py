from services.google_service import get_current_service

INTERVIEWER_EMAIL = "parasharghosh123@gmail.com"

def schedule_interview_email(selected_slot, candidate_email, job_title, from_number):
    """
    Creates Google Calendar event + Meet link + triggers email reminder.
    """
    service = get_current_service()
    if not service:
        print("⚠ Google authentication not completed")
        return None

    event_body = {
        "summary": f"Interview Scheduled for {job_title}",
        "start": {"dateTime": selected_slot["start"], "timeZone": "Asia/Kolkata"},
        "end": {"dateTime": selected_slot["end"], "timeZone": "Asia/Kolkata"},
        "attendees": [
            {"email": INTERVIEWER_EMAIL},
            {"email": candidate_email}
        ],
        "conferenceData": {
            "createRequest": {
                "requestId": f"meet-{from_number}",
                "conferenceSolutionKey": {"type": "hangoutsMeet"}
            }
        },
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "email", "minutes": 30},  # auto reminder before 30 mins
            ]
        }
    }

    created = service.events().insert(
        calendarId="primary",
        body=event_body,
        conferenceDataVersion=1,
        sendUpdates="all", 
        sendNotifications=True  # email invites sent automatically
    ).execute()

    meet_link = created["conferenceData"]["entryPoints"][0]["uri"]
    html_link = created.get("htmlLink")
    return meet_link, html_link
