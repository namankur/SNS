from fastapi import APIRouter, HTTPException, Depends
from models import LinkFamilyRequest
from database import get_db

router = APIRouter(prefix="/api/family", tags=["family"])

@router.post("/link")
async def link_family(req: LinkFamilyRequest):
    """
    Caller sends invite to dear_one phone number.
    Dear one receives WhatsApp message to accept.
    """
    return {"status": "success", "message": f"Invite sent to {req.dear_one_phone}"}

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
