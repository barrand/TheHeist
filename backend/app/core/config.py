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
    allowed_origins: list[str] = ["http://localhost:8087", "http://localhost:3000"]
    
    # Gemini API Configuration
    gemini_api_key: str
    gemini_model: str = "models/gemini-2.5-flash"
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings
    Use @lru_cache to load settings once and reuse across requests
    """
    return Settings()
