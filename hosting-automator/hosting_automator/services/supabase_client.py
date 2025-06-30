"""Supabase client for Hosting Automator"""

import logging
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from ..core.config import Config

logger = logging.getLogger("hosting_automator")


class SupabaseService:
    """Service for interacting with Supabase"""
    
    def __init__(self):
        """Initialize Supabase client"""
        Config.validate()
        self.client: Client = create_client(
            Config.SUPABASE_URL,
            Config.SUPABASE_SERVICE_KEY
        )
        logger.info("Supabase client initialized")
    
    def fetch_pending_hosting_sites(self, site_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch sites that need hosting setup
        
        Args:
            site_id: Optional specific site ID to process
            
        Returns:
            List of site records
        """
        try:
            query = self.client.table("sites").select("*")
            
            if site_id:
                # Process specific site
                query = query.eq("id", site_id)
            else:
                # Process all pending sites
                query = query.eq("status_dns", "active").eq("status_hosting", "pending")
            
            response = query.execute()
            sites = response.data
            
            logger.info(f"Found {len(sites)} sites pending hosting setup")
            return sites
            
        except Exception as e:
            logger.error(f"Failed to fetch pending sites: {e}")
            raise
    
    def update_site_hosting_status(
        self, 
        site_id: str, 
        status: str,
        doc_root: Optional[str] = None,
        matomo_id: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> None:
        """
        Update site hosting status and metadata
        
        Args:
            site_id: Site ID to update
            status: New status ('active' or 'failed')
            doc_root: Document root path on server
            matomo_id: Matomo site ID
            error_message: Error message if failed
        """
        try:
            update_data = {"status_hosting": status}
            
            if doc_root:
                update_data["hosting_doc_root"] = doc_root
                
            if matomo_id:
                update_data["matomo_site_id"] = matomo_id
                
            if error_message:
                update_data["error_message"] = error_message
            
            self.client.table("sites").update(update_data).eq("id", site_id).execute()
            logger.info(f"Updated site {site_id} hosting status to: {status}")
            
        except Exception as e:
            logger.error(f"Failed to update site status: {e}")
            raise
    
    def get_server_credentials(self, server_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get server credentials for SSH connection
        
        Args:
            server_id: Optional server ID, defaults to first server
            
        Returns:
            Server credentials dictionary
        """
        try:
            query = self.client.table("servers").select("*")
            
            if server_id:
                query = query.eq("id", server_id)
            
            response = query.execute()
            
            if not response.data:
                raise ValueError("No server credentials found")
            
            # Use first server if no specific ID provided
            server = response.data[0]
            logger.info(f"Retrieved credentials for server: {server.get('name', 'unknown')}")
            
            return server
            
        except Exception as e:
            logger.error(f"Failed to fetch server credentials: {e}")
            raise
    
    def get_matomo_credentials(self) -> Optional[Dict[str, Any]]:
        """
        Get Matomo API credentials
        
        Returns:
            Matomo credentials dictionary or None
        """
        try:
            response = self.client.table("infrastructure_credentials")\
                .select("*")\
                .eq("service", "matomo")\
                .execute()
            
            if response.data:
                matomo = response.data[0]
                logger.info("Retrieved Matomo credentials")
                # Transform to expected format
                return {
                    "api_url": matomo.get("url"),
                    "api_token": matomo.get("api_token")
                }
            else:
                logger.warning("No Matomo credentials found")
                return None
                
        except Exception as e:
            logger.error(f"Failed to fetch Matomo credentials: {e}")
            return None