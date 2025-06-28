#!/usr/bin/env python3
"""Test script to verify DNS Automator connections"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_supabase_connection():
    """Test Supabase connection"""
    print("Testing Supabase connection...")
    try:
        from dns_automator.services.supabase_client import SupabaseService
        
        service = SupabaseService()
        # Try to fetch cloudflare accounts to test connection
        service.client.table("cloudflare_accounts").select("count", count="exact").execute()
        print("✅ Supabase connection successful")
        return True
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False

def test_environment():
    """Test environment configuration"""
    print("\nChecking environment variables...")
    
    required_vars = ["SUPABASE_URL", "SUPABASE_SERVICE_KEY"]
    missing = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Missing required environment variables: {', '.join(missing)}")
        return False
    else:
        print("✅ All required environment variables present")
        return True

def main():
    """Run all tests"""
    print("DNS Automator Connection Test\n" + "="*40)
    
    tests_passed = []
    
    # Test environment
    tests_passed.append(test_environment())
    
    # Test Supabase
    if tests_passed[0]:  # Only test if env vars are present
        tests_passed.append(test_supabase_connection())
    
    print("\n" + "="*40)
    if all(tests_passed):
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please check your configuration.")
        sys.exit(1)

if __name__ == "__main__":
    main()