"""Main entry point for DNS Automator"""

import sys
import logging
from typing import Optional

from .core.config import settings
from .core.logging import setup_logging
from .services.supabase_client import SupabaseService
from .services.namecheap_client import NamecheapClient, NamecheapError
from .services.spaceship_client import SpaceshipClient, SpaceshipError
from .services.cloudflare_client import CloudflareClient, CloudflareError

# Setup logging
logger = setup_logging()


class DNSAutomator:
    """Main DNS automation orchestrator"""
    
    def __init__(self):
        """Initialize DNS Automator"""
        # Check if we have required settings
        if not settings.supabase_url or not settings.supabase_service_key:
            raise ValueError(
                "Supabase credentials not configured. "
                "Either set SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables "
                "or use the API service mode."
            )
        
        self.supabase = SupabaseService()
        self.registrar_clients = {}
        logger.info("DNS Automator initialized")
    
    def get_registrar_client(self, registrar_type: str):
        """
        Get or create registrar client
        
        Args:
            registrar_type: Type of registrar (namecheap or spaceship)
            
        Returns:
            Registrar client instance
        """
        if registrar_type in self.registrar_clients:
            return self.registrar_clients[registrar_type]
        
        # Fetch credentials from database
        creds = self.supabase.fetch_domain_registrar_credentials(registrar_type)
        
        if not creds:
            raise ValueError(f"No credentials found for {registrar_type} in database. Please configure via Management Hub Settings.")
        
        # Create client based on type
        if registrar_type == "namecheap":
            client = NamecheapClient(
                api_user=creds["api_user"],
                api_key=creds["api_key"],
                username=creds["username"],
                client_ip=creds["client_ip"]
            )
        elif registrar_type == "spaceship":
            client = SpaceshipClient(
                api_key=creds["api_key"],
                api_secret=creds["api_secret"]
            )
        else:
            raise ValueError(f"Unknown registrar type: {registrar_type}")
        
        self.registrar_clients[registrar_type] = client
        return client
    
    def process_site(self, site: dict) -> bool:
        """
        Process DNS configuration for a single site
        
        Args:
            site: Site record from database
            
        Returns:
            Success boolean
        """
        domain = site["domain"]
        site_id = site["id"]
        
        logger.info(f"Processing DNS for site: {domain} (ID: {site_id})")
        
        try:
            # Step 1: Fetch Cloudflare credentials
            cf_account_id = site["cloudflare_account_id"]
            logger.info(f"Fetching Cloudflare account: {cf_account_id}")
            cf_account = self.supabase.fetch_cloudflare_account(cf_account_id)
            if not cf_account:
                error_msg = f"Cloudflare account not found: {cf_account_id}"
                logger.error(error_msg)
                self.supabase.update_site_status(site_id, "failed", error_msg)
                return False
            
            logger.info(f"Found Cloudflare account: {cf_account['email']} ({cf_account['account_nickname']})")
            
            # Step 2: Create Cloudflare zone FIRST to get nameservers
            try:
                api_token = cf_account["api_token"]
                account_id = cf_account.get("cloudflare_account_id")
                logger.info(f"Using Cloudflare API token: {api_token[:10]}...{api_token[-4:]} (length: {len(api_token)})")
                logger.info(f"Using Cloudflare Account ID: {account_id[:8] if account_id else 'NOT SET'}...")
                
                if not account_id:
                    logger.warning("CRITICAL: Cloudflare Account ID not set in database! This will likely cause 'Invalid API key' errors.")
                    logger.warning("Please add the Account ID to the cloudflare_accounts table or via Management Hub Settings.")
                
                cf_client = CloudflareClient(api_token, account_id)
                
                # Create zone and get assigned nameservers
                zone_id, cloudflare_nameservers = cf_client.create_zone(domain)
                
                if not cloudflare_nameservers:
                    raise CloudflareError("No nameservers returned by Cloudflare")
                
                logger.info(f"Cloudflare assigned nameservers: {', '.join(cloudflare_nameservers)}")
                
                # Get hosting server IP from database
                server = self.supabase.fetch_default_server()
                if server:
                    server_ip = server["ip_address"]
                else:
                    raise CloudflareError("No default server configured in database. Please configure via Management Hub Settings.")
                
                # Create DNS records
                # A record for root domain
                cf_client.create_dns_record(
                    zone_id=zone_id,
                    record_type="A",
                    name="@",
                    content=server_ip,
                    proxied=True
                )
                
                # CNAME record for www
                cf_client.create_dns_record(
                    zone_id=zone_id,
                    record_type="CNAME",
                    name="www",
                    content=domain,
                    proxied=True
                )
                
                logger.info(f"Successfully configured Cloudflare DNS records for {domain}")
                
            except CloudflareError as e:
                error_msg = f"Cloudflare error: {str(e)}"
                logger.error(error_msg)
                self.supabase.update_site_status(site_id, "failed", error_msg)
                return False
            
            # Step 3: Update nameservers at registrar with Cloudflare's nameservers
            registrar_updated = False
            registrar_error = None
            
            # Try each registrar in order until one succeeds
            for registrar_type in ["namecheap", "spaceship"]:
                try:
                    registrar_client = self.get_registrar_client(registrar_type)
                    registrar_client.set_nameservers(domain, cloudflare_nameservers)
                    logger.info(f"Successfully updated nameservers at {registrar_type} for {domain}")
                    registrar_updated = True
                    break
                except ValueError as e:
                    # No credentials for this registrar, try next
                    logger.debug(f"No credentials for {registrar_type}: {e}")
                    continue
                except (NamecheapError, SpaceshipError) as e:
                    # API error, save it and try next registrar
                    registrar_error = str(e)
                    logger.warning(f"Failed with {registrar_type}: {e}")
                    continue
            
            if not registrar_updated:
                error_msg = registrar_error or "No registrar credentials configured"
                logger.error(f"Failed to update nameservers: {error_msg}")
                self.supabase.update_site_status(site_id, "failed", f"Registrar error: {error_msg}")
                return False
            
            # Step 4: Update status to active
            self.supabase.update_site_status(site_id, "active")
            logger.info(f"Successfully completed DNS configuration for {domain}")
            return True
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"Error processing site {domain}: {error_msg}")
            self.supabase.update_site_status(site_id, "failed", error_msg)
            return False
    
    def run(self):
        """Main execution method"""
        logger.info("Starting DNS Automator run")
        
        try:
            # Fetch pending sites
            sites = self.supabase.fetch_pending_dns_sites(settings.site_id)
            
            if not sites:
                logger.info("No pending DNS sites to process")
                return
            
            logger.info(f"Found {len(sites)} sites to process")
            
            # Process each site
            success_count = 0
            for site in sites:
                if self.process_site(site):
                    success_count += 1
            
            logger.info(f"DNS Automator run complete. Processed {success_count}/{len(sites)} sites successfully")
            
        except Exception as e:
            logger.error(f"Fatal error in DNS Automator: {e}")
            sys.exit(1)


def main():
    """Main entry point"""
    automator = DNSAutomator()
    automator.run()


if __name__ == "__main__":
    main()