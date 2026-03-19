import os
from database import get_db

db = get_db()
if not db:
    print("Database not connected")
    exit(1)

# List of tables to wipe and their primary key columns
WIPE_CONFIG = {
    "signals": "id",
    "check_requests": "request_id",
    "caller_dear_one_links": "link_id",
    "routine_profiles": "user_id",
    "users": "user_id"
}

print("--- STARTING SUPER PURGE ---")
for table, pk in WIPE_CONFIG.items():
    print(f"Purging {table}...")
    try:
        # Fetch all IDs
        res = db.table(table).select(pk).execute()
        ids = [r[pk] for r in res.data]
        if ids:
            print(f"Deleting {len(ids)} rows from {table}...")
            # Delete in chunks or all at once if supported
            db.table(table).delete().in_(pk, ids).execute()
        else:
            print(f"Table {table} is already empty.")
    except Exception as e:
        print(f"ERROR purging {table}: {e}")

print("--- DATABASE IS NOW COMPLETELY EMPTY ---")
