from database import get_db

db = get_db()
if not db:
    print("Database not connected")
    exit(1)

# Inspect columns by fetching one record
res = db.table("signals").select("*").limit(1).execute()
if res.data:
    print("Current Columns:", list(res.data[0].keys()))
else:
    print("No records found in signals table to inspect columns.")
