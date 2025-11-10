import os
import requests

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")  
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID") 


GRAPH_URL = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

def _headers():
    if not WHATSAPP_TOKEN or not PHONE_NUMBER_ID:
        raise RuntimeError("WHATSAPP_TOKEN or WHATSAPP_PHONE_NUMBER_ID not set")
    return {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

def send_text(to_number: str, body: str):
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": body}
    }
    r = requests.post(GRAPH_URL, headers=_headers(), json=payload, timeout=30)
    if r.status_code >= 300:
        raise RuntimeError(f"WhatsApp send_text failed: {r.text}")
    return r.json()

def send_slot_buttons(to_number: str, title: str, options: list[str]):
    """
    Sends up to 3 buttons with slot options. If you have more than 3, send multiple messages or a list-type interactive message.
    """
    buttons = []
    for idx, opt in enumerate(options[:3], start=1):
        buttons.append({
            "type": "reply",
            "reply": {"id": f"slot_{idx}", "title": opt}
        })

    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": title},
            "action": {"buttons": buttons}
        }
    }
    r = requests.post(GRAPH_URL, headers=_headers(), json=payload, timeout=30)
    if r.status_code >= 300:
        raise RuntimeError(f"WhatsApp send_slot_buttons failed: {r.text}")
    return r.json()
