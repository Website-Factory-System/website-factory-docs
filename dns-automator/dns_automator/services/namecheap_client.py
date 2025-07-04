"""Namecheap API client for domain management"""

import logging
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional

import requests

logger = logging.getLogger(__name__)


class NamecheapError(Exception):
    """Custom exception for Namecheap API errors"""
    pass


class NamecheapClient:
    """Client for interacting with Namecheap API"""
    
    def __init__(self, api_user: str, api_key: str, username: str, client_ip: str):
        """
        Initialize Namecheap client
        
        Args:
            api_user: Namecheap API user
            api_key: Namecheap API key
            username: Namecheap username
            client_ip: Whitelisted IP address
        """
        logger.info(f"🔧 Initializing Namecheap client...")
        logger.info(f"   API User: {api_user}")
        logger.info(f"   API Key: {api_key[:8]}...{api_key[-4:]} (length: {len(api_key)})")
        logger.info(f"   Username: {username}")
        logger.info(f"   Client IP: {client_ip}")
        
        self.api_user = api_user
        self.api_key = api_key
        self.username = username
        self.client_ip = client_ip
        self.base_url = "https://api.namecheap.com/xml.response"
        
        logger.info(f"✅ Namecheap client initialized successfully for user: {username}")
    
    def _make_request(self, command: str, params: Dict[str, str]) -> ET.Element:
        """
        Make API request to Namecheap
        
        Args:
            command: API command
            params: Additional parameters
            
        Returns:
            XML response root element
        """
        logger.info(f"📤 Making Namecheap API request...")
        logger.info(f"   Command: {command}")
        logger.info(f"   Additional params: {params}")
        
        # Build request parameters
        request_params = {
            "ApiUser": self.api_user,
            "ApiKey": self.api_key,
            "UserName": self.username,
            "ClientIp": self.client_ip,
            "Command": command,
            **params
        }
        
        # Log params (but mask the API key)
        safe_params = request_params.copy()
        safe_params["ApiKey"] = f"{self.api_key[:8]}...{self.api_key[-4:]}"
        logger.info(f"   Full request params: {safe_params}")
        logger.info(f"   Request URL: {self.base_url}")
        
        try:
            logger.info(f"   🌐 Sending GET request to Namecheap...")
            response = requests.get(self.base_url, params=request_params, timeout=30)
            
            logger.info(f"   📥 Response received - Status Code: {response.status_code}")
            logger.info(f"   Response Headers: {dict(response.headers)}")
            
            response.raise_for_status()
            
            logger.info(f"   📄 Response body length: {len(response.text)} characters")
            logger.info(f"   Response preview: {response.text[:500]}...")
            
            # Parse XML response
            logger.info(f"   🔍 Parsing XML response...")
            root = ET.fromstring(response.text)
            
            # Check for API errors
            status = root.get("Status")
            logger.info(f"   Response Status: {status}")
            
            if status != "OK":
                logger.error(f"   ❌ Namecheap API returned error status")
                errors = root.findall(".//Error")
                if errors:
                    for i, error in enumerate(errors, 1):
                        error_msg = error.text
                        error_number = error.get("Number", "Unknown")
                        logger.error(f"     Error {i}: #{error_number} - {error_msg}")
                    
                    # Raise the first error
                    error_msg = errors[0].text
                    error_number = errors[0].get("Number", "Unknown")
                    raise NamecheapError(f"Namecheap API Error {error_number}: {error_msg}")
                else:
                    logger.error(f"   No specific error details found in response")
                    raise NamecheapError("Unknown Namecheap API error")
            
            logger.info(f"   ✅ Namecheap API request successful")
            return root
            
        except requests.RequestException as e:
            logger.error(f"   ❌ HTTP Request error:")
            logger.error(f"     Error: {str(e)}")
            logger.error(f"     Error Type: {type(e).__name__}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"     Response Status: {e.response.status_code}")
                logger.error(f"     Response Text: {e.response.text[:1000]}")
            raise NamecheapError(f"Request failed: {str(e)}")
        except ET.ParseError as e:
            logger.error(f"   ❌ XML Parse error:")
            logger.error(f"     Error: {str(e)}")
            logger.error(f"     Response text: {response.text}")
            raise NamecheapError(f"Invalid API response: {str(e)}")
        except Exception as e:
            logger.error(f"   ❌ Unexpected error:")
            logger.error(f"     Error: {str(e)}")
            logger.error(f"     Error Type: {type(e).__name__}")
            import traceback
            logger.error(f"     Traceback: {traceback.format_exc()}")
            raise NamecheapError(f"Unexpected error: {str(e)}")
    
    def set_nameservers(self, domain: str, nameservers: List[str]) -> bool:
        """
        Update domain nameservers
        
        Args:
            domain: Domain name (e.g., example.com)
            nameservers: List of nameservers
            
        Returns:
            Success boolean
        """
        if not nameservers:
            raise NamecheapError("No nameservers provided")
        
        # Split domain into SLD and TLD
        parts = domain.split(".")
        if len(parts) < 2:
            raise NamecheapError(f"Invalid domain format: {domain}")
        
        sld = ".".join(parts[:-1])
        tld = parts[-1]
        
        # Build nameserver parameters
        params = {
            "SLD": sld,
            "TLD": tld,
            "Nameservers": ",".join(nameservers)
        }
        
        try:
            logger.info(f"🌐 Setting nameservers for {domain}")
            logger.info(f"   Target nameservers: {', '.join(nameservers)}")
            logger.info(f"   Domain parts: SLD='{sld}', TLD='{tld}'")
            
            root = self._make_request("namecheap.domains.dns.setCustom", params)
            
            logger.info(f"   🔍 Checking if nameserver update was successful...")
            
            # Check if update was successful
            command_response = root.find(".//CommandResponse")
            if command_response is not None:
                logger.info(f"   Found CommandResponse element")
                update_result = command_response.find(".//DomainDNSSetCustomResult")
                if update_result is not None:
                    updated = update_result.get("Updated")
                    logger.info(f"   DomainDNSSetCustomResult Updated attribute: '{updated}'")
                    if updated == "true":
                        logger.info(f"✅ Successfully updated nameservers for {domain}")
                        return True
                    else:
                        logger.error(f"   ❌ Update failed - Updated attribute is '{updated}', expected 'true'")
                else:
                    logger.error(f"   ❌ DomainDNSSetCustomResult element not found in response")
                    logger.error(f"   Available elements: {[elem.tag for elem in command_response.iter()]}")
            else:
                logger.error(f"   ❌ CommandResponse element not found in response")
                logger.error(f"   Response XML structure:")
                import xml.etree.ElementTree as ET
                logger.error(f"   {ET.tostring(root, encoding='unicode')}")
            
            logger.error(f"❌ Failed to update nameservers for {domain}")
            return False
            
        except NamecheapError as e:
            logger.error(f"❌ Namecheap API error for {domain}: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error updating nameservers for {domain}:")
            logger.error(f"   Error: {str(e)}")
            logger.error(f"   Error Type: {type(e).__name__}")
            import traceback
            logger.error(f"   Traceback: {traceback.format_exc()}")
            raise NamecheapError(f"Failed to update nameservers: {str(e)}")
    
    def get_domain_info(self, domain: str) -> Optional[Dict[str, str]]:
        """
        Get domain information (for testing/verification)
        
        Args:
            domain: Domain name
            
        Returns:
            Domain info dict or None
        """
        # Split domain
        parts = domain.split(".")
        if len(parts) < 2:
            return None
        
        sld = ".".join(parts[:-1])
        tld = parts[-1]
        
        params = {
            "SLD": sld,
            "TLD": tld
        }
        
        try:
            root = self._make_request("namecheap.domains.getInfo", params)
            
            domain_info = root.find(".//DomainGetInfoResult")
            if domain_info is not None:
                return {
                    "domain": domain_info.get("DomainName", ""),
                    "status": domain_info.get("Status", ""),
                    "id": domain_info.get("ID", "")
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting domain info for {domain}: {e}")
            return None