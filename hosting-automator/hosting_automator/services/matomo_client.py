"""Matomo API client for Hosting Automator"""

import logging
import requests
from typing import Optional, Tuple, Dict, Any

logger = logging.getLogger("hosting_automator")


class MatomoService:
    """Service for interacting with Matomo API"""
    
    def __init__(self, matomo_config: Optional[Dict[str, Any]]):
        """
        Initialize Matomo client
        
        Args:
            matomo_config: Matomo configuration from database
        """
        if not matomo_config:
            self.enabled = False
            logger.warning("Matomo configuration not found, analytics tracking disabled")
            return
        
        self.enabled = True
        self.api_url = matomo_config.get("api_url")
        self.api_token = matomo_config.get("api_token")
        
        if not all([self.api_url, self.api_token]):
            self.enabled = False
            logger.warning("Incomplete Matomo configuration, analytics tracking disabled")
            return
        
        # Ensure API URL ends with /
        if not self.api_url.endswith('/'):
            self.api_url += '/'
        
        logger.info(f"Matomo service initialized for {self.api_url}")
    
    def create_tracking_site(self, domain: str) -> Tuple[Optional[int], str]:
        """
        Create a new tracking site in Matomo
        
        Args:
            domain: Domain name for the site
            
        Returns:
            Tuple of (matomo_site_id, error_message)
        """
        if not self.enabled:
            logger.warning("Matomo is not enabled, skipping site creation")
            return None, ""
        
        try:
            # Prepare API request
            params = {
                'module': 'API',
                'method': 'SitesManager.addSite',
                'siteName': domain,
                'urls': f'https://{domain}',
                'format': 'json',
                'token_auth': self.api_token
            }
            
            # Make API request
            response = requests.post(
                self.api_url,
                data=params,
                timeout=30,
                verify=True  # Verify SSL certificate
            )
            
            # Check response
            if response.status_code != 200:
                error_msg = f"Matomo API returned status {response.status_code}"
                logger.error(error_msg)
                return None, error_msg
            
            # Parse response
            result = response.json()
            
            # Check for API error
            if isinstance(result, dict) and 'result' in result and result['result'] == 'error':
                error_msg = result.get('message', 'Unknown Matomo API error')
                logger.error(f"Matomo API error: {error_msg}")
                return None, error_msg
            
            # Extract site ID
            if isinstance(result, dict) and 'value' in result:
                site_id = int(result['value'])
            elif isinstance(result, (int, str)):
                site_id = int(result)
            else:
                error_msg = f"Unexpected Matomo API response format: {result}"
                logger.error(error_msg)
                return None, error_msg
            
            logger.info(f"Successfully created Matomo tracking site for {domain} with ID {site_id}")
            return site_id, ""
            
        except requests.exceptions.Timeout:
            error_msg = "Matomo API request timed out"
            logger.error(error_msg)
            return None, error_msg
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Matomo API request failed: {e}"
            logger.error(error_msg)
            return None, error_msg
            
        except ValueError as e:
            error_msg = f"Failed to parse Matomo API response: {e}"
            logger.error(error_msg)
            return None, error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error creating Matomo site: {e}"
            logger.error(error_msg)
            return None, error_msg
    
    def check_site_exists(self, domain: str) -> Optional[int]:
        """
        Check if a site already exists in Matomo
        
        Args:
            domain: Domain name to check
            
        Returns:
            Site ID if exists, None otherwise
        """
        if not self.enabled:
            return None
        
        try:
            # Get all sites
            params = {
                'module': 'API',
                'method': 'SitesManager.getAllSites',
                'format': 'json',
                'token_auth': self.api_token
            }
            
            response = requests.get(
                self.api_url,
                params=params,
                timeout=30,
                verify=True
            )
            
            if response.status_code == 200:
                sites = response.json()
                
                # Search for domain
                for site in sites:
                    if site.get('main_url', '').endswith(domain) or site.get('name', '') == domain:
                        return int(site.get('idsite'))
                        
        except Exception as e:
            logger.warning(f"Failed to check existing Matomo sites: {e}")
        
        return None