"""FastAPI app for Hosting Automator service"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from hosting_automator.main import HostingAutomator
from hosting_automator.core.logging import setup_logging

# Setup logging
logger = setup_logging()


class ProcessRequest(BaseModel):
    """Request model for processing hosting"""
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
    logger.info("Hosting Automator service starting up...")
    yield
    logger.info("Hosting Automator service shutting down...")


app = FastAPI(
    title="Hosting Automator",
    description="Hosting automation service for Website Factory",
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


def run_hosting_automation(supabase_url: str, supabase_service_key: str, site_id: Optional[str] = None):
    """Background task to run hosting automation"""
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
            automator = HostingAutomator()
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
        logger.error(f"Hosting automation failed: {e}")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "service": "hosting-automator"}


@app.post("/process", response_model=ProcessResponse)
async def process_hosting(request: ProcessRequest, background_tasks: BackgroundTasks):
    """
    Process hosting configuration for pending sites
    
    This endpoint is called by the Management Hub API with injected credentials
    """
    try:
        # Add the hosting automation to background tasks
        background_tasks.add_task(
            run_hosting_automation,
            request.supabase_url,
            request.supabase_service_key,
            request.site_id
        )
        
        return ProcessResponse(
            status="accepted",
            message="Hosting automation task started",
            task_id=request.site_id
        )
        
    except Exception as e:
        logger.error(f"Failed to start hosting automation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "hosting-automator",
        "version": "1.0.0",
        "features": [
            "cloudpanel",
            "ssl",
            "matomo"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)