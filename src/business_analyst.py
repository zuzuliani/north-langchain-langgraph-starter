from fastapi import Request, HTTPException
from fastapi.responses import StreamingResponse
from datetime import datetime

@app.post("/business_analyst")
async def business_analyst(request: Request):
    try:
        # Get the JWT token from the Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
        
        jwt_token = auth_header.split(" ")[1]
        
        # Get the request body
        body = await request.json()
        user_id = body.get("user_id")
        message = body.get("message")
        
        if not user_id or not message:
            raise HTTPException(status_code=400, detail="Missing user_id or message")
        
        # Stream the response
        async def generate():
            full_response = ""
            async for chunk in business_analyst_agent.ainvoke({"input": message}):
                if chunk:
                    full_response += chunk
                    yield chunk
            
            # After streaming is complete, save to Supabase
            conversation_data = {
                "user_id": user_id,
                "message": message,
                "response": full_response,
                "created_at": datetime.utcnow().isoformat()
            }
            await memory_manager.store_long_term("conversations", conversation_data, jwt_token)
        
        return StreamingResponse(generate(), media_type="text/plain")
        
    except Exception as e:
        print(f"Error in business_analyst endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 