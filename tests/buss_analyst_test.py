import os
from dotenv import load_dotenv
import httpx
import asyncio
from supabase import create_client

load_dotenv()

API_URL = "http://127.0.0.1:8000/chat/business-analyst"
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_USERNAME = os.getenv("SUPABASE_USERNAME")
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD")

# Fetch JWT token using Supabase credentials
def get_jwt_token():
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    if not SUPABASE_USERNAME or not SUPABASE_PASSWORD:
        raise ValueError("SUPABASE_USERNAME and SUPABASE_PASSWORD must be set in .env file")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    response = supabase.auth.sign_in_with_password({
        "email": SUPABASE_USERNAME,
        "password": SUPABASE_PASSWORD
    })
    session = response.session
    if session and session.access_token:
        print("[buss_analyst_test] JWT Token:", session.access_token)
        return session.access_token
    else:
        raise Exception("Failed to obtain JWT token from Supabase.")

JWT_TOKEN = get_jwt_token()

payload = {
    "message": "What have we discussed so far?",
    "session_id": "test-session",
    "supabase_url": SUPABASE_URL,
    "supabase_key": SUPABASE_KEY
}

headers = {
    "Authorization": f"Bearer {JWT_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "text/event-stream"
}

async def make_request():
    try:
        print("Starting test request...")
        print(f"Using Supabase URL: {SUPABASE_URL}")
        print(f"Using JWT Token: {JWT_TOKEN[:10]}...")  # Only show first 10 chars for security
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", API_URL, headers=headers, json=payload, timeout=None) as response:
                print(f"\nStatus code: {response.status_code}")
                if response.status_code != 200:
                    error_text = await response.aread()
                    print(f"Error: {error_text.decode()}")
                    return
                print("\nResponse:")
                async for chunk in response.aiter_text():
                    if chunk:
                        print(chunk, end="", flush=True)
    except httpx.RequestError as e:
        print(f"Request error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        import traceback
        print(traceback.format_exc())

def main():
    asyncio.run(make_request())

if __name__ == "__main__":
    main() 