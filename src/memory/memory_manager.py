from typing import Any, Dict, Optional
import redis
from supabase import create_client, Client
from src.config.settings import settings
import os
import httpx
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self):
        # Initialize Redis client for short-term memory
        self.redis_client = redis.from_url(settings.REDIS_URL) if settings.REDIS_URL else None
        
        # Initialize Supabase client for long-term memory
        self.supabase_url = os.getenv("SUPABASE_URL") or settings.SUPABASE_URL
        self.supabase_key = os.getenv("SUPABASE_KEY") or settings.SUPABASE_KEY
        if not self.supabase_url or not self.supabase_key:
            raise Exception("Supabase URL and Key must be set in environment variables or settings.")
        logger.info("MemoryManager initialized with Supabase URL and key")

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

    async def store_long_term(self, table: str, data: Dict[str, Any], jwt_token: str) -> Dict[str, Any]:
        url = f"{self.supabase_url}/rest/v1/{table}"
        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        logger.info(f"Storing data in {table}")
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)
            if response.status_code not in (200, 201):
                logger.error(f"Failed to store in Supabase: {response.text}")
                raise Exception(f"Failed to store in Supabase: {response.text}")
            logger.info(f"Successfully stored data in {table}")
            return response.json()

    async def update_long_term(self, table: str, id: str, data: Dict[str, Any], jwt_token: str) -> Dict[str, Any]:
        url = f"{self.supabase_url}/rest/v1/{table}?id=eq.{id}"
        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        logger.info(f"Updating record {id} in {table}")
        async with httpx.AsyncClient() as client:
            response = await client.patch(url, headers=headers, json=data)
            if response.status_code != 200:
                logger.error(f"Failed to update in Supabase: {response.text}")
                raise Exception(f"Failed to update in Supabase: {response.text}")
            logger.info(f"Successfully updated record {id} in {table}")
            return response.json()

    async def get_long_term(self, table: str, query: Dict[str, Any], jwt_token: str) -> Dict[str, Any]:
        url = f"{self.supabase_url}/rest/v1/{table}"
        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }
        # Build query string
        params = {}
        for k, v in query.items():
            params[k] = f"eq.{v}"
        logger.info(f"Fetching data from {table} with query: {params}")
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            if response.status_code != 200:
                logger.error(f"Failed to fetch from Supabase: {response.text}")
                raise Exception(f"Failed to fetch from Supabase: {response.text}")
            logger.info(f"Successfully fetched data from {table}")
            return response.json()

# Create a singleton instance
memory_manager = MemoryManager() 