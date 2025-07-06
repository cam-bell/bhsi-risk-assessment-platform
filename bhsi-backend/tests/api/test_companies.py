import pytest
from fastapi.testclient import TestClient
from tests.utils.utils import get_test_company_data, get_test_classification_data


def test_search_endpoint(client: TestClient):
    """Test the main search endpoint with minimal data"""
    data = get_test_company_data()
    data["id"] = "test-company-id-123"
    response = client.post(
        "/api/v1/search",
        json=data
    )
    assert response.status_code == 200
    data = response.json()
    assert "company_name" in data
    assert "metadata" in data
    assert "performance" in data


def test_health_endpoint(client: TestClient):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_api_root(client: TestClient):
    """Test root API endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "BHSI" in data["message"]


def test_search_performance_endpoint(client: TestClient):
    """Test search performance endpoint"""
    response = client.get("/api/v1/search/performance")
    assert response.status_code == 200
    data = response.json()
    assert "total_searches" in data
    

def test_search_health_endpoint(client: TestClient):
    """Test search health endpoint"""
    response = client.get("/api/v1/search/health")
    assert response.status_code == 200
    data = response.json()
    assert "streamlined_orchestrator" in data
    assert "hybrid_classifier" in data 