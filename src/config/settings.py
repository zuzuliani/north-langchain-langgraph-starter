from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "LLM Agent API"
    
    # LLM Settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Database Settings
    _supabase_url: Optional[str] = os.getenv("SUPABASE_URL")
    _supabase_key: Optional[str] = os.getenv("SUPABASE_KEY")
    
    # Redis Settings (for Railway)
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    
    class Config:
        case_sensitive = True

    @property
    def SUPABASE_URL(self) -> Optional[str]:
        return self._supabase_url

    @SUPABASE_URL.setter
    def SUPABASE_URL(self, value: str):
        self._supabase_url = value

    @property
    def SUPABASE_KEY(self) -> Optional[str]:
        return self._supabase_key

    @SUPABASE_KEY.setter
    def SUPABASE_KEY(self, value: str):
        self._supabase_key = value

settings = Settings() 