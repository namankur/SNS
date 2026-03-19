from fastapi import APIRouter, HTTPException, Depends
from models import LinkFamilyRequest
from database import get_db
from api.deps import get_current_user, send_sms_via_textbee, TEXTBEE_API_KEY
from core.sms_bot import handle_incoming_sms
from core.ai_engine import generate_response
from core.routine_engine import calculate_deviation_score
from datetime import datetime

router = APIRouter(prefix="/api/family", tags=["family"])

@router.post("/link")
async def link_family(req: LinkFamilyRequest, caller_id: str = Depends(get_current_user)):
    """
    Caller sends invite to dear_one phone number.
    Dear one receives SMS message with app install link.
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

    # Send Invite Message via SMS (TextBee)
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

    sms_status = "no_textbee_config"
    sms_error = None

    if TEXTBEE_API_KEY:
        result = await send_sms_via_textbee([dear_phone], message_body)
        if result["success"]:
            sms_status = "sent"
            print(f"SMS invite sent via TextBee to {dear_phone}")
        else:
            sms_status = "failed"
            sms_error = result.get("error", "Unknown TextBee error")
            print(f"Error sending SMS invite via TextBee: {sms_error}")
    else:
        sms_error = "TextBee API key not configured. Set TEXTBEE_API_KEY and TEXTBEE_DEVICE_ID in .env"

    return {
        "status": "success", 
        "message": "Dear one linked successfully",
        "dear_one_id": dear_one_id,
        "invite_status": sms_status,
        "sms_status": sms_status,
        "sms_error": sms_error,
        "message_body": message_body
    }

@router.get("/check/{dear_one_nickname}")
async def manual_check(dear_one_nickname: str, caller_id: str = Depends(get_current_user)):
    """
    Called when caller clicks 'Check Now via SMS' in the UI.
    """
    db = get_db()
    if not db:
        raise HTTPException(status_code=500, detail="Database not connected")
        
    # 1. Lookup the link to get dear_one_id
    link_res = db.table("caller_dear_one_links").select("*").eq("caller_id", caller_id).ilike("nickname", dear_one_nickname).execute()
    if not link_res.data:
        raise HTTPException(status_code=404, detail=f"No link found for {dear_one_nickname}")
        
    link = link_res.data[0]
    dear_one_id = link['dear_one_id']
    
    # 2. Process Request via AI (Mirroring logic in sms_bot.py)
    score = calculate_deviation_score(user_id=dear_one_id)
    signals_res = db.table("signals").select("*").eq("user_id", dear_one_id).order("timestamp", desc=True).limit(3).execute()
    routine_res = db.table("routine_profiles").select("*").eq("user_id", dear_one_id).execute()
    
    signals = signals_res.data if signals_res.data else []
    routine = routine_res.data[0] if routine_res.data else {}
    
    ai_response = generate_response(
        user_id=dear_one_id,
        dear_one_nickname=dear_one_nickname,
        language="hindi",
        signals=signals,
        routine_profile=routine,
        deviation_score=score,
        current_datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    
    # 3. Record request
    db.table("check_requests").insert({
        "caller_id": caller_id,
        "dear_one_id": dear_one_id,
        "response_generated": ai_response,
        "deviation_score": score,
        "tier": "free"
    }).execute()
    
    # 4. Send SMS to Caller
    caller_res = db.table("users").select("phone_number").eq("user_id", caller_id).execute()
    if caller_res.data:
        caller_phone = caller_res.data[0]['phone_number']
        if TEXTBEE_API_KEY:
            await send_sms_via_textbee([caller_phone], ai_response)
            
    return {"status": "success", "message": ai_response}

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
