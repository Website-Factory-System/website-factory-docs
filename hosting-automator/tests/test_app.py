"""Tests for FastAPI app"""

import pytest
from fastapi.testclient import TestClient
from app import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "hosting-automator"
    assert "cloudpanel" in data["features"]


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_process_endpoint(client):
    """Test process endpoint"""
    request_data = {
        "supabase_url": "https://test.supabase.co",
        "supabase_service_key": "test-key"
    }
    
    response = client.post("/process", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "accepted"
    assert "automation task started" in data["message"]