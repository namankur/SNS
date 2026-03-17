import os
from datetime import datetime, timedelta, timezone
from .routine_engine import calculate_deviation_score, calculate_routine_profile
from .ai_engine import generate_response
from database import get_db

FREE_TIER_COOLDOWN_MINS = int(os.getenv("FREE_TIER_COOLDOWN_MINS", 60))
PREMIUM_TIER_COOLDOWN_MINS = int(os.getenv("PREMIUM_TIER_COOLDOWN_MINS", 20))

def parse_dear_one_from_message(message: str, caller_id: str) -> str:
    """
    Extract name from message and match to caller's linked dear ones.
    Returns: mapped dear_one_id or None
    """
    msg_lower = message.lower().strip()
    
    # Common variations mapping
    # Just mock returning the first linked dear one for now since DB is empty
    db = get_db()
    if not db:
        return None
        
    links = db.table("caller_dear_one_links").select("*").eq("caller_id", caller_id).execute()
    if not links.data:
        return None
        
    if len(links.data) == 1:
        return links.data[0]['dear_one_id']
        
    # If multiple, ideally parse msg_lower for matches
    for link in links.data:
        nickname = link['nickname'].lower()
        if nickname in msg_lower:
            return link['dear_one_id']
            
    # Ambiguous
    return "AMBIGUOUS"

def check_cooldown(caller_id: str, dear_one_id: str, tier: str) -> dict:
    """
    Enforces check frequency limits.
    Returns dict: {"allowed": bool, "message": str} 
    """
    db = get_db()
    if not db:
        return {"allowed": True}
        
    cooldown_mins = PREMIUM_TIER_COOLDOWN_MINS if tier == 'premium' else FREE_TIER_COOLDOWN_MINS
    
    # Check last request in check_requests table
    # Mocking check for brevity
    # last_check = db.table()...
    last_check_time = None # datetime object
    
    if last_check_time:
        diff_mins = (datetime.now(timezone.utc) - last_check_time).total_seconds() / 60
        if diff_mins < cooldown_mins:
            rem = int(cooldown_mins - diff_mins)
            return {
                "allowed": False,
                "message": f"Aapne {int(diff_mins)} minute pehle check kiya tha.\nTab ka status: [cached]\nNext check available in {rem} minutes."
            }
            
    return {"allowed": True}

def get_onboarding_message() -> str:
    return (
        "Namaste! 🙏 Main Safe & Sound hoon.\n"
        "Apno ki chinta khatam karo.\n"
        "Setup ke liye:\n"
        "safeandsound.in/setup par jaiye aur apna account banao.\n"
        "Baad mein yahan 'Maa' ya 'Papa' likh ke check kar sakte ho."
    )

def handle_incoming_whatsapp(caller_phone: str, message: str) -> str:
    """
    Full pipeline to orchestrate the webhook request.
    """
    db = get_db()
    if not db:
        return "Abhi system busy hai. 2 minute mein dobara try karein 🙏"
        
    # 1. Lookup caller
    users = db.table("users").select("*").eq("phone_number", caller_phone).execute()
    if not users.data:
        return get_onboarding_message()
        
    caller = users.data[0]
    caller_id = caller['user_id']
    tier = caller.get('tier', 'free')
    
    # 2. Parse dear one
    dear_one_id = parse_dear_one_from_message(message, caller_id)
    if not dear_one_id:
        return "Aapne abhi tak kisi ko link nahi kiya hai. Pehle website par jaa ke setup complete karein."
    if dear_one_id == "AMBIGUOUS":
        return "Maa ya Papa? Kiska status check karna hai?"
        
    # 3. Check Cooldown
    cooldown = check_cooldown(caller_id, dear_one_id, tier)
    if not cooldown["allowed"]:
        return cooldown["message"]
        
    # 4. Process Request via AI
    score = calculate_deviation_score(user_id=dear_one_id)
    signals_res = db.table("signals").select("*").eq("user_id", dear_one_id).order("timestamp", desc=True).limit(3).execute()
    routine_res = db.table("routine_profiles").select("*").eq("user_id", dear_one_id).execute()
    
    signals = signals_res.data if signals_res.data else []
    routine = routine_res.data[0] if routine_res.data else {}
    
    ai_response = generate_response(
        user_id=dear_one_id,
        dear_one_nickname="Ji", # Can fetch from link
        language="hindi",
        signals=signals,
        routine_profile=routine,
        deviation_score=score,
        current_datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    
    # 5. Record request
    db.table("check_requests").insert({
        "caller_id": caller_id,
        "dear_one_id": dear_one_id,
        "response_generated": ai_response,
        "deviation_score": score,
        "tier": tier
    }).execute()
    
    return ai_response
