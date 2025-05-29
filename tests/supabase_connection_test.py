import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_USERNAME = os.getenv("SUPABASE_USERNAME")
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD")

def test_supabase_connection():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        return
    if not SUPABASE_USERNAME or not SUPABASE_PASSWORD:
        print("SUPABASE_USERNAME and SUPABASE_PASSWORD must be set in .env file")
        return
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        response = supabase.auth.sign_in_with_password({
            "email": SUPABASE_USERNAME,
            "password": SUPABASE_PASSWORD
        })
        session = response.session
        if session and session.access_token:
            print("Supabase authentication successful!")
            print(f"Access token (first 20 chars): {session.access_token[:20]}...")
        else:
            print("Failed to obtain access token from Supabase.")
    except Exception as e:
        print(f"Error connecting to Supabase: {str(e)}")

if __name__ == "__main__":
    test_supabase_connection() 