from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from models import SignalCreate
from database import get_db
from core.routine_engine import calculate_routine_profile

router = APIRouter(prefix="/api/signals", tags=["signals"])

# Dummy dep for JWT; would decode real JWT in prod
async def get_current_user_id() -> str:
    # return decoded_jwt['sub']
    return "00000000-0000-0000-0000-000000000000" # fallback

@router.post("")
async def receive_signals(signal: SignalCreate, background_tasks: BackgroundTasks):
    """
    Receive signal packet from dear one's Android app.
    """
    db = get_db()
    if not db:
        raise HTTPException(status_code=500, detail="Database not connected")
        
    user_id = await get_current_user_id()
    
    try:
        db.table("signals").insert({
            "user_id": user_id,
            "timestamp": signal.timestamp.isoformat(),
            "screen_active_last_mins": signal.screen_active_last_mins,
            "movement_type": signal.movement_type,
            "last_interaction_time": signal.last_interaction_time,
            "battery_level": signal.battery_level,
            "is_charging": signal.is_charging,
            "network_type": signal.network_type,
            "dnd_active": signal.dnd_active
        }).execute()
    except Exception as e:
        # FK error likely if user doesn't exist yet
        pass
        
    # Calculate Routine Profile periodically in background
    # Instead of doing it inline, standard practice:
    background_tasks.add_task(calculate_routine_profile, user_id)
    
    return {"status": "success", "message": "Signal recorded"}
