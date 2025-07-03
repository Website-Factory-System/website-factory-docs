"""Configuration management for DNS Automator"""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Supabase database connection (using Railway shared variables)
    supabase_url: Optional[str] = Field(None, description="Supabase project URL")
    supabase_service_key: Optional[str] = Field(None, description="Supabase service role key")
    
    # Logging
    log_level: str = Field("INFO", description="Logging level")
    
    # Testing
    site_id: Optional[str] = Field(None, description="Specific site ID to process (for testing)")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create settings instance - will not fail if env vars are missing
settings = Settings()