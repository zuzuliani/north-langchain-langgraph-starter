from typing import Any, Dict, Optional
import redis
from supabase import create_client, Client
from src.config.settings import settings

class MemoryManager:
    def __init__(self):
        # Initialize Redis client for short-term memory
        self.redis_client = redis.from_url(settings.REDIS_URL) if settings.REDIS_URL else None
        
        # Initialize Supabase client for long-term memory
        if settings.SUPABASE_URL and settings.SUPABASE_KEY:
            self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        else:
            self.supabase = None

    async def store_short_term(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Store data in Redis with TTL (default 1 hour)"""
        if not self.redis_client:
            raise Exception("Redis client not initialized")
        try:
            return self.redis_client.setex(key, ttl, str(value))
        except Exception as e:
            raise Exception(f"Failed to store in Redis: {str(e)}")

    async def get_short_term(self, key: str) -> Optional[str]:
        """Retrieve data from Redis"""
        if not self.redis_client:
            raise Exception("Redis client not initialized")
        try:
            return self.redis_client.get(key)
        except Exception as e:
            raise Exception(f"Failed to retrieve from Redis: {str(e)}")

    async def store_long_term(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Store data in Supabase"""
        if not self.supabase:
            raise Exception("Supabase client not initialized")
        try:
            response = self.supabase.table(table).insert(data).execute()
            return response.data
        except Exception as e:
            raise Exception(f"Failed to store in Supabase: {str(e)}")

    async def get_long_term(self, table: str, query: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve data from Supabase"""
        if not self.supabase:
            raise Exception("Supabase client not initialized")
        try:
            response = self.supabase.table(table).select("*").match(query).execute()
            return response.data
        except Exception as e:
            raise Exception(f"Failed to retrieve from Supabase: {str(e)}")

# Create a singleton instance
memory_manager = MemoryManager() 