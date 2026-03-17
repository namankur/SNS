import os
from datetime import datetime, timedelta
import jwt
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from twilio.rest import Client
from models import UserCreate, VerifyOTPRequest
from database import get_db

router = APIRouter(prefix="/api/auth", tags=["auth"])

JWT_SECRET = os.getenv("JWT_SECRET_KEY", "fallback_secret_must_be_at_least_32_bytes_long_for_hs256")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_SMS_NUMBER = os.getenv("TWILIO_SMS_NUMBER")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) if TWILIO_ACCOUNT_SID else None
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

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
