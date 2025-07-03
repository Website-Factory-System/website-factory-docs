"""Main entry point for DNS Automator"""

print("🟢 DEBUG: dns_automator/main.py module loading...")

import sys
import logging
from typing import Optional
from datetime import datetime

print("🟢 DEBUG: Basic imports done, loading local modules...")

from .core.config import settings
print("🟢 DEBUG: config imported")

from .core.logging import setup_logging
print("🟢 DEBUG: logging imported")

from .services.supabase_client import SupabaseService
print("🟢 DEBUG: supabase_client imported")

# Hub API client removed - using shared Railway variables instead

from .services.namecheap_client import NamecheapClient, NamecheapError
print("🟢 DEBUG: namecheap_client imported")

from .services.spaceship_client import SpaceshipClient, SpaceshipError
print("🟢 DEBUG: spaceship_client imported")

from .services.cloudflare_client import CloudflareClient, CloudflareError
print("🟢 DEBUG: cloudflare_client imported")

# Setup logging
print("🟢 DEBUG: Setting up logging...")
logger = setup_logging()
print("🟢 DEBUG: Logger setup complete")
print("🟢 DEBUG: dns_automator/main.py module loaded successfully")


class DNSAutomator:
    """Main DNS automation orchestrator"""
    
    def __init__(self):
        """Initialize DNS Automator"""
        print("🟢 DEBUG: DNSAutomator.__init__() called")
        logger.info("🟢 DEBUG: DNSAutomator.__init__() called")
        
        # Initialize Supabase client using Railway shared variables
        print("🟢 DEBUG: Initializing Supabase client with shared Railway variables...")
        
        if not settings.supabase_url or not settings.supabase_service_key:
            raise ValueError(
                "Supabase credentials not configured. "
                "Please ensure SUPABASE_URL and SUPABASE_SERVICE_KEY are set as Railway shared variables."
            )
        
        self.data_client = SupabaseService()
        
        self.registrar_clients = {}
        print("🟢 DEBUG: DNSAutomator initialization complete")
        logger.info("DNS Automator initialized")
    
    def get_registrar_client(self, registrar_type: str):
        """
        Get or create registrar client
        
        Args:
            registrar_type: Type of registrar (namecheap or spaceship)
            
        Returns:
            Registrar client instance
        """
        print(f"🟢 DEBUG: get_registrar_client() called with registrar_type='{registrar_type}'")
        logger.info(f"🟢 DEBUG: get_registrar_client() called with registrar_type='{registrar_type}'")
        
        if registrar_type in self.registrar_clients:
            print(f"🟢 DEBUG: Using cached {registrar_type} client")
            logger.debug(f"Using cached {registrar_type} client")
            return self.registrar_clients[registrar_type]
        
        print(f"🟢 DEBUG: Fetching {registrar_type} credentials from database...")
        logger.info(f"🔑 Fetching {registrar_type} credentials from database...")
        
        # Fetch credentials from database
        creds = self.data_client.get_registrar_credentials(registrar_type)
        
        if not creds:
            error_msg = f"No credentials found for {registrar_type} in database"
            logger.error(f"❌ {error_msg}")
            logger.error(f"   Please configure {registrar_type} credentials via Management Hub Settings")
            logger.error(f"   Required fields for {registrar_type}:")
            if registrar_type == "namecheap":
                logger.error(f"   - api_user (Namecheap username)")
                logger.error(f"   - api_key (Namecheap API key)")
                logger.error(f"   - username (typically same as api_user)")
                logger.error(f"   - client_ip (whitelisted IP address)")
            elif registrar_type == "spaceship":
                logger.error(f"   - api_key (Spaceship API key)")
                logger.error(f"   - api_secret (Spaceship API secret)")
            raise ValueError(error_msg + ". Please configure via Management Hub Settings.")
        
        logger.info(f"✅ Found {registrar_type} credentials in database")
        logger.info(f"   Validating required fields...")
        
        # Validate credentials structure for each registrar type
        if registrar_type == "namecheap":
            required_fields = ["api_user", "api_key", "username", "client_ip"]
            logger.info(f"   Namecheap requires: {', '.join(required_fields)}")
            
            missing_fields = []
            for field in required_fields:
                if field not in creds or not creds[field]:
                    missing_fields.append(field)
                else:
                    # Show field status (with masking for sensitive data)
                    if field == "api_key":
                        value_display = f"{creds[field][:8]}..." if len(creds[field]) > 8 else "***"
                    else:
                        value_display = creds[field]
                    logger.info(f"   ✅ {field}: {value_display}")
            
            if missing_fields:
                error_msg = f"Missing required Namecheap credentials: {', '.join(missing_fields)}"
                logger.error(f"❌ {error_msg}")
                logger.error(f"   Current credentials in database:")
                for key, value in creds.items():
                    if key == "api_key":
                        display_value = f"{value[:8]}..." if value and len(value) > 8 else "***" if value else "NOT SET"
                    else:
                        display_value = value if value else "NOT SET"
                    logger.error(f"     {key}: {display_value}")
                raise ValueError(error_msg)
                
            logger.info(f"✅ All required Namecheap fields present")
            logger.info(f"   Creating Namecheap client...")
            
            client = NamecheapClient(
                api_user=creds["api_user"],
                api_key=creds["api_key"],
                username=creds["username"],
                client_ip=creds["client_ip"]
            )
            
        elif registrar_type == "spaceship":
            required_fields = ["api_key", "api_secret"]
            logger.info(f"   Spaceship requires: {', '.join(required_fields)}")
            
            missing_fields = []
            for field in required_fields:
                if field not in creds or not creds[field]:
                    missing_fields.append(field)
                else:
                    # Show field status (with masking)
                    value_display = f"{creds[field][:8]}..." if len(creds[field]) > 8 else "***"
                    logger.info(f"   ✅ {field}: {value_display}")
            
            if missing_fields:
                error_msg = f"Missing required Spaceship credentials: {', '.join(missing_fields)}"
                logger.error(f"❌ {error_msg}")
                raise ValueError(error_msg)
                
            logger.info(f"✅ All required Spaceship fields present")
            logger.info(f"   Creating Spaceship client...")
            
            client = SpaceshipClient(
                api_key=creds["api_key"],
                api_secret=creds["api_secret"]
            )
        else:
            error_msg = f"Unknown registrar type: {registrar_type}"
            logger.error(f"❌ {error_msg}")
            logger.error(f"   Supported registrar types: namecheap, spaceship")
            raise ValueError(error_msg)
        
        logger.info(f"✅ {registrar_type.title()} client created successfully")
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
        print("🟢 DEBUG: process_site() called")
        print(f"🟢 DEBUG: process_site() called with site: {site}")
        
        domain = site["domain"]
        site_id = site["id"]
        
        print(f"🟢 DEBUG: Processing domain: {domain}, site_id: {site_id}")
        logger.info(f"🟢 DEBUG: process_site() called for domain: {domain}")
        logger.info(f"🚀 ===== STARTING DNS PROCESSING FOR {domain} =====")
        logger.info(f"Site ID: {site_id}")
        logger.info(f"Site data: {site}")
        
        try:
            # Step 1: Fetch Cloudflare credentials
            cf_account_id = site["cloudflare_account_id"]
            logger.info(f"📋 STEP 1: Fetching Cloudflare account credentials")
            logger.info(f"CF Account ID from site: {cf_account_id}")
            
            cf_account = self.data_client.get_cloudflare_account(cf_account_id)
            if not cf_account:
                error_msg = f"❌ STEP 1 FAILED: Cloudflare account not found: {cf_account_id}"
                logger.error(error_msg)
                self.data_client.update_site_status(site_id, "failed", error_msg)
                return False
            
            logger.info(f"✅ STEP 1 SUCCESS: Found Cloudflare account")
            logger.info(f"   Email: {cf_account['email']}")
            logger.info(f"   Nickname: {cf_account['account_nickname']}")
            logger.info(f"   API Token: {cf_account['api_token'][:10]}...{cf_account['api_token'][-4:]}")
            logger.info(f"   CF Account ID: {cf_account.get('cloudflare_account_id', 'NOT SET')}")
            
            # Step 2: Create Cloudflare zone FIRST to get nameservers
            logger.info(f"📋 STEP 2: Creating Cloudflare zone for {domain}")
            
            try:
                api_token = cf_account["api_token"]
                account_id = cf_account.get("cloudflare_account_id")
                
                logger.info(f"   API Token: {api_token[:10]}...{api_token[-4:]} (length: {len(api_token)})")
                logger.info(f"   Account ID: {account_id[:8] if account_id else 'NOT SET'}...")
                
                if not account_id:
                    error_msg = "❌ STEP 2 FAILED: Cloudflare Account ID not set in database!"
                    logger.error(error_msg)
                    logger.error("This will cause 'Invalid API key' errors. Please add Account ID via Management Hub Settings.")
                    self.data_client.update_site_status(site_id, "failed", error_msg)
                    return False
                
                logger.info(f"   Initializing Cloudflare client...")
                cf_client = CloudflareClient(api_token, account_id)
                
                # Create zone and get assigned nameservers
                logger.info(f"   Creating zone for {domain}...")
                zone_id, cloudflare_nameservers = cf_client.create_zone(domain)
                
                if not cloudflare_nameservers:
                    error_msg = "❌ STEP 2 FAILED: No nameservers returned by Cloudflare"
                    logger.error(error_msg)
                    self.data_client.update_site_status(site_id, "failed", error_msg)
                    return False
                
                logger.info(f"   ✅ Zone created! ID: {zone_id}")
                logger.info(f"   📋 Assigned nameservers: {', '.join(cloudflare_nameservers)}")
                
                # Get hosting server IP from database
                logger.info(f"   Fetching default server configuration...")
                server = self.data_client.fetch_default_server()
                if server:
                    server_ip = server["ip_address"]
                    logger.info(f"   Server IP: {server_ip}")
                else:
                    error_msg = "❌ STEP 2 FAILED: No default server configured in database"
                    logger.error(error_msg)
                    logger.error("Please configure via Management Hub Settings.")
                    self.data_client.update_site_status(site_id, "failed", error_msg)
                    return False
                
                # Create DNS records
                logger.info(f"   Creating DNS records...")
                
                # A record for root domain
                logger.info(f"   Creating A record: @ -> {server_ip}")
                cf_client.create_dns_record(
                    zone_id=zone_id,
                    record_type="A",
                    name="@",
                    content=server_ip,
                    proxied=True
                )
                
                # CNAME record for www
                logger.info(f"   Creating CNAME record: www -> {domain}")
                cf_client.create_dns_record(
                    zone_id=zone_id,
                    record_type="CNAME",
                    name="www",
                    content=domain,
                    proxied=True
                )
                
                logger.info(f"✅ STEP 2 SUCCESS: Cloudflare DNS configured for {domain}")
                
            except CloudflareError as e:
                error_msg = f"Cloudflare error: {str(e)}"
                logger.error(f"❌ STEP 2 FAILED - Cloudflare Error:")
                logger.error(f"   Error Message: {error_msg}")
                logger.error(f"   This usually indicates:")
                logger.error(f"   - Invalid or expired Cloudflare API token")
                logger.error(f"   - Missing Cloudflare Account ID")
                logger.error(f"   - Insufficient API token permissions")
                logger.error(f"   - Rate limiting or billing issues")
                self.data_client.update_site_status(site_id, "failed", error_msg)
                return False
            
            # Step 3: Update nameservers at registrar with Cloudflare's nameservers
            logger.info(f"📋 STEP 3: Updating nameservers at domain registrar")
            logger.info(f"   New nameservers to set: {', '.join(cloudflare_nameservers)}")
            
            registrar_updated = False
            registrar_error = None
            
            # Try each registrar in order until one succeeds
            for registrar_type in ["namecheap", "spaceship"]:
                logger.info(f"   🔄 Trying {registrar_type.title()} registrar...")
                try:
                    logger.info(f"   Fetching {registrar_type} credentials from database...")
                    registrar_client = self.get_registrar_client(registrar_type)
                    logger.info(f"   ✅ {registrar_type.title()} client initialized successfully")
                    
                    logger.info(f"   📡 Calling {registrar_type} API to set nameservers for {domain}...")
                    logger.info(f"      - Domain: {domain}")
                    logger.info(f"      - Nameservers: {cloudflare_nameservers}")
                    
                    registrar_client.set_nameservers(domain, cloudflare_nameservers)
                    
                    logger.info(f"✅ STEP 3 SUCCESS: Nameservers updated at {registrar_type.title()}")
                    logger.info(f"   Domain {domain} now points to Cloudflare nameservers")
                    registrar_updated = True
                    break
                    
                except ValueError as e:
                    # No credentials for this registrar, try next
                    logger.warning(f"   ⚠️  No credentials configured for {registrar_type}: {e}")
                    logger.info(f"   Skipping {registrar_type}, trying next registrar...")
                    continue
                    
                except (NamecheapError, SpaceshipError) as e:
                    # API error, save it and try next registrar
                    registrar_error = str(e)
                    logger.error(f"   ❌ {registrar_type.title()} API error:")
                    logger.error(f"     Error: {str(e)}")
                    logger.error(f"     Error Type: {type(e).__name__}")
                    logger.error(f"   Common causes for {registrar_type} errors:")
                    if registrar_type == "namecheap":
                        logger.error(f"     - Invalid API key or username")
                        logger.error(f"     - Client IP not whitelisted in Namecheap")
                        logger.error(f"     - Domain not managed by this Namecheap account")
                        logger.error(f"     - API rate limiting")
                    elif registrar_type == "spaceship":
                        logger.error(f"     - Invalid API key or secret")
                        logger.error(f"     - Domain not managed by this Spaceship account")
                        logger.error(f"     - API authentication issues")
                    logger.info(f"   Trying next registrar...")
                    continue
                    
                except Exception as e:
                    # Unexpected error
                    registrar_error = str(e)
                    logger.error(f"   ❌ Unexpected error with {registrar_type}: {e}")
                    logger.info(f"   Trying next registrar...")
                    continue
            
            if not registrar_updated:
                error_msg = registrar_error or "No registrar credentials configured"
                logger.error(f"❌ STEP 3 FAILED: Could not update nameservers at any registrar")
                logger.error(f"   Final error: {error_msg}")
                logger.error(f"   Available registrar types tried: namecheap, spaceship")
                logger.error(f"   Please check registrar credentials in Management Hub Settings")
                self.data_client.update_site_status(site_id, "failed", f"Registrar error: {error_msg}")
                return False
            
            # Step 4: Mark DNS configuration as complete
            logger.info(f"📋 STEP 4: Finalizing DNS configuration")
            logger.info(f"   Updating database status to 'active'...")
            
            self.data_client.update_site_status(site_id, "active")
            
            logger.info(f"✅ STEP 4 SUCCESS: Database updated")
            logger.info(f"")
            logger.info(f"🎉 ===== DNS PROCESSING COMPLETED SUCCESSFULLY FOR {domain} =====")
            logger.info(f"✅ All steps completed:")
            logger.info(f"   1. ✅ Cloudflare account fetched and validated")
            logger.info(f"   2. ✅ Cloudflare zone created with DNS records")
            logger.info(f"   3. ✅ Domain nameservers updated at registrar")
            logger.info(f"   4. ✅ Database status updated to 'active'")
            logger.info(f"")
            logger.info(f"🌐 Website {domain} is now configured and should be accessible!")
            logger.info(f"📡 DNS propagation may take 24-48 hours to complete globally")
            logger.info(f"")
            return True
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"")
            logger.error(f"💥 ===== UNEXPECTED ERROR DURING DNS PROCESSING FOR {domain} =====")
            logger.error(f"❌ Fatal error occurred: {error_msg}")
            logger.error(f"🔍 Exception type: {type(e).__name__}")
            logger.error(f"📍 This suggests a code issue rather than configuration problem")
            logger.error(f"🛠️  Please report this error to the development team")
            logger.error(f"")
            
            logger.info(f"📋 Updating database status to 'failed'...")
            self.data_client.update_site_status(site_id, "failed", error_msg)
            logger.info(f"✅ Database updated with error status")
            logger.error(f"")
            return False
    
    def run(self):
        """Main execution method"""
        print("🟢 DEBUG: run() method called")
        logger.info("🟢 DEBUG: run() method called")
        
        logger.info("=" * 80)
        logger.info("🚀 DNS AUTOMATOR STARTING UP")
        logger.info("=" * 80)
        logger.info(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("🟢 DEBUG: About to fetch pending DNS sites...")
        
        try:
            # Fetch pending sites
            logger.info(f"📋 Fetching pending DNS sites from database...")
            
            if settings.site_id:
                logger.info(f"🎯 Processing specific site ID: {settings.site_id}")
            else:
                logger.info(f"🔍 Processing all sites with status_dns = 'pending'")
                
            # Get site from data client (Hub API or Supabase)
            if settings.site_id:
                site = self.data_client.get_site(settings.site_id)
                sites = [site] if site else []
            else:
                # For Hub API mode, we'll implement batch processing later
                # For now, we expect a specific site_id
                sites = []
            
            if not sites:
                logger.info("✅ No pending DNS sites found to process")
                logger.info("🏁 DNS Automator run complete - nothing to do")
                return
            
            logger.info(f"📊 Found {len(sites)} site(s) to process")
            for i, site in enumerate(sites, 1):
                logger.info(f"   {i}. {site['domain']} (ID: {site['id']})")
            logger.info("")
            
            # Process each site
            success_count = 0
            failed_sites = []
            
            for i, site in enumerate(sites, 1):
                logger.info(f"🔄 Processing site {i}/{len(sites)}: {site['domain']}")
                
                if self.process_site(site):
                    success_count += 1
                    logger.info(f"✅ Site {i}/{len(sites)} completed successfully")
                else:
                    failed_sites.append(site['domain'])
                    logger.error(f"❌ Site {i}/{len(sites)} failed")
                
                logger.info("")  # Add spacing between sites
            
            # Final summary
            logger.info("=" * 80)
            logger.info("📊 DNS AUTOMATOR RUN SUMMARY")
            logger.info("=" * 80)
            logger.info(f"🎯 Total sites processed: {len(sites)}")
            logger.info(f"✅ Successful: {success_count}")
            logger.info(f"❌ Failed: {len(sites) - success_count}")
            
            if failed_sites:
                logger.info(f"💥 Failed sites:")
                for domain in failed_sites:
                    logger.info(f"   - {domain}")
            
            if success_count == len(sites):
                logger.info("🎉 All sites processed successfully!")
            elif success_count > 0:
                logger.info("⚠️  Some sites failed - check logs above for details")
            else:
                logger.error("💥 All sites failed - check configuration and credentials")
                
            logger.info(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error("")
            logger.error("=" * 80) 
            logger.error("💥 FATAL ERROR IN DNS AUTOMATOR")
            logger.error("=" * 80)
            logger.error(f"❌ Unexpected error: {e}")
            logger.error(f"🔍 Exception type: {type(e).__name__}")
            logger.error(f"📍 This prevented the DNS Automator from running at all")
            logger.error(f"🛠️  Check configuration and database connectivity")
            logger.error("=" * 80)
            sys.exit(1)


def main():
    """Main entry point"""
    print("🟢 DEBUG: main() function called")
    print("🟢 DEBUG: About to create DNSAutomator instance...")
    
    automator = DNSAutomator()
    
    print("🟢 DEBUG: DNSAutomator created, about to call run()...")
    automator.run()
    
    print("🟢 DEBUG: main() function completed")


if __name__ == "__main__":
    main()