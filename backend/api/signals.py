from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from models import SignalCreate
from database import get_db
from core.routine_engine import calculate_routine_profile

router = APIRouter(prefix="/api/signals", tags=["signals"])

@router.post("")
async def receive_signals(signal: SignalCreate, background_tasks: BackgroundTasks):
    """
    Receive signal packet from dear one's Android app.
    """
    db = get_db()
    if not db:
        raise HTTPException(status_code=500, detail="Database not connected")

    # Robustly lookup user by matching the last 10 digits to ignore formatting
    clean_incoming = ''.join(filter(str.isdigit, signal.phone_number))
    if len(clean_incoming) < 10:
        raise HTTPException(status_code=400, detail="Invalid phone number format")
    target_digits = clean_incoming[-10:]
    
    users_res = db.table("users").select("user_id, phone_number").execute()
    user_id = None
    
    for u in users_res.data:
        clean_db = ''.join(filter(str.isdigit, u.get("phone_number", "")))
        if clean_db.endswith(target_digits):
            user_id = u["user_id"]
            break
            
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found for this phone number")
    try:
        db.table("signals").insert({
            "user_id": user_id,
            "timestamp": signal.timestamp.isoformat(),
            "screen_active_last_mins": signal.screen_active_last_mins,
            "movement_type": signal.movement_type,
            "last_interaction_time": signal.last_interaction_time,
            "battery_level": signal.battery_level,
            "is_charging": signal.is_charging,
            "is_wifi": signal.is_wifi,
            "network_type": signal.network_type,
            "dnd_active": signal.dnd_active,
            "ringer_mode": signal.ringer_mode,
            "ringer_volume": signal.ringer_volume,
            "is_headphone_plugged": signal.is_headphone_plugged,
            "ambient_light": signal.ambient_light,
            "phone_orientation": signal.phone_orientation,
            "proximity": signal.proximity,
            "app_category": signal.app_category
        }).execute()
    except Exception as e:
        # FK error likely if user doesn't exist yet
        pass
        
    # Calculate Routine Profile periodically in background
    # Instead of doing it inline, standard practice:
    background_tasks.add_task(calculate_routine_profile, user_id)
    
    return {"status": "success", "message": "Signal recorded"}
