"""Spaceship API client for domain management"""

import logging
from typing import List, Dict, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

import requests

logger = logging.getLogger(__name__)


class SpaceshipError(Exception):
    """Custom exception for Spaceship API errors"""
    pass


class SpaceshipClient:
    """Client for interacting with Spaceship API"""
    
    def __init__(self, api_key: str, api_secret: str):
        """
        Initialize Spaceship client
        
        Args:
            api_key: Spaceship API key
            api_secret: Spaceship API secret
        """
        logger.info(f"🔧 Initializing Spaceship client...")
        logger.info(f"   API Key: {api_key[:8]}...{api_key[-4:]} (length: {len(api_key)})")
        logger.info(f"   API Secret: {api_secret[:8]}...{api_secret[-4:]} (length: {len(api_secret)})")
        
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.spaceship.com/v2"
        self.session = requests.Session()
        
        logger.info(f"   🔐 Attempting authentication...")
        self._authenticate()
        
        logger.info(f"✅ Spaceship client initialized successfully")
    
    def _authenticate(self):
        """Authenticate and get access token"""
        try:
            auth_url = f"{self.base_url}/oauth/token"
            auth_data = {
                "grant_type": "client_credentials",
                "client_id": self.api_key,
                "client_secret": self.api_secret
            }
            
            response = self.session.post(auth_url, json=auth_data, timeout=30)
            response.raise_for_status()
            
            token_data = response.json()
            access_token = token_data.get("access_token")
            
            if not access_token:
                raise SpaceshipError("No access token received")
            
            # Set authorization header for all future requests
            self.session.headers.update({
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            })
            
            logger.info("Successfully authenticated with Spaceship API")
            
        except requests.RequestException as e:
            logger.error(f"Authentication error: {e}")
            raise SpaceshipError(f"Authentication failed: {str(e)}")
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """
        Make API request to Spaceship
        
        Args:
            method: HTTP method (GET, POST, PUT, etc.)
            endpoint: API endpoint
            data: Request data
            
        Returns:
            JSON response
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                timeout=30
            )
            
            # Handle token expiration
            if response.status_code == 401:
                logger.info("Token expired, re-authenticating...")
                self._authenticate()
                # Retry the request
                response = self.session.request(
                    method=method,
                    url=url,
                    json=data,
                    timeout=30
                )
            
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Request error: {e}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response body: {e.response.text}")
            raise SpaceshipError(f"Request failed: {str(e)}")
    
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
            raise SpaceshipError("No nameservers provided")
        
        try:
            logger.info(f"Setting nameservers for {domain} to: {', '.join(nameservers)}")
            
            # Update nameservers
            endpoint = f"/domains/{domain}/nameservers"
            data = {
                "nameservers": nameservers
            }
            
            result = self._make_request("PUT", endpoint, data)
            
            if result.get("success", False):
                logger.info(f"Successfully updated nameservers for {domain}")
                return True
            else:
                logger.error(f"Failed to update nameservers for {domain}: {result.get('message', 'Unknown error')}")
                return False
                
        except SpaceshipError as e:
            logger.error(f"Spaceship API error for {domain}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error updating nameservers for {domain}: {e}")
            raise SpaceshipError(f"Failed to update nameservers: {str(e)}")
    
    def get_domain_info(self, domain: str) -> Optional[Dict[str, str]]:
        """
        Get domain information (for testing/verification)
        
        Args:
            domain: Domain name
            
        Returns:
            Domain info dict or None
        """
        try:
            endpoint = f"/domains/{domain}"
            result = self._make_request("GET", endpoint)
            
            if result:
                return {
                    "domain": result.get("domain", ""),
                    "status": result.get("status", ""),
                    "expires_at": result.get("expires_at", ""),
                    "nameservers": result.get("nameservers", [])
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting domain info for {domain}: {e}")
            return None