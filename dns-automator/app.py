"""FastAPI app for DNS Automator service"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from dns_automator.main import DNSAutomator
from dns_automator.core.logging import setup_logging

# Setup logging
logger = setup_logging()


class ProcessRequest(BaseModel):
    """Request model for processing DNS"""
    supabase_url: str
    supabase_service_key: str
    site_id: Optional[str] = None


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


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "service": "dns-automator"}


@app.post("/process", response_model=ProcessResponse)
async def process_dns(request: ProcessRequest, background_tasks: BackgroundTasks):
    """
    Process DNS configuration for pending sites
    
    This endpoint is called by the Management Hub API with injected credentials
    """
    try:
        # Add the DNS automation to background tasks
        background_tasks.add_task(
            run_dns_automation,
            request.supabase_url,
            request.supabase_service_key,
            request.site_id
        )
        
        return ProcessResponse(
            status="accepted",
            message="DNS automation task started",
            task_id=request.site_id
        )
        
    except Exception as e:
        logger.error(f"Failed to start DNS automation: {e}")
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
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)