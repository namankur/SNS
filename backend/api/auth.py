import os
from datetime import datetime, timedelta
import jwt
from fastapi import APIRouter, HTTPException, Depends
from models import UserCreate, VerifyOTPRequest
from database import get_db
from api.deps import JWT_SECRET, JWT_ALGORITHM, twilio_client, TWILIO_SMS_NUMBER, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

def create_jwt_token(user_id: str, role: str):
    expiration = datetime.utcnow() + timedelta(hours=int(os.getenv("JWT_EXPIRY_HOURS", 720)))
    payload = {
        "sub": user_id,
        "role": role,
        "exp": expiration
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

@router.post("/register")
async def register(user: UserCreate):
    """
    Register new user. Sends OTP.
    """
    db = get_db()
    if not db:
        raise HTTPException(status_code=500, detail="Database not connected")
        
    user_id = None
    try:
        existing = db.table("users").select("*").eq("phone_number", user.phone_number).execute()
        if len(existing.data) > 0:
            user_id = existing.data[0]['user_id']
            # Update name in case it changed
            db.table("users").update({"name": user.name}).eq("user_id", user_id).execute()
        else:
            # Insert new user
            new_user = db.table("users").insert({
                "name": user.name,
                "phone_number": user.phone_number,
                "role": user.role.value
            }).execute()
            user_id = new_user.data[0]['user_id']
    except Exception as e:
        print(f"Supabase connection error: {e}")
        user_id = "00000000-0000-0000-0000-000000000000" # Fallback for demo/missing DB
    
    # Store OTP in cache/redis in production. We use '1234' as static for this MVP unless hooked to Redis
    otp = "1234"
    
    # Format phone number to E.164 standard for Twilio
    target_phone = user.phone_number.strip()
    if len(target_phone) == 10 and target_phone.isdigit():
        target_phone = f"+91{target_phone}"
    elif not target_phone.startswith('+'):
        target_phone = f"+{target_phone}"
    
    if twilio_client and TWILIO_SMS_NUMBER:
        try:
            twilio_client.messages.create(
                body=f"Your Safe & Sound OTP is {otp}",
                from_=TWILIO_SMS_NUMBER,
                to=target_phone
            )
        except Exception as e:
            print(f"Twilio error: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to send SMS: {e}")
            
    return {"status": "success", "message": "OTP sent", "user_id": user_id}

@router.post("/verify-otp")
async def verify_otp(req: VerifyOTPRequest):
    """
    Verify OTP. Returns JWT.
    """
    db = get_db()
    if not db:
        raise HTTPException(status_code=500, detail="Database not connected")
    
    # In production, fetch OTP from Redis here. Hardcoded to '1234' for MVP demo.
    if req.otp != "1234":
        raise HTTPException(status_code=400, detail="Invalid OTP")
        
    # Fetch user
    user = db.table("users").select("*").eq("phone_number", req.phone_number).execute()
    if not user.data:
        raise HTTPException(status_code=404, detail="User not found")
        
    user_data = user.data[0]
    token = create_jwt_token(user_data['user_id'], user_data['role'])
    
    return {
        "status": "success", 
        "token": token, 
        "user_id": user_data['user_id'],
        "role": user_data['role']
    }
