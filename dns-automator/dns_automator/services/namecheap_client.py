"""Namecheap API client for domain management"""

import logging
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

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
        self.api_user = api_user
        self.api_key = api_key
        self.username = username
        self.client_ip = client_ip
        self.base_url = "https://api.namecheap.com/xml.response"
        
        logger.info(f"Namecheap client initialized for user: {username}")
    
    def _make_request(self, command: str, params: Dict[str, str]) -> ET.Element:
        """
        Make API request to Namecheap
        
        Args:
            command: API command
            params: Additional parameters
            
        Returns:
            XML response root element
        """
        # Build request parameters
        request_params = {
            "ApiUser": self.api_user,
            "ApiKey": self.api_key,
            "UserName": self.username,
            "ClientIp": self.client_ip,
            "Command": command,
            **params
        }
        
        try:
            response = requests.get(self.base_url, params=request_params, timeout=30)
            response.raise_for_status()
            
            # Parse XML response
            root = ET.fromstring(response.text)
            
            # Check for API errors
            status = root.get("Status")
            if status != "OK":
                errors = root.findall(".//Error")
                if errors:
                    error_msg = errors[0].text
                    error_number = errors[0].get("Number", "Unknown")
                    raise NamecheapError(f"API Error {error_number}: {error_msg}")
                raise NamecheapError("Unknown API error")
            
            return root
            
        except requests.RequestException as e:
            logger.error(f"Request error: {e}")
            raise NamecheapError(f"Request failed: {str(e)}")
        except ET.ParseError as e:
            logger.error(f"XML parse error: {e}")
            raise NamecheapError(f"Invalid API response: {str(e)}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
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
            logger.info(f"Setting nameservers for {domain} to: {', '.join(nameservers)}")
            
            root = self._make_request("namecheap.domains.dns.setCustom", params)
            
            # Check if update was successful
            command_response = root.find(".//CommandResponse")
            if command_response is not None:
                update_result = command_response.find(".//DomainDNSSetCustomResult")
                if update_result is not None and update_result.get("Updated") == "true":
                    logger.info(f"Successfully updated nameservers for {domain}")
                    return True
            
            logger.error(f"Failed to update nameservers for {domain}")
            return False
            
        except NamecheapError as e:
            logger.error(f"Namecheap API error for {domain}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error updating nameservers for {domain}: {e}")
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