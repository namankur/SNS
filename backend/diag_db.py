import os
from database import get_db

db = get_db()
if not db:
    print("Database not connected")
    exit(1)

print("--- USERS ---")
users = db.table("users").select("phone_number, name").execute()
for u in users.data:
    print(f"Name: {u['name']}, Phone: {u['phone_number']}")

print("\n--- RECENT CHECK REQUESTS ---")
reqs = db.table("check_requests").select("*").limit(10).execute()
for r in reqs.data:
    print(f"Data: {r}")
