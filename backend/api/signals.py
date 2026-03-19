from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from models import SignalCreate
from database import get_db
from core.routine_engine import calculate_routine_profile

router = APIRouter(prefix="/api/signals", tags=["signals"])

    # Lookup user by phone number
    users_res = db.table("users").select("user_id").eq("phone_number", signal.phone_number).execute()
    if not users_res.data:
        raise HTTPException(status_code=404, detail="User not found for this phone number")
        
    user_id = users_res.data[0]['user_id']
    
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
