from typing import AsyncGenerator, Dict, Any
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from src.memory.memory_manager import memory_manager
from src.config.settings import settings
import json
from datetime import datetime
import traceback

class BusinessAnalystAgent:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in environment variables")
            
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.7,
            streaming=True,
            api_key=settings.OPENAI_API_KEY
        )
        
        self.system_message = SystemMessage(content="""You are an experienced Business Analyst Consultant. 
        Your role is to help clients understand their business needs, analyze problems, and propose solutions.
        You should:
        - Ask clarifying questions to understand the business context
        - Provide data-driven insights and recommendations
        - Explain complex concepts in simple terms
        - Be professional but conversational
        - Focus on practical, actionable advice""")

    async def get_conversation_history(self, session_id: str, user_id: str, jwt_token: str) -> list:
        """Retrieve conversation history from Supabase"""
        try:
            history = await memory_manager.get_long_term(
                table="conversations",
                query={
                    "session_id": session_id,
                    "user_id": user_id,
                    "is_archived": False
                },
                jwt_token=jwt_token
            )
            return history if history else []
        except Exception as e:
            print(f"Error retrieving conversation history: {str(e)}")
            print(traceback.format_exc())
            return []

    async def save_conversation(self, session_id: str, user_id: str, message: Dict[str, Any], jwt_token: str, is_first_message: bool = False):
        """Save conversation to Supabase"""
        try:
            metadata = {
                "message_type": "text",
                "formatting": "markdown",
                "is_first_message": is_first_message
            }
            title = None
            if is_first_message:
                title = message["content"][:100] + "..." if len(message["content"]) > 100 else message["content"]
            data_to_insert = {
                "session_id": session_id,
                "user_id": user_id,
                "role": message["role"],
                "content": message["content"],
                "title": title,
                "metadata": json.dumps(metadata),
                "created_at": datetime.utcnow().isoformat(),
                "last_updated_at": datetime.utcnow().isoformat()
            }
            print(f"[save_conversation] Inserting data: {data_to_insert}")
            await memory_manager.store_long_term(
                table="conversations",
                data=data_to_insert,
                jwt_token=jwt_token
            )
        except Exception as e:
            print(f"Error saving conversation: {str(e)}")
            print(traceback.format_exc())

    async def generate_response(self, user_input: str, session_id: str, user_id: str, jwt_token: str) -> AsyncGenerator[str, None]:
        """Generate streaming response from the agent"""
        try:
            print(f"Starting response generation for session {session_id}")
            
            # Get conversation history
            history = await self.get_conversation_history(session_id, user_id, jwt_token)
            print(f"Retrieved {len(history)} messages from history")
            
            # Check if this is the first message
            is_first_message = len(history) == 0
            
            # Prepare messages for the LLM
            messages = [self.system_message]
            
            # Add conversation history
            for msg in history:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    messages.append(SystemMessage(content=msg["content"]))
            
            # Add current user input
            messages.append(HumanMessage(content=user_input))
            
            # Save user message
            await self.save_conversation(session_id, user_id, {
                "role": "user",
                "content": user_input
            }, jwt_token=jwt_token, is_first_message=is_first_message)
            
            print("Generating response from LLM...")
            # Generate and stream response
            response_content = ""
            async for chunk in self.llm.astream(messages):
                if chunk.content:
                    response_content += chunk.content
                    yield chunk.content
            
            print("Saving response to database...")
            # Save agent response
            await self.save_conversation(session_id, user_id, {
                "role": "assistant",
                "content": response_content
            }, jwt_token=jwt_token)
            
        except Exception as e:
            error_message = f"Error generating response: {str(e)}"
            print(error_message)
            print(traceback.format_exc())
            yield error_message

# Create a singleton instance
business_analyst = BusinessAnalystAgent() 