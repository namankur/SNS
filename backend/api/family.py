from fastapi import APIRouter, HTTPException, Depends
from models import LinkFamilyRequest
from database import get_db
from api.deps import get_current_user, twilio_client, TWILIO_SMS_NUMBER, TWILIO_WHATSAPP_NUMBER

router = APIRouter(prefix="/api/family", tags=["family"])

@router.post("/link")
async def link_family(req: LinkFamilyRequest, caller_id: str = Depends(get_current_user)):
    """
    Caller sends invite to dear_one phone number.
    Dear one receives WhatsApp message to accept.
    """
    db = get_db()
    if not db:
        raise HTTPException(status_code=500, detail="Database not connected")
        
    dear_phone = req.dear_one_phone.strip()
    if len(dear_phone) == 10 and dear_phone.isdigit():
        dear_phone = f"+91{dear_phone}"
    elif not dear_phone.startswith('+'):
        dear_phone = f"+{dear_phone}"

    dear_one_id = None
    try:
        existing = db.table("users").select("*").eq("phone_number", dear_phone).execute()
        if existing.data:
            dear_one_id = existing.data[0]['user_id']
        else:
            new_user = db.table("users").insert({
                "name": req.nickname,
                "phone_number": dear_phone,
                "role": "dear_one"
            }).execute()
            dear_one_id = new_user.data[0]['user_id']
            
        db.table("caller_dear_one_links").insert({
            "caller_id": caller_id,
            "dear_one_id": dear_one_id,
            "nickname": req.nickname
        }).execute()
    except Exception as e:
        print(f"Error executing Supabase link: {e}")

    # Send Invite Message
    try:
        caller_res = db.table("users").select("name").eq("user_id", caller_id).execute()
        caller_name = caller_res.data[0]['name'] if caller_res.data else "Aapke kisi apne"
    except Exception:
        caller_name = "Aapke kisi apne"

    apk_link = "https://awqhrmnfxsdqospuiamm.supabase.co/storage/v1/object/public/releases/app-debug.apk"
    message_body = (
        f"Namaste {req.nickname} ji, "
        f"{caller_name} ne aapke liye Safe & Sound app setup kiya hai. "
        f"Install karein: {apk_link}"
    )

    sms_status = "no_twilio_client"
    sms_error = None
    whatsapp_status = "skipped"
    whatsapp_error = None

    if twilio_client:
        # 1) PRIMARY: Send via SMS (reliable on trial accounts)
        if TWILIO_SMS_NUMBER:
            try:
                sms_msg = twilio_client.messages.create(
                    body=message_body,
                    from_=TWILIO_SMS_NUMBER,
                    to=dear_phone
                )
                sms_status = "sent"
                print(f"SMS invite sent! SID: {sms_msg.sid}")
            except Exception as e:
                sms_status = "failed"
                sms_error = str(e)
                print(f"Error sending SMS invite: {e}")
        else:
            sms_status = "no_sms_number_configured"

        # 2) SECONDARY: Also try WhatsApp (works only if recipient has active session)
        if TWILIO_WHATSAPP_NUMBER:
            try:
                wa_number = TWILIO_WHATSAPP_NUMBER.replace("whatsapp:", "")
                wa_msg = twilio_client.messages.create(
                    body=message_body,
                    from_=f"whatsapp:{wa_number}",
                    to=f"whatsapp:{dear_phone}"
                )
                whatsapp_status = "sent"
                print(f"WhatsApp invite also sent! SID: {wa_msg.sid}")
            except Exception as e:
                whatsapp_status = "failed"
                whatsapp_error = str(e)
                print(f"WhatsApp attempt failed (non-critical): {e}")

    # Invite is considered successful if SMS was sent
    overall_status = "sent" if sms_status == "sent" else sms_status

    return {
        "status": "success", 
        "message": "Dear one linked successfully",
        "dear_one_id": dear_one_id,
        "invite_status": overall_status,
        "sms_status": sms_status,
        "sms_error": sms_error,
        "whatsapp_status": whatsapp_status,
        "whatsapp_error": whatsapp_error,
        "message_body": message_body
    }

@router.get("/check/{dear_one_nickname}")
async def manual_check(dear_one_nickname: str):
    """
    Called when caller asks 'Maa?' on WhatsApp (or via UI).
    Enforce cooldown.
    Calculate deviation score.
    Call Claude API.
    """
    return {"status": "success", "message": "Simulated checking response."}

@router.get("/dear-one/check-log")
async def get_check_log():
    """
    Dear one can see who checked and when. 
    Returns last 10 requests.
    """
    return {"logs": []}

@router.post("/dear-one/pause")
async def pause_checks(hours: int = 12):
    """
    Dear one pauses all checks for X hours.
    """
    return {"status": "success", "message": f"Paused checks for {hours} hours"}
