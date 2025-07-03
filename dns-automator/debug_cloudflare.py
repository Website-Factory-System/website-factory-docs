#!/usr/bin/env python3
"""Debug script to test CloudFlare API library behavior"""

import os
import sys
import logging

# Set up logging to see what's happening
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_cloudflare_import():
    """Test if CloudFlare library imports correctly"""
    try:
        # Test different import patterns
        import cloudflare
        logger.info("✅ cloudflare (lowercase) imported successfully")
        logger.info(f"   cloudflare version: {cloudflare.__version__ if hasattr(cloudflare, '__version__') else 'Unknown'}")
        return True
    except ImportError as e1:
        logger.error(f"❌ cloudflare (lowercase) import failed: {e1}")
        try:
            import CloudFlare
            from CloudFlare.exceptions import CloudFlareAPIError
            logger.info("✅ CloudFlare (uppercase) imported successfully")
            logger.info(f"   CloudFlare version: {CloudFlare.__version__ if hasattr(CloudFlare, '__version__') else 'Unknown'}")
            return True
        except ImportError as e2:
            logger.error(f"❌ CloudFlare (uppercase) import failed: {e2}")
            return False

def test_cloudflare_authentication():
    """Test CloudFlare authentication without making real API calls"""
    try:
        import CloudFlare
        from CloudFlare.exceptions import CloudFlareAPIError
        
        # Test with a fake token to see what error we get
        fake_token = "invalid_token_12345"
        logger.info(f"Testing with fake token: {fake_token}")
        
        cf = CloudFlare.CloudFlare(token=fake_token)
        logger.info("✅ CloudFlare client created (no API call yet)")
        
        # Now try to make a simple API call to test authentication
        logger.info("Making test API call to verify token...")
        try:
            # Try to list zones (this should fail with authentication error)
            zones = cf.zones.get()
            logger.info("🤔 Unexpected success - fake token worked?")
        except CloudFlareAPIError as e:
            logger.info(f"✅ Expected authentication error: Code={e.code}, Message={e}")
            logger.info(f"   This is normal - we used a fake token")
            if hasattr(e, 'errors'):
                logger.info(f"   Error details: {e.errors}")
        except Exception as e:
            logger.error(f"❌ Unexpected error type: {type(e).__name__}: {e}")
        
        return True
    except Exception as e:
        logger.error(f"❌ CloudFlare authentication test failed: {e}")
        return False

def test_cloudflare_error_handling():
    """Test how CloudFlare library handles different error scenarios"""
    try:
        import CloudFlare
        from CloudFlare.exceptions import CloudFlareAPIError
        
        logger.info("Testing error handling patterns...")
        
        # Test 1: Empty token
        try:
            cf = CloudFlare.CloudFlare(token="")
            zones = cf.zones.get()
        except CloudFlareAPIError as e:
            logger.info(f"Empty token error: Code={e.code}, Message={e}")
        except Exception as e:
            logger.info(f"Empty token error (other): {type(e).__name__}: {e}")
        
        # Test 2: None token
        try:
            cf = CloudFlare.CloudFlare(token=None)
            zones = cf.zones.get()
        except CloudFlareAPIError as e:
            logger.info(f"None token error: Code={e.code}, Message={e}")
        except Exception as e:
            logger.info(f"None token error (other): {type(e).__name__}: {e}")
        
        # Test 3: Malformed token
        try:
            cf = CloudFlare.CloudFlare(token="malformed_token")
            zones = cf.zones.get()
        except CloudFlareAPIError as e:
            logger.info(f"Malformed token error: Code={e.code}, Message={e}")
        except Exception as e:
            logger.info(f"Malformed token error (other): {type(e).__name__}: {e}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error handling test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("CloudFlare API Debug Test\n" + "="*50)
    
    tests = [
        test_cloudflare_import,
        test_cloudflare_authentication,
        test_cloudflare_error_handling
    ]
    
    for test in tests:
        print(f"\n--- Running {test.__name__} ---")
        try:
            test()
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with unexpected error: {e}")
        print()

if __name__ == "__main__":
    main()