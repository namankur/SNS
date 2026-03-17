import os
from pathlib import Path
from supabase import create_client, Client

# Load .env only if it exists (Railway injects env vars natively)
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("WARNING: Supabase credentials not found. Database features will fail.")
    supabase: Client = None
else:
    # Initialize Supabase client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_db() -> Client:
    """Returns the initialized supabase client."""
    return supabase
