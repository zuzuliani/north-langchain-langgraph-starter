from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv
from fastapi.responses import StreamingResponse
from src.agents.business_analyst import business_analyst
import uuid
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client
from jose import jwt
from src.config.settings import settings
import traceback

# Load environment variables
load_dotenv()

app = FastAPI(
    title="LLM Agent API",
    description="API for LLM Agents with LangChain and LangGraph",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    request: ChatRequest = None
) -> str:
    """Get the current user's ID from the JWT token"""
    try:
        # Use provided Supabase credentials if available, otherwise fall back to environment variables
        supabase_url = request.supabase_url if request and request.supabase_url else settings.SUPABASE_URL
        supabase_key = request.supabase_key if request and request.supabase_key else settings.SUPABASE_KEY
        
        if not supabase_url or not supabase_key:
            raise ValueError("Supabase credentials not provided")
            
        # Create Supabase client
        supabase = create_client(supabase_url, supabase_key)
        
        # Get the JWT secret from Supabase
        jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
        print(f"JWT Secret being used: {jwt_secret}")
        if not jwt_secret:
            raise ValueError("SUPABASE_JWT_SECRET is not set in environment variables")
        
        # Verify the JWT token
        token = credentials.credentials
        try:
            # Attempt to decode the token using the JWT secret
            payload = jwt.decode(token, jwt_secret, algorithms=["HS256"], options={"verify_aud": False})
            user_id = payload.get("sub")
            if not user_id:
                raise ValueError("Invalid token payload")
            return user_id
        except jwt.JWTError as e:
            print(f"JWT verification failed: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail=f"Invalid token: {str(e)}"
            )
            
    except Exception as e:
        print(f"Authentication failed: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail=f"Authentication failed: {str(e)}"
        )

# Basic health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

# Business Analyst Chat endpoint with streaming
@app.post("/chat/business-analyst")
async def chat_with_business_analyst(
    request: ChatRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_id: str = Depends(get_current_user)
):
    try:
        print(f"Received chat request from user {user_id}")
        print(f"Message: {request.message}")
        print(f"Session ID: {request.session_id}")
        
        # Generate a new session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Update Supabase settings if credentials are provided
        if request.supabase_url and request.supabase_key:
            print("Updating Supabase settings with provided credentials")
            settings.SUPABASE_URL = request.supabase_url
            settings.SUPABASE_KEY = request.supabase_key
        
        print("Creating streaming response...")
        # Create streaming response
        return StreamingResponse(
            business_analyst.generate_response(
                request.message,
                session_id,
                user_id,
                credentials.credentials
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 