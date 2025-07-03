"""Logging configuration for DNS Automator"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

from .config import settings


def setup_logging():
    """Configure logging for the application"""
    print("🟢 DEBUG: setup_logging() called")
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    print(f"🟢 DEBUG: Log directory created: {log_dir.absolute()}")
    
    # Configure root logger
    logger = logging.getLogger()
    log_level = getattr(logging, settings.log_level.upper())
    logger.setLevel(log_level)
    print(f"🟢 DEBUG: Root logger level set to: {settings.log_level.upper()} ({log_level})")
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    print("🟢 DEBUG: Console handler configured")
    
    # File handler with rotation
    log_file = log_dir / "dns_automator.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    print(f"🟢 DEBUG: File handler configured: {log_file.absolute()}")
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    print("🟢 DEBUG: Handlers added to logger")
    
    # Test the logger
    print("🟢 DEBUG: Testing logger...")
    logger.info("🧪 TEST LOG MESSAGE - Logger is working!")
    print("🟢 DEBUG: Logger test complete")
    
    return logger