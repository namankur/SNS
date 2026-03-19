import os
from database import get_db

db = get_db()
if not db:
    print("Database not connected")
    exit(1)

# Primary User to Keep
PRIMARY_USER_ID = "f6ae6145-9b2c-4b4e-b063-292c4feb99d1"

# Identify linked Dear One IDs for the primary user to keep them as well
links = db.table("caller_dear_one_links").select("dear_one_id").eq("caller_id", PRIMARY_USER_ID).execute()
DEAR_ONE_IDS = [l['dear_one_id'] for l in links.data]

# Combine all IDs to preserve
KEEP_IDS = [PRIMARY_USER_ID] + DEAR_ONE_IDS
print(f"Keeping User IDs: {KEEP_IDS}")

# Delete from tables in order (to avoid FK constraints where possible, though Supabase usually handles CASCADE)
# Tables: signals, check_requests, caller_dear_one_links, routine_profiles, users

for user_id in [u['user_id'] for u in db.table("users").select("user_id").execute().data]:
    if user_id not in KEEP_IDS:
        print(f"Cleaning data for User {user_id}...")
        # Delete related records
        db.table("signals").delete().eq("user_id", user_id).execute()
        db.table("check_requests").delete().eq("caller_id", user_id).execute()
        db.table("check_requests").delete().eq("dear_one_id", user_id).execute()
        db.table("caller_dear_one_links").delete().eq("caller_id", user_id).execute()
        db.table("caller_dear_one_links").delete().eq("dear_one_id", user_id).execute()
        db.table("routine_profiles").delete().eq("user_id", user_id).execute()
        
        # Finally delete user
        db.table("users").delete().eq("user_id", user_id).execute()

print("Database cleanup complete.")
