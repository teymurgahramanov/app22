import pytest
from fastapi import status


class TestMainRoutes:
    """Test cases for main application routes."""
    
    def test_index_redirect(self, test_client):
        """Test that index route redirects to docs."""
        response = test_client.get("/", allow_redirects=False)
        
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert response.headers["location"] == "/docs"
    
    def test_docs_endpoint_accessible(self, test_client):
        """Test that docs endpoint is accessible."""
        response = test_client.get("/docs")
        
        assert response.status_code == status.HTTP_200_OK
        # Should contain FastAPI docs content
        assert "text/html" in response.headers.get("content-type", "")
    
    def test_redoc_endpoint_accessible(self, test_client):
        """Test that redoc endpoint is accessible."""
        response = test_client.get("/redoc")
        
        assert response.status_code == status.HTTP_200_OK
        # Should contain ReDoc content
        assert "text/html" in response.headers.get("content-type", "")
    
    def test_metrics_endpoint(self, test_client):
        """Test Prometheus metrics endpoint."""
        response = test_client.get("/metrics")
        
        assert response.status_code == status.HTTP_200_OK
        # Should return plain text metrics
        assert response.headers.get("content-type") == "text/plain; charset=utf-8"
        
        # Should contain Prometheus metrics format
        content = response.text
        assert "# HELP" in content or "# TYPE" in content or len(content) > 0
    
    def test_openapi_json_endpoint(self, test_client):
        """Test OpenAPI schema endpoint."""
        response = test_client.get("/openapi.json")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should contain OpenAPI schema structure
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
        assert data["info"]["title"] == "App22"
        assert data["info"]["version"] == "v1.0.0" 