from fastapi import APIRouter, Request, Response
from database import get_db
from core.sms_bot import handle_incoming_sms

router = APIRouter(prefix="/webhook", tags=["webhooks"])

@router.post("/sms")
async def textbee_sms_webhook(request: Request):
    """
    TextBee incoming SMS Webhook.
    TextBee sends POST with JSON body:
    {
        "smsId": "...",
        "message": "...",
        "sender": "+91...",
        "webhookEvent": "MESSAGE_RECEIVED"
    }
    """
    try:
        json_data = await request.json()
    except Exception:
        return {"status": "error", "message": "Invalid JSON body"}

    sender = json_data.get("sender", "").strip()
    body = json_data.get("message", "").strip()
    event = json_data.get("webhookEvent", "")

    if event != "MESSAGE_RECEIVED":
        return {"status": "ignored", "message": f"Unhandled event: {event}"}

    if not sender or not body:
        return {"status": "error", "message": "Missing sender or message"}

    response_msg = handle_incoming_sms(sender, body)

    return {"status": "ok", "reply": response_msg}

@router.post("/missed-call")
async def missed_call_webhook(request: Request):
    """
    Exotel webhook when dear one gives missed call.
    """
    form_data = await request.form()
    caller_phone = form_data.get("From", "")
    call_duration = int(form_data.get("DialCallDuration", 0))
    
    if call_duration < 5:
        db = get_db()
        if db:
            users = db.table("users").select("*").eq("phone_number", caller_phone).execute()
            if users.data:
                user_id = users.data[0]['user_id']
                db.table("signals").insert({
                    "user_id": user_id,
                    "timestamp": "now()",
                    "movement_type": "CHECKED_IN_MISSED_CALL",
                    "screen_active_last_mins": 1
                }).execute()
                
    return Response(content="ok", media_type="text/plain")
