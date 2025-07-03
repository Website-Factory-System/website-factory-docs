"""FastAPI app for DNS Automator service"""

print("🟢 DEBUG: app.py module loading...")

import os
import logging
from contextlib import asynccontextmanager
from typing import Optional

print("🟢 DEBUG: Basic imports done, loading FastAPI...")

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

print("🟢 DEBUG: FastAPI imported, loading DNS automator...")

from dns_automator.main import DNSAutomator
print("🟢 DEBUG: DNSAutomator imported")

from dns_automator.core.logging import setup_logging
print("🟢 DEBUG: logging setup imported")

# Setup logging
print("🟢 DEBUG: Setting up logging...")
logger = setup_logging()
print("🟢 DEBUG: Logger setup complete in app.py")


class ProcessRequest(BaseModel):
    """Request model for processing DNS"""
    site_id: str


class ProcessResponse(BaseModel):
    """Response model for process request"""
    status: str
    message: str
    task_id: Optional[str] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the app"""
    logger.info("DNS Automator service starting up...")
    yield
    logger.info("DNS Automator service shutting down...")


app = FastAPI(
    title="DNS Automator",
    description="DNS automation service for Website Factory",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def run_dns_automation(supabase_url: str, supabase_service_key: str, site_id: Optional[str] = None):
    """Background task to run DNS automation"""
    try:
        # Temporarily set environment variables for this execution
        original_url = os.environ.get("SUPABASE_URL")
        original_key = os.environ.get("SUPABASE_SERVICE_KEY")
        
        os.environ["SUPABASE_URL"] = supabase_url
        os.environ["SUPABASE_SERVICE_KEY"] = supabase_service_key
        
        if site_id:
            os.environ["SITE_ID"] = site_id
        
        try:
            # Run the automator
            automator = DNSAutomator()
            automator.run()
        finally:
            # Restore original environment
            if original_url:
                os.environ["SUPABASE_URL"] = original_url
            else:
                os.environ.pop("SUPABASE_URL", None)
                
            if original_key:
                os.environ["SUPABASE_SERVICE_KEY"] = original_key
            else:
                os.environ.pop("SUPABASE_SERVICE_KEY", None)
                
            os.environ.pop("SITE_ID", None)
            
    except Exception as e:
        logger.error(f"DNS automation failed: {e}")


def run_dns_automation_sync(site_id: str) -> bool:
    """Synchronous DNS automation that returns the actual result"""
    print("🟢 DEBUG: run_dns_automation_sync() called")
    print(f"🟢 DEBUG: site_id={site_id}")
    
    try:
        print("🟢 DEBUG: Setting environment variables...")
        # Set SITE_ID for this execution
        original_site_id = os.environ.get("SITE_ID")
        os.environ["SITE_ID"] = site_id
        
        print("🟢 DEBUG: Environment variables set, creating DNSAutomator...")
        
        try:
            # Run the automator and get result
            automator = DNSAutomator()
            
            print("🟢 DEBUG: DNSAutomator created, fetching pending sites...")
            # Get the specific site by ID
            sites = automator.data_client.fetch_pending_dns_sites(site_id)
            
            print(f"🟢 DEBUG: Found {len(sites) if sites else 0} sites")
            
            if not sites:
                print("🟢 DEBUG: No site found with specified ID")
                logger.warning(f"No site found with ID: {site_id}")
                return False
                
            print(f"🟢 DEBUG: Processing site: {sites[0].get('domain', 'unknown')}")
            # Process the site
            result = automator.process_site(sites[0])
            
            print(f"🟢 DEBUG: Processing result: {result}")
            return result
            
        finally:
            # Restore original environment
            if original_site_id:
                os.environ["SITE_ID"] = original_site_id
            else:
                os.environ.pop("SITE_ID", None)
            
    except Exception as e:
        logger.error(f"DNS automation failed: {e}")
        return False


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "service": "dns-automator"}


@app.post("/process", response_model=ProcessResponse)
async def process_dns(request: ProcessRequest):
    """
    Process DNS configuration for a specific site
    
    This endpoint uses Railway shared variables for database access
    """
    print("🟢 DEBUG: /process endpoint called")
    print(f"🟢 DEBUG: request.site_id={request.site_id}")
    
    try:
        print("🟢 DEBUG: About to call run_dns_automation_sync...")
        # Run DNS automation synchronously to get the actual result
        result = run_dns_automation_sync(request.site_id)
        
        print(f"🟢 DEBUG: run_dns_automation_sync returned: {result}")
        
        if result:
            return ProcessResponse(
                status="completed",
                message="DNS automation completed successfully",
                task_id=request.site_id
            )
        else:
            return ProcessResponse(
                status="failed", 
                message="DNS automation failed - check logs for details",
                task_id=request.site_id
            )
        
    except Exception as e:
        logger.error(f"Failed to run DNS automation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "dns-automator",
        "version": "1.0.0",
        "features": [
            "namecheap",
            "spaceship",
            "cloudflare"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8080))
    # Use :: for IPv6 dual-stack to support Railway private networking
    uvicorn.run(app, host="::", port=port)