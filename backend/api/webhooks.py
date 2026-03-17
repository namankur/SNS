from fastapi import APIRouter, Request, BackgroundTasks, Response
from database import get_db
from core.whatsapp_bot import handle_incoming_whatsapp

router = APIRouter(prefix="/webhook", tags=["webhooks"])

@router.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    """
    Twilio WhatsApp Webhook.
    """
    form_data = await request.form()
    sender = form_data.get("From", "").replace("whatsapp:", "") # e.g. whatsapp:+1234
    body = form_data.get("Body", "").strip()
    
    response_msg = handle_incoming_whatsapp(sender, body)
    
    # Return valid TwiML
    twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{response_msg}</Message>
</Response>'''
    
    return Response(content=twiml, media_type="application/xml")

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
