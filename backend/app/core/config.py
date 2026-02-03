"""
Configuration Management
Load and validate environment variables and application settings
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Configuration
    app_name: str = "The Heist Backend"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS Configuration
    allowed_origins: list[str] = [
        "http://localhost:8087",
        "http://localhost:8088",
        "http://localhost:8089",
        "http://localhost:8090",
        "http://localhost:3000",
    ]
    
    # Gemini API Configuration (centralized model settings)
    gemini_api_key: str
    # Experience Generation: Long-form heist creation (handled by scripts)
    gemini_experience_model: str = "gemini-2.5-flash"
    # NPC Interactions: Real-time dialogue during gameplay
    gemini_npc_model: str = "gemini-2.0-flash-lite"
    # Quick Response Suggestions: Player chat helpers
    gemini_quick_response_model: str = "gemini-2.0-flash-lite"
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = "../.env"  # Load from project root
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings
    Use @lru_cache to load settings once and reuse across requests
    """
    # Force load from .env file, ignoring environment variables
    import os
    from dotenv import load_dotenv
    
    # Load .env and override any existing environment variables
    load_dotenv("../.env", override=True)
    
    return Settings()
