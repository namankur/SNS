from fastapi import APIRouter, Request, Response, BackgroundTasks
from database import get_db
from core.sms_bot import handle_incoming_sms
from .deps import send_sms_via_textbee

router = APIRouter(prefix="/webhook", tags=["webhooks"])

@router.get("/test")
async def test_webhook():
    return {"status": "ok", "message": "Webhook endpoint is reachable"}

@router.get("/sms")
@router.get("/sms/")
async def textbee_sms_webhook_get():
    return {"status": "ok", "message": "TextBee Webhook Endpoint is Active"}

@router.post("/sms")
@router.post("/sms/")
async def textbee_sms_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    TextBee incoming SMS Webhook.
    """
    try:
        json_data = await request.json()
        
        sender = json_data.get("sender", "").strip()
        body = json_data.get("message", "").strip()
        event = json_data.get("webhookEvent", "")

        if event != "MESSAGE_RECEIVED":
            return {"status": "ignored", "message": f"Unhandled event: {event}"}

        if not sender or not body:
            return {"status": "error", "message": "Missing sender or message"}

        # Process and generate AI response
        response_msg = handle_incoming_sms(sender, body)

        # Queue the SMS response via TextBee
        if response_msg:
            background_tasks.add_task(send_sms_via_textbee, [sender], response_msg)

        return {"status": "ok", "message": "Webhook processed, response queued"}

    except Exception as e:
        error_msg = str(e)
        print(f"WEBHOOK ERROR: {error_msg}")
        return {"status": "error", "message": error_msg}

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
