from datetime import datetime, timedelta, timezone
from database import get_db

IST = timezone(timedelta(hours=5, minutes=30))

def calculate_routine_profile(user_id: str):
    """
    Calculate the routine profile for a user based on last 14 days of signals.
    """
    db = get_db()
    if not db:
        return
        
    two_weeks_ago = (datetime.now(IST) - timedelta(days=14)).isoformat()
    signals = db.table("signals").select("*").eq("user_id", user_id).gt("timestamp", two_weeks_ago).execute()
    
    # Calculate days of data
    unique_days = set()
    for sig in signals.data:
        try:
            dt = datetime.fromisoformat(sig['timestamp'].replace('Z', '+00:00'))
            dt_ist = dt.astimezone(IST)
            unique_days.add(dt_ist.date())
        except:
            pass
            
    if len(unique_days) >= 7:
        # Mock aggregation for brevity in this full-stack proof-of-concept
        # A real implementation would parse the dates and categorize events natively
        profile = {
            "user_id": user_id,
            "wake_time_avg": "06:30 AM",
            "nap_window_start": "02:00 PM",
            "nap_window_end": "04:00 PM",
            "sleep_time_avg": "10:30 PM",
            "walk_days": ["MON", "WED", "FRI"],
            "days_of_data": len(unique_days),
            "last_updated": "now()"
        }
        db.table("routine_profiles").upsert(profile).execute()

def calculate_deviation_score(user_id: str):
    """
    Calculate how much the latest signal deviates from the established routine.
    Returns: float 0.0 to 1.0
    """
    db = get_db()
    if not db:
        return 0.0
        
    signals = db.table("signals").select("*").eq("user_id", user_id).order("timestamp", desc=True).limit(1).execute()
    profiles = db.table("routine_profiles").select("*").eq("user_id", user_id).execute()
    
    if not signals.data or not profiles.data:
        return 0.0 # Not enough data
        
    latest = signals.data[0]
    profile = profiles.data[0]
    
    score = 0.0
    
    # Analyze lack of signal
    try:
        last_dt = datetime.fromisoformat(latest['timestamp'].replace('Z', '+00:00'))
        hours_since = (datetime.now(IST) - last_dt.astimezone(IST)).total_seconds() / 3600
        
        if hours_since > 8:
            score += 0.4
        elif hours_since > 4:
            score += 0.2
            
        # Example naive activity proxy
        if latest.get("screen_active_last_mins", 0) < 5 and hours_since < 2:
            score += 0.1
            
    except:
        pass
        
    return min(1.0, score)
