#!/usr/bin/env python3
"""
Railway Private Networking Diagnostic Script
Helps identify issues with service-to-service communication
"""

import os
import asyncio
import httpx
import socket
import subprocess
import json
from datetime import datetime

class RailwayNetworkingDiagnostic:
    def __init__(self):
        self.dns_url = os.getenv("DNS_AUTOMATOR_URL", "http://dns-automator.railway.internal")
        self.hosting_url = os.getenv("HOSTING_AUTOMATOR_URL", "http://hosting-automator.railway.internal")
        self.results = {}
    
    async def test_environment_variables(self):
        """Test 1: Verify environment variables are set"""
        print("🧪 Test 1: Environment Variables")
        print(f"DNS_AUTOMATOR_URL: {self.dns_url}")
        print(f"HOSTING_AUTOMATOR_URL: {self.hosting_url}")
        print(f"PORT: {os.getenv('PORT', 'Not set')}")
        print(f"RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT', 'Not set')}")
        print(f"RAILWAY_PROJECT_ID: {os.getenv('RAILWAY_PROJECT_ID', 'Not set')}")
        print()
        
        self.results["env_vars"] = {
            "dns_url": self.dns_url,
            "hosting_url": self.hosting_url,
            "port": os.getenv('PORT'),
            "railway_env": os.getenv('RAILWAY_ENVIRONMENT'),
            "project_id": os.getenv('RAILWAY_PROJECT_ID')
        }
    
    async def test_dns_resolution(self):
        """Test 2: Test DNS resolution for Railway internal domains"""
        print("🧪 Test 2: DNS Resolution")
        
        hosts_to_test = [
            "dns-automator.railway.internal",
            "hosting-automator.railway.internal"
        ]
        
        for host in hosts_to_test:
            try:
                # Test IPv4 resolution
                ipv4_result = socket.getaddrinfo(host, None, socket.AF_INET)
                print(f"✅ {host} IPv4: {[r[4][0] for r in ipv4_result]}")
            except Exception as e:
                print(f"❌ {host} IPv4 failed: {e}")
            
            try:
                # Test IPv6 resolution  
                ipv6_result = socket.getaddrinfo(host, None, socket.AF_INET6)
                print(f"✅ {host} IPv6: {[r[4][0] for r in ipv6_result]}")
            except Exception as e:
                print(f"❌ {host} IPv6 failed: {e}")
        print()
    
    async def test_port_scanning(self):
        """Test 3: Test if services are listening on expected ports"""
        print("🧪 Test 3: Port Scanning")
        
        services = [
            ("dns-automator.railway.internal", 8000),
            ("hosting-automator.railway.internal", 8000),
        ]
        
        for host, port in services:
            try:
                # Test IPv6 connection
                sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((host, port))
                sock.close()
                
                if result == 0:
                    print(f"✅ {host}:{port} is reachable (IPv6)")
                else:
                    print(f"❌ {host}:{port} is not reachable (IPv6) - Error: {result}")
            except Exception as e:
                print(f"❌ {host}:{port} IPv6 test failed: {e}")
        print()
    
    async def test_http_connectivity(self):
        """Test 4: Test HTTP connectivity with different configurations"""
        print("🧪 Test 4: HTTP Connectivity")
        
        test_urls = [
            self.dns_url,
            f"{self.dns_url}:8000",
            "http://dns-automator.railway.internal:8000",
            self.hosting_url,
            f"{self.hosting_url}:8000", 
            "http://hosting-automator.railway.internal:8000"
        ]
        
        for url in test_urls:
            await self._test_single_url(url)
        print()
    
    async def _test_single_url(self, url):
        """Test a single URL with various HTTP configurations"""
        print(f"Testing: {url}")
        
        # Test with different client configurations
        configs = [
            {"timeout": 10.0, "description": "Default"},
            {"timeout": 30.0, "description": "Longer timeout"},
            {"timeout": 10.0, "verify": False, "description": "No SSL verify"},
        ]
        
        for config in configs:
            try:
                desc = config.pop("description")
                async with httpx.AsyncClient(**config) as client:
                    response = await client.get(f"{url}/health")
                    print(f"  ✅ {desc}: Status {response.status_code}")
                    if response.status_code == 200:
                        data = response.json()
                        print(f"     Response: {data}")
            except httpx.ConnectError as e:
                print(f"  ❌ {desc}: Connection failed - {e}")
            except httpx.TimeoutException as e:
                print(f"  ❌ {desc}: Timeout - {e}")
            except Exception as e:
                print(f"  ❌ {desc}: Error - {e}")
    
    async def test_background_task_context(self):
        """Test 5: Verify environment in background task context"""
        print("🧪 Test 5: Background Task Context")
        
        # Simulate what happens in a FastAPI background task
        async def background_task():
            return {
                "dns_url": os.getenv("DNS_AUTOMATOR_URL"),
                "hosting_url": os.getenv("HOSTING_AUTOMATOR_URL"),
                "supabase_url": os.getenv("SUPABASE_URL", "Not set"),
                "working_directory": os.getcwd()
            }
        
        result = await background_task()
        print(f"Background task environment: {json.dumps(result, indent=2)}")
        print()
        
        self.results["background_context"] = result
    
    async def test_railway_metadata(self):
        """Test 6: Check Railway-specific metadata"""
        print("🧪 Test 6: Railway Metadata")
        
        railway_vars = [
            "RAILWAY_ENVIRONMENT_NAME",
            "RAILWAY_PROJECT_NAME", 
            "RAILWAY_SERVICE_NAME",
            "RAILWAY_DEPLOYMENT_ID",
            "RAILWAY_REPLICA_ID",
            "RAILWAY_PRIVATE_DOMAIN",
            "RAILWAY_PUBLIC_DOMAIN"
        ]
        
        for var in railway_vars:
            value = os.getenv(var, "Not set")
            print(f"{var}: {value}")
        print()
    
    async def run_all_tests(self):
        """Run all diagnostic tests"""
        print("🚀 Railway Private Networking Diagnostic")
        print("=" * 50)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print()
        
        await self.test_environment_variables()
        await self.test_dns_resolution()
        await self.test_port_scanning()
        await self.test_http_connectivity()
        await self.test_background_task_context()
        await self.test_railway_metadata()
        
        print("🏁 Diagnostic Complete")
        print("=" * 50)
        
        # Save results to file
        with open("railway_diagnostic_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        print("Results saved to: railway_diagnostic_results.json")

if __name__ == "__main__":
    diagnostic = RailwayNetworkingDiagnostic()
    asyncio.run(diagnostic.run_all_tests())