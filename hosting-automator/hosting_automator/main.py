"""Main orchestrator for Hosting Automator"""

import logging
import sys
from typing import Optional

from .core.config import Config
from .core.logging import setup_logging
from .services.supabase_client import SupabaseService
from .services.cloudpanel_client import CloudPanelService
from .services.matomo_client import MatomoService

# Setup logging
logger = setup_logging()


class HostingAutomator:
    """Main class for hosting automation workflow"""
    
    def __init__(self):
        """Initialize the automator"""
        logger.info("Initializing Hosting Automator...")
        
        try:
            # Initialize services
            self.supabase = SupabaseService()
            self.cloudpanel = None
            self.matomo = None
            
        except Exception as e:
            logger.error(f"Failed to initialize Hosting Automator: {e}")
            raise
    
    def run(self, site_id: Optional[str] = None) -> None:
        """
        Run the hosting automation workflow
        
        Args:
            site_id: Optional specific site ID to process
        """
        logger.info("Starting hosting automation workflow...")
        
        try:
            # Get site ID from config if not provided
            if not site_id:
                site_id = Config.SITE_ID
            
            # Fetch pending sites
            sites = self.supabase.fetch_pending_hosting_sites(site_id)
            
            if not sites:
                logger.info("No sites pending hosting setup")
                return
            
            # Get server credentials for SSH
            server_config = self.supabase.get_server_credentials()
            
            # Initialize CloudPanel service with SSH connection
            self.cloudpanel = CloudPanelService(server_config)
            self.cloudpanel.connect()
            
            # Get Matomo credentials if available
            matomo_config = self.supabase.get_matomo_credentials()
            self.matomo = MatomoService(matomo_config)
            
            # Process each site
            for site in sites:
                self._process_site(site)
            
        except Exception as e:
            logger.error(f"Fatal error in hosting automation: {e}")
            raise
        
        finally:
            # Ensure SSH connection is closed
            if self.cloudpanel:
                self.cloudpanel.disconnect()
            
            logger.info("Hosting automation workflow completed")
    
    def _process_site(self, site: dict) -> None:
        """
        Process hosting setup for a single site
        
        Args:
            site: Site record from database
        """
        domain = site.get("domain")
        site_id = site.get("id")
        
        logger.info(f"Processing hosting for site: {domain} (ID: {site_id})")
        
        try:
            # Step 1: Create site in CloudPanel
            logger.info(f"Creating CloudPanel site for {domain}...")
            success, doc_root, error = self.cloudpanel.create_site(domain)
            
            if not success:
                logger.error(f"Failed to create CloudPanel site: {error}")
                self.supabase.update_site_hosting_status(
                    site_id, 
                    "failed", 
                    error_message=error
                )
                return
            
            # Step 2: Provision SSL certificate
            logger.info(f"Provisioning SSL certificate for {domain}...")
            ssl_success, ssl_error = self.cloudpanel.provision_ssl(domain)
            
            if not ssl_success:
                logger.error(f"Failed to provision SSL: {ssl_error}")
                self.supabase.update_site_hosting_status(
                    site_id, 
                    "failed",
                    doc_root=doc_root,
                    error_message=f"SSL provisioning failed: {ssl_error}"
                )
                return
            
            # Step 3: Create Matomo tracking site (optional)
            matomo_id = None
            if self.matomo and self.matomo.enabled:
                logger.info(f"Creating Matomo tracking site for {domain}...")
                
                # Check if site already exists
                existing_id = self.matomo.check_site_exists(domain)
                if existing_id:
                    logger.info(f"Matomo site already exists with ID {existing_id}")
                    matomo_id = existing_id
                else:
                    matomo_id, matomo_error = self.matomo.create_tracking_site(domain)
                    
                    if matomo_error:
                        # Log warning but don't fail the entire process
                        logger.warning(f"Failed to create Matomo site: {matomo_error}")
            
            # Step 4: Update status to active
            logger.info(f"Updating site status to active...")
            self.supabase.update_site_hosting_status(
                site_id,
                "active",
                doc_root=doc_root,
                matomo_id=matomo_id
            )
            
            logger.info(f"Successfully completed hosting setup for {domain}")
            
        except Exception as e:
            error_msg = f"Unexpected error processing site: {e}"
            logger.error(error_msg)
            
            # Update status to failed
            self.supabase.update_site_hosting_status(
                site_id,
                "failed",
                error_message=error_msg
            )


def main():
    """Main entry point for the script"""
    try:
        # Create and run automator
        automator = HostingAutomator()
        automator.run()
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()