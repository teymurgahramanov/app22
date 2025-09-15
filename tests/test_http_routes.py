import pytest
import time
from unittest.mock import patch
from fastapi import status


class TestHTTPRoutes:
    """Test cases for HTTP routes (/headers, /response)."""
    
    def test_headers_endpoint(self, test_client):
        """Test headers endpoint returns request headers."""
        # Add custom headers to the request
        custom_headers = {
            "X-Custom-Header": "test-value",
            "User-Agent": "test-agent",
            "Accept": "application/json"
        }
        
        response = test_client.get("/headers", headers=custom_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify our custom headers are in the response
        assert "x-custom-header" in data
        assert data["x-custom-header"] == "test-value"
        assert "user-agent" in data
        assert data["user-agent"] == "test-agent"
        assert "accept" in data
        assert data["accept"] == "application/json"
    
    def test_headers_endpoint_no_custom_headers(self, test_client):
        """Test headers endpoint with minimal headers."""
        response = test_client.get("/headers")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should still contain default headers from test client
        assert isinstance(data, dict)
        assert "host" in data  # TestClient adds host header
    
    def test_response_endpoint_default(self, test_client):
        """Test response endpoint with default parameters."""
        response = test_client.get("/response")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["status"] == 200
        assert data["delay"] == 0
    
    def test_response_endpoint_custom_status(self, test_client):
        """Test response endpoint with custom status code."""
        custom_status = 404
        response = test_client.get(f"/response?status={custom_status}")
        
        assert response.status_code == custom_status
        data = response.json()
        
        assert data["status"] == custom_status
        assert data["delay"] == 0
    
    def test_response_endpoint_with_delay(self, test_client):
        """Test response endpoint with delay parameter."""
        delay_seconds = 1
        start_time = time.time()
        
        response = test_client.get(f"/response?delay={delay_seconds}")
        
        end_time = time.time()
        actual_delay = end_time - start_time
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["status"] == 200
        assert data["delay"] == delay_seconds
        # Verify the delay actually occurred (with some tolerance)
        assert actual_delay >= delay_seconds - 0.1  # Allow 0.1s tolerance
    
    def test_response_endpoint_custom_status_and_delay(self, test_client):
        """Test response endpoint with both custom status and delay."""
        custom_status = 500
        delay_seconds = 1
        start_time = time.time()
        
        response = test_client.get(f"/response?status={custom_status}&delay={delay_seconds}")
        
        end_time = time.time()
        actual_delay = end_time - start_time
        
        assert response.status_code == custom_status
        data = response.json()
        
        assert data["status"] == custom_status
        assert data["delay"] == delay_seconds
        assert actual_delay >= delay_seconds - 0.1  # Allow 0.1s tolerance
    
    def test_response_endpoint_various_status_codes(self, test_client):
        """Test response endpoint with various HTTP status codes."""
        test_statuses = [200, 201, 400, 401, 403, 404, 500, 502, 503]
        
        for status_code in test_statuses:
            response = test_client.get(f"/response?status={status_code}")
            
            assert response.status_code == status_code
            data = response.json()
            assert data["status"] == status_code
    
    def test_response_endpoint_zero_delay(self, test_client):
        """Test response endpoint with explicit zero delay."""
        response = test_client.get("/response?delay=0")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["status"] == 200
        assert data["delay"] == 0
    
    def test_response_endpoint_invalid_parameters(self, test_client):
        """Test response endpoint with invalid parameters."""
        # Test with non-integer status (should use default or handle gracefully)
        response = test_client.get("/response?status=invalid")
        # FastAPI will return 422 for invalid query parameters
        assert response.status_code == 422
        
        # Test with non-integer delay
        response = test_client.get("/response?delay=invalid")
        assert response.status_code == 422 