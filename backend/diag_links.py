import os
from database import get_db

db = get_db()
if not db:
    print("Database not connected")
    exit(1)

print("--- USERS ---")
users = db.table("users").select("user_id, phone_number, name").execute()
user_map = {u['user_id']: u['name'] for u in users.data}
for u in users.data:
    print(f"ID: {u['user_id']}, Name: {u['name']}, Phone: {u['phone_number']}")

print("\n--- FAMILY LINKS ---")
links = db.table("caller_dear_one_links").select("*").execute()
for l in links.data:
    caller_name = user_map.get(l['caller_id'], "Unknown")
    dear_one_name = user_map.get(l['dear_one_id'], "Unknown")
    print(f"Caller: {caller_name} -> Dear One: {dear_one_name} (Nickname: {l['nickname']})")
