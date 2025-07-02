#!/usr/bin/env python3
"""
Test script to debug workflow execution and private networking
"""

import asyncio
import httpx
import json
import time
from datetime import datetime

class WorkflowTester:
    def __init__(self):
        # Update these URLs to match your Railway deployment
        self.api_base = "https://management-hub-api-production.up.railway.app"
        self.username = "admin"  # Update with your credentials
        self.password = "admin123"  # Update with your credentials
        self.auth_token = None
    
    async def login(self):
        """Login and get auth token"""
        print("🔐 Logging in...")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_base}/auth/token",
                data={
                    "username": self.username,
                    "password": self.password
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.auth_token = token_data["access_token"]
                print("✅ Login successful")
                return True
            else:
                print(f"❌ Login failed: {response.status_code} - {response.text}")
                return False
    
    async def create_test_site(self):
        """Create a test site to trigger workflow"""
        print("🌐 Creating test site...")
        
        if not self.auth_token:
            print("❌ Not authenticated")
            return None
        
        test_domain = f"test-{int(time.time())}.example.com"
        
        async with httpx.AsyncClient() as client:
            # First, get Cloudflare accounts
            accounts_response = await client.get(
                f"{self.api_base}/cloudflare-accounts",
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
            
            if accounts_response.status_code != 200:
                print(f"❌ Failed to get Cloudflare accounts: {accounts_response.text}")
                return None
            
            accounts = accounts_response.json()
            if not accounts:
                print("❌ No Cloudflare accounts found")
                return None
            
            # Create site with first available account
            site_data = {
                "domain": test_domain,
                "cloudflare_account_id": accounts[0]["id"]
            }
            
            response = await client.post(
                f"{self.api_base}/sites",
                json=site_data,
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
            
            if response.status_code == 201:
                site = response.json()
                print(f"✅ Created site: {site['domain']} (ID: {site['id']})")
                return site
            else:
                print(f"❌ Failed to create site: {response.status_code} - {response.text}")
                return None
    
    async def monitor_site_status(self, site_id, duration_minutes=5):
        """Monitor site status for workflow progress"""
        print(f"👁️ Monitoring site {site_id} for {duration_minutes} minutes...")
        
        end_time = time.time() + (duration_minutes * 60)
        last_status = {}
        
        while time.time() < end_time:
            try:
                async with httpx.AsyncClient() as client:
                    # Get site status
                    response = await client.get(
                        f"{self.api_base}/sites/{site_id}",
                        headers={"Authorization": f"Bearer {self.auth_token}"}
                    )
                    
                    if response.status_code == 200:
                        site = response.json()
                        current_status = {
                            "dns": site.get("status_dns"),
                            "hosting": site.get("status_hosting"),
                            "content": site.get("status_content"),
                            "deployment": site.get("status_deployment")
                        }
                        
                        # Only print if status changed
                        if current_status != last_status:
                            print(f"[{datetime.now().strftime('%H:%M:%S')}] Status: {current_status}")
                            if site.get("error_message"):
                                print(f"   Error: {site['error_message']}")
                            last_status = current_status
                    
                    # Also check detailed status
                    status_response = await client.get(
                        f"{self.api_base}/status/{site_id}",
                        headers={"Authorization": f"Bearer {self.auth_token}"}
                    )
                    
                    if status_response.status_code == 200:
                        status_detail = status_response.json()
                        if status_detail.get("current_phase"):
                            print(f"   Phase: {status_detail['current_phase']} - {status_detail.get('status', 'unknown')}")
                            if status_detail.get("steps"):
                                for step in status_detail["steps"][-3:]:  # Show last 3 steps
                                    print(f"     Step: {step.get('step_name')} - {step.get('status')}")
                
            except Exception as e:
                print(f"❌ Error monitoring status: {e}")
            
            await asyncio.sleep(10)  # Check every 10 seconds
        
        print("⏰ Monitoring period completed")
    
    async def test_direct_automator_access(self):
        """Test direct access to automator services"""
        print("🔗 Testing direct automator access...")
        
        # These URLs should be accessible from within Railway's network
        automator_urls = [
            "http://dns-automator.railway.internal",
            "http://dns-automator.railway.internal:8000",
            "https://dns-automator-production.up.railway.app",  # Public URL for comparison
        ]
        
        for url in automator_urls:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(f"{url}/health")
                    if response.status_code == 200:
                        data = response.json()
                        print(f"✅ {url} - Status: {data}")
                    else:
                        print(f"❌ {url} - HTTP {response.status_code}")
            except Exception as e:
                print(f"❌ {url} - Error: {e}")
    
    async def run_full_test(self):
        """Run complete workflow test"""
        print("🚀 Starting Workflow Execution Test")
        print("=" * 50)
        
        # Step 1: Login
        if not await self.login():
            return
        
        # Step 2: Test direct automator access (this will fail from local, but shows the pattern)
        await self.test_direct_automator_access()
        
        # Step 3: Create test site
        site = await self.create_test_site()
        if not site:
            return
        
        # Step 4: Monitor workflow execution
        await self.monitor_site_status(site["id"], duration_minutes=5)
        
        print("🏁 Test completed")

if __name__ == "__main__":
    tester = WorkflowTester()
    asyncio.run(tester.run_full_test())