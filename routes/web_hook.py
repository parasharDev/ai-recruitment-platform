from fastapi import APIRouter, Request
import json

router = APIRouter()

VERIFY_TOKEN = "my_verify_token"  

# Verification endpoint for WhatsApp
@router.get("/whatsapp/webhook")
async def verify(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)
    return {"status": "verification failed"}

# Receiving incoming messages from WhatsApp
# @router.post("/whatsapp/webhook")
# async def webhook(request: Request):
#     data = await request.json()
#     print("\nIncoming WhatsApp message:")
#     print(json.dumps(data, indent=2))

#     try:
#         # 1. Extracting message + button click ID
#         entry = data.get("entry", [])[0]
#         changes = entry.get("changes", [])[0]
#         value = changes.get("value", {})

#         messages = value.get("messages", [])
#         if not messages:
#             return {"status": "ignored"}

#         msg = messages[0]
#         from_number = msg.get("from")       # candidate WhatsApp number

#         # Checking if it's a button reply
#         if msg.get("type") == "interactive" and "button_reply" in msg["interactive"]:
#             button_id = msg["interactive"]["button_reply"]["id"]  
#             print(" Button clicked:", button_id)

#             # Lookup cached slots
#             from routes.whatsapp_send import SLOT_CACHE 

#             if from_number not in SLOT_CACHE:
#                 print(" No slot cache found for user:", from_number)
#                 return {"status": "no slots cached"}

#             selected_index = int(button_id.split("_")[1]) - 1  
#             selected_slot = SLOT_CACHE[from_number][selected_index]

#             print("Selected slot:", selected_slot)

#             #  2. Scheduling the event on Google Calendar
#             from routes.interview_scheduling import get_current_service
#             # from utils.google_calendar import get_calendar_service

#             service = get_current_service()

#             event_body = {
#                 "summary": "Interview Scheduled",
#                 "start": {"dateTime": selected_slot["start"], "timeZone": "Asia/Kolkata"},
#                 "end": {"dateTime": selected_slot["end"], "timeZone": "Asia/Kolkata"},
#                 "attendees": [
#                     {"email": "parasharghosh123@gmail.com"},
#                     {"email": "candidate@example.com"}  
#                 ],
#                 "conferenceData": {
#                     "createRequest": {
#                         "requestId": "meet-" + from_number,
#                         "conferenceSolutionKey": {"type": "hangoutsMeet"}
#                     }
#                 }
#             }

#             created = service.events().insert(
#                 calendarId="primary",
#                 body=event_body,
#                 conferenceDataVersion=1
#             ).execute()

#             meet_link = created["conferenceData"]["entryPoints"][0]["uri"]

#             #  Sending WhatsApp confirmation
#             from utils.whatsapp_client import send_text
#             send_text(from_number, f" Interview confirmed!\nMeet Link: {meet_link}")

#             return {"status": "scheduled", "meet_link": meet_link}

#         return {"status": "no action"}

#     except Exception as e:
#         print("ERROR in webhook:", e)
#         return {"status": "error", "message": str(e)}



@router.post("/whatsapp/webhook")
async def webhook(request: Request):
    data = await request.json()
    print("\nIncoming WhatsApp:")
    print(json.dumps(data, indent=2))

    try:
        entry = data["entry"][0]
        msg = entry["changes"][0]["value"].get("messages", [])[0]
        from_number = msg.get("from")  # WhatsApp number

        if msg.get("type") != "interactive":
            return {"status": "ignored"}

        button_id = msg["interactive"]["button_reply"]["id"]
        selected_index = int(button_id.split("_")[1]) - 1

        # CHANGE 4 — fetch metadata
        from routes.whatsapp_send import SLOT_CACHE
        cache = SLOT_CACHE.get(from_number)

        if not cache:
            return {"status": "cache_not_found"}

        selected_slot = cache["slots"][selected_index]
        candidate_email = cache["candidate_email"]

        from routes.interview_scheduling import get_current_service
        service = get_current_service()

        event = {
            "summary": "Interview Scheduled",
            "start": {"dateTime": selected_slot["start"], "timeZone": "Asia/Kolkata"},
            "end": {"dateTime": selected_slot["end"], "timeZone": "Asia/Kolkata"},
            "attendees": [
                {"email": "parasharghosh123@gmail.com"},
                {"email": candidate_email}
            ],
            "conferenceData": {
                "createRequest": {
                    "requestId": f"meet-{from_number}",
                    "conferenceSolutionKey": {"type": "hangoutsMeet"}
                }
            }
        }

        created = service.events().insert(
            calendarId="primary", body=event, conferenceDataVersion=1
        ).execute()

        meet_link = created["conferenceData"]["entryPoints"][0]["uri"]
        html_link = created.get("htmlLink")

        #  CHANGE 5 — save back to cache
        cache.update({
            "selected_slot": selected_slot,
            "meet_link": meet_link,
            "html_link": html_link,
            "status": "scheduled",
        })

        from utils.whatsapp_client import send_text
        send_text(from_number, f"Interview confirmed!\nMeet Link: {meet_link}")

        return {"status": "scheduled", "meet_link": meet_link}

    except Exception as e:
        print("ERROR:", e)
        return {"status": "error", "message": str(e)}


