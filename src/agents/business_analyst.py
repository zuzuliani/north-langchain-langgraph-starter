from typing import AsyncGenerator, Dict, Any
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.callbacks.streaming import StreamingStdOutCallbackHandler
from src.memory.memory_manager import memory_manager
from src.config.settings import settings
import json
from datetime import datetime

class BusinessAnalystAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",  # or gpt-3.5-turbo if you prefer
            temperature=0.7,
            streaming=True,
            callbacks=[StreamingStdOutCallbackHandler()]
        )
        
        # System message to define the agent's role and capabilities
        self.system_message = SystemMessage(content="""You are an experienced Business Analyst Consultant. 
        Your role is to help clients understand their business needs, analyze problems, and propose solutions.
        You should:
        - Ask clarifying questions to understand the business context
        - Provide data-driven insights and recommendations
        - Explain complex concepts in simple terms
        - Be professional but conversational
        - Focus on practical, actionable advice""")

    async def get_conversation_history(self, session_id: str, user_id: str) -> list:
        """Retrieve conversation history from Supabase"""
        try:
            history = await memory_manager.get_long_term(
                table="conversations",
                query={
                    "session_id": session_id,
                    "user_id": user_id,
                    "is_archived": False
                }
            )
            return history if history else []
        except Exception as e:
            print(f"Error retrieving conversation history: {e}")
            return []

    async def save_conversation(self, session_id: str, user_id: str, message: Dict[str, Any], is_first_message: bool = False):
        """Save conversation to Supabase"""
        try:
            # Prepare metadata
            metadata = {
                "message_type": "text",
                "formatting": "markdown",
                "is_first_message": is_first_message
            }

            # For the first message, generate a title
            title = None
            if is_first_message:
                title = message["content"][:100] + "..." if len(message["content"]) > 100 else message["content"]

            await memory_manager.store_long_term(
                table="conversations",
                data={
                    "session_id": session_id,
                    "user_id": user_id,
                    "role": message["role"],
                    "content": message["content"],
                    "title": title,
                    "metadata": json.dumps(metadata),
                    "created_at": datetime.utcnow().isoformat(),
                    "last_updated_at": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            print(f"Error saving conversation: {e}")

    async def generate_response(self, user_input: str, session_id: str, user_id: str) -> AsyncGenerator[str, None]:
        """Generate streaming response from the agent"""
        try:
            # Get conversation history
            history = await self.get_conversation_history(session_id, user_id)
            
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
            }, is_first_message=is_first_message)
            
            # Generate and stream response
            response_content = ""
            async for chunk in self.llm.astream(messages):
                if chunk.content:
                    response_content += chunk.content
                    yield chunk.content
            
            # Save agent response
            await self.save_conversation(session_id, user_id, {
                "role": "assistant",
                "content": response_content
            })
            
        except Exception as e:
            error_message = f"Error generating response: {str(e)}"
            print(error_message)
            yield error_message

# Create a singleton instance
business_analyst = BusinessAnalystAgent() 