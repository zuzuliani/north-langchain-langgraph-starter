import httpx
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = "http://127.0.0.1:8000/chat/business-analyst"
JWT_TOKEN = os.getenv("SUPABASE_KEY")  # Loaded from .env

payload = {
    "message": "What are some KPIs for SaaS businesses?",
    "session_id": "test-session"
}

headers = {
    "Authorization": f"Bearer {JWT_TOKEN}",
    "Content-Type": "application/json"
}

def main():
    with httpx.stream("POST", API_URL, headers=headers, json=payload, timeout=None) as response:
        print(f"Status code: {response.status_code}")
        print("Response:")
        for chunk in response.iter_text():
            print(chunk, end="", flush=True)

if __name__ == "__main__":
    main() 