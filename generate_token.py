import os
from dotenv import load_dotenv
from supabase import create_client
import getpass

load_dotenv()

def generate_token():
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        return
    
    # Create Supabase client
    supabase = create_client(supabase_url, supabase_key)
    
    # Get user credentials
    email = os.getenv("SUPABASE_USERNAME")
    password = os.getenv("SUPABASE_PASSWORD")
    
    if not email or not password:
        print("Error: SUPABASE_USERNAME and SUPABASE_PASSWORD must be set in .env file")
        return
    
    try:
        # Sign in with email and password
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        # Get the session
        session = response.session
        
        if session and session.access_token:
            print("\nAuthentication successful!")
            print("\nAdd this to your .env file:")
            print(f"SUPABASE_JWT_TOKEN={session.access_token}")
            
            # Also print the JWT secret for reference
            print("\nMake sure you have this in your .env file:")
            print("SUPABASE_JWT_SECRET=your-jwt-secret-from-supabase-dashboard")
            print("\nYou can find the JWT secret in your Supabase dashboard under:")
            print("Project Settings -> API -> JWT Settings -> JWT Secret")
        else:
            print("Error: No access token in response")
            
    except Exception as e:
        print(f"Error during authentication: {str(e)}")

if __name__ == "__main__":
    generate_token() 