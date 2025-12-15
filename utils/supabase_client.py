import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

# Singleton instance
supabase: Client = None

if url and key:
    try:
        supabase = create_client(url, key)
    except Exception as e:
        print(f"Failed to initialize Supabase client: {e}")
else:
    print("Supabase URL or Key not found in environment variables.")
