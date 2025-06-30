"""CloudPanel CLI client via SSH for Hosting Automator"""

import logging
import re
import secrets
import string
import shlex
from typing import Optional, Tuple, Dict, Any
from paramiko import SSHClient, AutoAddPolicy, RSAKey
from io import StringIO

logger = logging.getLogger("hosting_automator")


class CloudPanelService:
    """Service for interacting with CloudPanel via SSH/CLI"""
    
    def __init__(self, server_config: Dict[str, Any]):
        """
        Initialize CloudPanel SSH client
        
        Args:
            server_config: Server configuration from database
        """
        self.ssh_host = server_config.get("ip_address")
        self.ssh_port = server_config.get("ssh_port", 22)
        self.ssh_user = server_config.get("ssh_user", "root")
        self.ssh_key = server_config.get("ssh_private_key")
        
        if not all([self.ssh_host, self.ssh_key]):
            raise ValueError("Missing required SSH configuration")
        
        self.ssh_client = None
        logger.info(f"CloudPanel service initialized for {self.ssh_host}")
    
    def connect(self) -> None:
        """Establish SSH connection to server"""
        try:
            self.ssh_client = SSHClient()
            self.ssh_client.set_missing_host_key_policy(AutoAddPolicy())
            
            # Parse private key
            private_key = RSAKey.from_private_key(StringIO(self.ssh_key))
            
            # Connect
            self.ssh_client.connect(
                hostname=self.ssh_host,
                port=self.ssh_port,
                username=self.ssh_user,
                pkey=private_key,
                timeout=30
            )
            
            logger.info(f"SSH connection established to {self.ssh_host}")
            
        except Exception as e:
            logger.error(f"Failed to establish SSH connection: {e}")
            raise
    
    def disconnect(self) -> None:
        """Close SSH connection"""
        if self.ssh_client:
            self.ssh_client.close()
            logger.info("SSH connection closed")
    
    def execute_command(self, command: str) -> Tuple[str, str, int]:
        """
        Execute command via SSH
        
        Args:
            command: Command to execute
            
        Returns:
            Tuple of (stdout, stderr, exit_code)
        """
        if not self.ssh_client:
            raise RuntimeError("SSH client not connected")
        
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            
            # Read output
            stdout_str = stdout.read().decode().strip()
            stderr_str = stderr.read().decode().strip()
            exit_code = stdout.channel.recv_exit_status()
            
            # Log command result
            if exit_code == 0:
                logger.debug(f"Command succeeded: {command}")
            else:
                logger.warning(f"Command failed (exit {exit_code}): {command}")
                if stderr_str:
                    logger.warning(f"Error output: {stderr_str}")
            
            return stdout_str, stderr_str, exit_code
            
        except Exception as e:
            logger.error(f"Failed to execute command: {e}")
            return "", str(e), -1
    
    @staticmethod
    def generate_secure_password(length: int = 16) -> str:
        """Generate a secure random password"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password
    
    @staticmethod
    def sanitize_input(value: str, allowed_pattern: str = r'^[a-zA-Z0-9.-]+$') -> str:
        """
        Sanitize input to prevent command injection
        
        Args:
            value: Value to sanitize
            allowed_pattern: Regex pattern for allowed characters
            
        Returns:
            Sanitized value
        """
        if not re.match(allowed_pattern, value):
            raise ValueError(f"Invalid characters in input: {value}")
        return value
    
    def create_site(self, domain: str) -> Tuple[bool, str, str]:
        """
        Create a static site in CloudPanel
        
        Args:
            domain: Domain name for the site
            
        Returns:
            Tuple of (success, doc_root, error_message)
        """
        try:
            # Sanitize domain
            domain = self.sanitize_input(domain)
            
            # Generate site user (remove dots and limit length)
            site_user = f"user_{domain.replace('.', '')[:15]}"
            site_user = self.sanitize_input(site_user, r'^[a-zA-Z0-9_]+$')
            
            # Generate secure password
            password = self.generate_secure_password()
            
            # Create static site
            command = (
                f"clpctl site:add:static "
                f"--domainName={shlex.quote(domain)} "
                f"--siteUser={shlex.quote(site_user)} "
                f"--siteUserPassword={shlex.quote(password)}"
            )
            
            stdout, stderr, exit_code = self.execute_command(command)
            
            if exit_code != 0:
                # Check if site already exists
                if "already exists" in stderr.lower():
                    logger.warning(f"Site {domain} already exists, continuing...")
                else:
                    return False, "", f"Failed to create site: {stderr}"
            
            # Infer document root path
            doc_root = f"/home/{site_user}/htdocs/{domain}"
            
            logger.info(f"Successfully created site for {domain} with user {site_user}")
            return True, doc_root, ""
            
        except Exception as e:
            error_msg = f"Error creating site: {e}"
            logger.error(error_msg)
            return False, "", error_msg
    
    def provision_ssl(self, domain: str) -> Tuple[bool, str]:
        """
        Provision Let's Encrypt SSL certificate
        
        Args:
            domain: Domain name
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Sanitize domain
            domain = self.sanitize_input(domain)
            
            # Install Let's Encrypt certificate
            command = f"clpctl lets-encrypt:install:certificate --domainName={shlex.quote(domain)}"
            
            stdout, stderr, exit_code = self.execute_command(command)
            
            if exit_code != 0:
                # Check if certificate already exists
                if "already" in stderr.lower() or "exists" in stderr.lower():
                    logger.warning(f"SSL certificate for {domain} already exists")
                    return True, ""
                else:
                    return False, f"Failed to provision SSL: {stderr}"
            
            logger.info(f"Successfully provisioned SSL certificate for {domain}")
            return True, ""
            
        except Exception as e:
            error_msg = f"Error provisioning SSL: {e}"
            logger.error(error_msg)
            return False, error_msg