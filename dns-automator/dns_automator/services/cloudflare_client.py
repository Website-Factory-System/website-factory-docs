"""Cloudflare API client for DNS zone management"""

import logging
from typing import Dict, List, Optional, Any
from tenacity import retry, stop_after_attempt, wait_exponential

import CloudFlare
from CloudFlare.exceptions import CloudFlareAPIError

logger = logging.getLogger(__name__)


class CloudflareError(Exception):
    """Custom exception for Cloudflare API errors"""
    pass


class CloudflareClient:
    """Client for interacting with Cloudflare API"""
    
    def __init__(self, api_token: str, account_id: str = None):
        """
        Initialize Cloudflare client
        
        Args:
            api_token: Cloudflare API token (scoped)
            account_id: Cloudflare Account ID (required for zone creation)
        """
        logger.info(f"🔧 Initializing Cloudflare client...")
        logger.info(f"   API Token: {api_token[:10]}...{api_token[-4:]} (length: {len(api_token)})")
        logger.info(f"   Account ID: {account_id[:8] if account_id else 'None'}...{account_id[-4:] if account_id else ''}")
        
        try:
            self.cf = CloudFlare.CloudFlare(token=api_token)
            self.account_id = account_id
            logger.info(f"✅ Cloudflare client initialized successfully")
            
            # Test the API token by making a simple API call
            logger.info(f"🧪 Testing API token validity...")
            try:
                user_info = self.cf.user.get()
                logger.info(f"✅ API token is valid - authenticated as: {user_info.get('email', 'unknown')}")
            except Exception as test_e:
                logger.error(f"❌ API token test failed: {test_e}")
                logger.error(f"   This may indicate an invalid or expired API token")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize Cloudflare client: {e}")
            raise CloudflareError(f"Failed to initialize Cloudflare client: {str(e)}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def create_zone(self, domain: str) -> tuple[str, list[str]]:
        """
        Create a new DNS zone
        
        Args:
            domain: Domain name (e.g., example.com)
            
        Returns:
            Tuple of (zone_id, nameservers)
        """
        try:
            logger.info(f"🌐 Creating Cloudflare zone for {domain}")
            
            # Create zone (following Cloudflare automation docs)
            zone_data = {
                "name": domain,
                "type": "full"
            }
            
            # Add account ID if provided (required for proper zone creation)
            if self.account_id:
                zone_data["account"] = {
                    "id": self.account_id
                }
                logger.info(f"   Including account ID in zone creation: {self.account_id[:8]}...{self.account_id[-4:]}")
            else:
                logger.warning("   ⚠️  No account ID provided - zone creation may fail")
            
            logger.info(f"   📤 Sending POST request to Cloudflare API...")
            logger.info(f"   Request data: {zone_data}")
            
            result = self.cf.zones.post(data=zone_data)
            
            logger.info(f"   📥 Cloudflare API response received")
            logger.info(f"   Response keys: {list(result.keys()) if isinstance(result, dict) else 'not a dict'}")
            
            zone_id = result["id"]
            nameservers = result.get("name_servers", [])
            
            logger.info(f"✅ Successfully created zone for {domain}")
            logger.info(f"   Zone ID: {zone_id}")
            logger.info(f"   Assigned nameservers: {', '.join(nameservers)}")
            return zone_id, nameservers
            
        except CloudFlareAPIError as e:
            logger.error(f"❌ Cloudflare API Error occurred:")
            logger.error(f"   Error Code: {e.code}")
            logger.error(f"   Error Message: {str(e)}")
            logger.error(f"   Error Type: {type(e).__name__}")
            
            if hasattr(e, 'errors') and e.errors:
                logger.error(f"   Detailed Errors:")
                for i, error in enumerate(e.errors, 1):
                    logger.error(f"     {i}. {error}")
            
            # Check if zone already exists
            if e.code == 1061:  # Zone already exists
                logger.info(f"   Zone already exists for {domain}, fetching existing zone")
                zone_id = self.get_zone_id(domain)
                zone_info = self.get_zone_info(zone_id)
                return zone_id, zone_info.get("name_servers", [])
            
            # Common error codes to help with debugging
            if e.code == 6003:
                logger.error(f"   🔑 ERROR 6003: Invalid or expired API token")
                logger.error(f"   Check that your Cloudflare API token is valid and has the correct permissions")
            elif e.code == 1000:
                logger.error(f"   🔐 ERROR 1000: Insufficient permissions")
                logger.error(f"   Check that your API token has Zone:Edit permissions")
            elif e.code == 1001:
                logger.error(f"   💳 ERROR 1001: Account limit exceeded or billing issue")
            
            raise CloudflareError(f"Cloudflare API error (code {e.code}): {str(e)}")
        except Exception as e:
            logger.error(f"❌ Unexpected error creating zone for {domain}:")
            logger.error(f"   Error: {str(e)}")
            logger.error(f"   Error Type: {type(e).__name__}")
            import traceback
            logger.error(f"   Traceback: {traceback.format_exc()}")
            raise CloudflareError(f"Unexpected error creating zone: {str(e)}")
    
    def get_zone_id(self, domain: str) -> str:
        """
        Get zone ID for a domain
        
        Args:
            domain: Domain name
            
        Returns:
            Zone ID
        """
        try:
            zones = self.cf.zones.get(params={"name": domain})
            
            if not zones:
                raise CloudflareError(f"Zone not found for domain: {domain}")
            
            return zones[0]["id"]
            
        except CloudFlareAPIError as e:
            logger.error(f"Error fetching zone for {domain}: {e}")
            raise CloudflareError(f"Failed to get zone: {str(e)}")
    
    def get_zone_info(self, zone_id: str) -> Dict[str, Any]:
        """
        Get zone information including nameservers
        
        Args:
            zone_id: Zone ID
            
        Returns:
            Zone information
        """
        try:
            zone = self.cf.zones.get(zone_id)
            return zone
        except CloudFlareAPIError as e:
            logger.error(f"Error fetching zone info: {e}")
            raise CloudflareError(f"Failed to get zone info: {str(e)}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def create_dns_record(
        self, 
        zone_id: str, 
        record_type: str, 
        name: str, 
        content: str, 
        proxied: bool = True,
        ttl: int = 1  # Auto TTL when proxied
    ) -> str:
        """
        Create a DNS record
        
        Args:
            zone_id: Zone ID
            record_type: Record type (A, CNAME, etc.)
            name: Record name (@ for root, www, etc.)
            content: Record content (IP address, domain, etc.)
            proxied: Whether to proxy through Cloudflare
            ttl: Time to live (auto when proxied)
            
        Returns:
            Record ID
        """
        try:
            logger.info(f"Creating {record_type} record: {name} -> {content}")
            
            # Get zone info to get the domain name
            zone_info = self.cf.zones.get(zone_id)
            domain = zone_info["name"]
            
            # Format the record name
            if name == "@" or name == domain:
                record_name = domain
            elif name.endswith(domain):
                record_name = name
            else:
                record_name = f"{name}.{domain}"
            
            record_data = {
                "type": record_type,
                "name": record_name,
                "content": content,
                "proxied": proxied,
                "ttl": ttl
            }
            
            result = self.cf.zones.dns_records.post(zone_id, data=record_data)
            record_id = result["id"]
            
            logger.info(f"Successfully created {record_type} record with ID: {record_id}")
            return record_id
            
        except CloudFlareAPIError as e:
            # Check if record already exists
            if e.code == 81057:  # Record already exists
                logger.info(f"Record already exists: {name} -> {content}")
                return self.update_or_get_existing_record(zone_id, record_type, name, content, proxied)
            
            logger.error(f"Cloudflare API error creating record: {e}")
            raise CloudflareError(f"Failed to create record: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error creating record: {e}")
            raise CloudflareError(f"Failed to create record: {str(e)}")
    
    def update_or_get_existing_record(
        self, 
        zone_id: str, 
        record_type: str, 
        name: str, 
        content: str, 
        proxied: bool = True
    ) -> str:
        """
        Update existing record or get its ID
        
        Args:
            zone_id: Zone ID
            record_type: Record type
            name: Record name
            content: New content
            proxied: Whether to proxy
            
        Returns:
            Record ID
        """
        try:
            # Get zone info
            zone_info = self.cf.zones.get(zone_id)
            domain = zone_info["name"]
            
            # Format the record name
            if name == "@" or name == domain:
                search_name = domain
            elif name.endswith(domain):
                search_name = name
            else:
                search_name = f"{name}.{domain}"
            
            # Find existing record
            records = self.cf.zones.dns_records.get(
                zone_id, 
                params={"type": record_type, "name": search_name}
            )
            
            if records:
                record = records[0]
                record_id = record["id"]
                
                # Update if content is different
                if record["content"] != content or record["proxied"] != proxied:
                    logger.info(f"Updating existing record: {name}")
                    
                    update_data = {
                        "type": record_type,
                        "name": search_name,
                        "content": content,
                        "proxied": proxied,
                        "ttl": 1
                    }
                    
                    self.cf.zones.dns_records.put(zone_id, record_id, data=update_data)
                    logger.info(f"Successfully updated record {record_id}")
                else:
                    logger.info(f"Record already exists with correct content: {record_id}")
                
                return record_id
            
            # This shouldn't happen, but handle it
            raise CloudflareError(f"Record not found after existence check: {name}")
            
        except Exception as e:
            logger.error(f"Error updating existing record: {e}")
            raise CloudflareError(f"Failed to update record: {str(e)}")
    
    def list_dns_records(self, zone_id: str) -> List[Dict[str, Any]]:
        """
        List all DNS records for a zone (for testing/verification)
        
        Args:
            zone_id: Zone ID
            
        Returns:
            List of DNS records
        """
        try:
            records = self.cf.zones.dns_records.get(zone_id)
            return records
        except Exception as e:
            logger.error(f"Error listing DNS records: {e}")
            return []