#!/usr/bin/env python3
"""
Debug script to test Cloudflare API connectivity directly
"""
import os
import sys
from supabase import create_client
import CloudFlare
from CloudFlare.exceptions import CloudFlareAPIError

def main():
    # Load Supabase credentials
    supabase_url = os.getenv('SUPABASE_URL', 'https://dhmshimcnbsirvirvttx.supabase.co')
    
    # Read service key from management-hub-api env file
    try:
        with open('management-hub-api/.env', 'r') as f:
            for line in f:
                if line.startswith('SUPABASE_SERVICE_KEY='):
                    supabase_key = line.split('=', 1)[1].strip()
                    break
            else:
                print("❌ SUPABASE_SERVICE_KEY not found in management-hub-api/.env")
                return
    except FileNotFoundError:
        print("❌ management-hub-api/.env file not found")
        return
    
    # Connect to Supabase
    try:
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase")
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return
    
    # Fetch Cloudflare accounts
    try:
        result = supabase.table('cloudflare_accounts').select('*').execute()
        accounts = result.data
        print(f"✅ Found {len(accounts)} Cloudflare accounts in database")
    except Exception as e:
        print(f"❌ Failed to fetch Cloudflare accounts: {e}")
        return
    
    if not accounts:
        print("❌ No Cloudflare accounts found in database")
        return
    
    # Test each account
    for i, account in enumerate(accounts):
        print(f"\n--- Testing Account {i+1}: {account['account_nickname']} ---")
        print(f"Email: {account['email']}")
        print(f"Token length: {len(account['api_token'])} characters")
        print(f"Token format: {account['api_token'][:10]}...{account['api_token'][-4:]}")
        
        # Test Cloudflare API
        try:
            cf = CloudFlare.CloudFlare(token=account['api_token'])
            
            # Test basic API call - get user info
            print("Testing API connectivity...")
            user_info = cf.user.get()
            print(f"✅ API working! User: {user_info.get('email', 'N/A')}")
            
            # Test zone list
            print("Testing zone access...")
            zones = cf.zones.get()
            print(f"✅ Can access {len(zones)} zones")
            
            # Test creating a test zone (we'll delete it immediately)
            test_domain = "test-example-dns-factory.com"
            print(f"Testing zone creation with {test_domain}...")
            
            try:
                zone_data = {
                    "name": test_domain,
                    "type": "full"
                }
                result = cf.zones.post(data=zone_data)
                zone_id = result["id"]
                print(f"✅ Successfully created test zone: {zone_id}")
                
                # Delete the test zone
                cf.zones.delete(zone_id)
                print("✅ Test zone deleted")
                
            except CloudFlareAPIError as e:
                if e.code == 1061:  # Zone already exists
                    print("⚠️  Test zone already exists (this is normal)")
                else:
                    print(f"❌ Zone creation failed: Code {e.code}, Error: {e}")
                    if hasattr(e, 'errors'):
                        print(f"Details: {e.errors}")
            
        except CloudFlareAPIError as e:
            print(f"❌ Cloudflare API Error: Code {e.code}, Error: {e}")
            if hasattr(e, 'errors'):
                print(f"Error details: {e.errors}")
        except Exception as e:
            print(f"❌ Unexpected error: {type(e).__name__}: {e}")
    
    print("\n=== Summary ===")
    print("If you see API errors above, the issue is with the Cloudflare tokens.")
    print("If all tests pass, the issue is likely in the DNS Automator logic.")

if __name__ == "__main__":
    main()