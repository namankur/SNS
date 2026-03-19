import os
from database import get_db

db = get_db()
if not db:
    print("Database not connected")
    exit(1)

print("--- USERS (DETAILED) ---")
users = db.table("users").select("user_id, phone_number, name, created_at").execute()
for u in users.data:
    print(f"ID: {u['user_id']}, Name: {u['name']}, Phone: {u['phone_number']}, Created: {u.get('created_at', 'N/A')}")
