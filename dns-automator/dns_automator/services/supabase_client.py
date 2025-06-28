"""Supabase client for database interactions"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from uuid import UUID

from supabase import create_client, Client
from ..core.config import settings

logger = logging.getLogger(__name__)


class SupabaseService:
    """Service for interacting with Supabase database"""
    
    def __init__(self):
        """Initialize Supabase client"""
        if not settings.supabase_url or not settings.supabase_service_key:
            raise ValueError("Supabase credentials not configured")
            
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_key
        )
        logger.info("Supabase client initialized")
    
    def fetch_pending_dns_sites(self, site_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch sites with pending DNS status
        
        Args:
            site_id: Optional specific site ID to process
            
        Returns:
            List of site records
        """
        try:
            query = self.client.table("sites").select("*")
            
            if site_id:
                query = query.eq("id", site_id)
            else:
                query = query.eq("status_dns", "pending")
            
            response = query.execute()
            sites = response.data
            
            logger.info(f"Fetched {len(sites)} pending DNS sites")
            return sites
            
        except Exception as e:
            logger.error(f"Error fetching pending sites: {e}")
            return []
    
    def fetch_cloudflare_account(self, account_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch Cloudflare account details
        
        Args:
            account_id: UUID of the Cloudflare account
            
        Returns:
            Account record or None
        """
        try:
            response = self.client.table("cloudflare_accounts").select("*").eq("id", account_id).single().execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching Cloudflare account {account_id}: {e}")
            return None
    
    def fetch_domain_registrar_credentials(self, registrar_type: str = "namecheap") -> Optional[Dict[str, Any]]:
        """
        Fetch domain registrar credentials from the database
        
        Args:
            registrar_type: Type of registrar (namecheap or spaceship)
            
        Returns:
            Credentials record or None
        """
        try:
            response = self.client.table("registrar_credentials").select("*").eq("provider", registrar_type).single().execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching {registrar_type} credentials: {e}")
            return None
    
    def fetch_default_server(self) -> Optional[Dict[str, Any]]:
        """
        Fetch the default server configuration
        
        Returns:
            Server record or None
        """
        try:
            response = self.client.table("servers").select("*").eq("is_default", True).single().execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching default server: {e}")
            return None
    
    def update_site_status(self, site_id: str, status: str, error_message: Optional[str] = None) -> bool:
        """
        Update site DNS status
        
        Args:
            site_id: UUID of the site
            status: New status (active, failed)
            error_message: Optional error message if failed
            
        Returns:
            Success boolean
        """
        try:
            update_data = {
                "status_dns": status,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if error_message:
                update_data["error_message"] = error_message
            elif status == "active":
                # Clear error message on success
                update_data["error_message"] = None
            
            response = self.client.table("sites").update(update_data).eq("id", site_id).execute()
            
            logger.info(f"Updated site {site_id} DNS status to {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating site {site_id} status: {e}")
            return False