"""Configuration for DNS Automator when called from Management Hub API"""

from typing import Optional
from pydantic import BaseModel


class InjectedConfig(BaseModel):
    """Configuration injected by the Management Hub API"""
    
    # Supabase credentials
    supabase_url: str
    supabase_service_key: str
    
    # Optional parameters
    site_id: Optional[str] = None
    log_level: str = "INFO"