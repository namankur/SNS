"""
Shared dependencies used across API modules.
Avoids circular imports between auth.py and family.py.
"""
import os
import jwt
import httpx
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

JWT_SECRET = os.getenv("JWT_SECRET_KEY", "fallback_secret_must_be_at_least_32_bytes_long_for_hs256")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# TextBee SMS Gateway Config
TEXTBEE_API_KEY = os.getenv("TEXTBEE_API_KEY")
TEXTBEE_DEVICE_ID = os.getenv("TEXTBEE_DEVICE_ID")
TEXTBEE_BASE_URL = os.getenv("TEXTBEE_BASE_URL", "https://api.textbee.dev/api/v1")

security = HTTPBearer()

async def send_sms_via_textbee(recipients: list, message: str) -> dict:
    """
    Send SMS using TextBee REST API.
    POST {BASE_URL}/gateway/devices/{DEVICE_ID}/send-sms
    Headers: x-api-key
    Body: { recipients: [...], message: "..." }
    Returns: { "success": bool, "data": ..., "error": ... }
    """
    if not TEXTBEE_API_KEY or not TEXTBEE_DEVICE_ID:
        return {"success": False, "error": "TextBee API key or Device ID not configured"}

    url = f"{TEXTBEE_BASE_URL}/gateway/devices/{TEXTBEE_DEVICE_ID}/send-sms"
    headers = {
        "x-api-key": TEXTBEE_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "recipients": recipients,
        "message": message,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response_data = response.json()

            if response.status_code >= 200 and response.status_code < 300:
                print(f"TextBee SMS sent successfully to {recipients}")
                return {"success": True, "data": response_data}
            else:
                error_msg = response_data.get("message", response.text)
                print(f"TextBee API error ({response.status_code}): {error_msg}")
                return {"success": False, "error": error_msg, "status_code": response.status_code}
    except httpx.TimeoutException:
        print("TextBee API request timed out")
        return {"success": False, "error": "Request timed out. Check network or TextBee service status."}
    except Exception as e:
        print(f"TextBee send error: {e}")
        return {"success": False, "error": str(e)}


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
