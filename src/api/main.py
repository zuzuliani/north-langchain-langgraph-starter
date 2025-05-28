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

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Get the current user's ID from the JWT token"""
    try:
        # Here you would typically verify the JWT token with Supabase
        # For now, we'll just return the token as the user_id
        # In production, you should properly verify the token
        return credentials.credentials
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )

# Basic health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

# Business Analyst Chat endpoint with streaming
@app.post("/chat/business-analyst")
async def chat_with_business_analyst(
    request: ChatRequest,
    user_id: str = Depends(get_current_user)
):
    try:
        # Generate a new session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Create streaming response
        return StreamingResponse(
            business_analyst.generate_response(
                request.message,
                session_id,
                user_id
            ),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 