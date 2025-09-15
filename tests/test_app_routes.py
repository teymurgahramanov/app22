import pytest
from unittest.mock import patch
from fastapi import status


class TestAppRoutes:
    """Test cases for app routes (/version, /healthz, /log)."""
    
    def test_version_endpoint(self, test_client):
        """Test the version endpoint returns correct version."""
        response = test_client.get("/version")
        assert response.status_code == status.HTTP_200_OK
        # Should return the version as an object now
        data = response.json()
        assert "version" in data
        assert data["version"] == "v1.0.0"
    
    def test_healthz_endpoint_healthy(self, test_client):
        """Test health check when system is healthy."""
        response = test_client.get("/healthz")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "healthy" in data
        assert data["healthy"] is True
    
    def test_healthz_toggle_endpoint(self, test_client):
        """Test health check toggle functionality."""
        # First, ensure it's healthy
        response = test_client.get("/healthz")
        assert response.status_code == status.HTTP_200_OK
        initial_health = response.json()["healthy"]
        
        # Toggle health status
        response = test_client.get("/healthz/toggle")
        assert response.status_code == status.HTTP_200_OK
        toggled_health = response.json()["healthy"]
        assert toggled_health != initial_health
        
        # Check health status has changed
        response = test_client.get("/healthz")
        if toggled_health:
            assert response.status_code == status.HTTP_200_OK
            assert response.json()["healthy"] is True
        else:
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json()["detail"]["healthy"] is False
    
    def test_healthz_endpoint_unhealthy(self, test_client):
        """Test health check when system is unhealthy."""
        # Toggle to unhealthy state first
        test_client.get("/healthz/toggle")  # Ensure it's unhealthy
        test_client.get("/healthz/toggle")  # Toggle to unhealthy
        
        response = test_client.get("/healthz")
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json()["detail"]["healthy"] is False
    
    @patch('app.routes.app.logger')
    def test_log_endpoint_with_message(self, mock_logger, test_client):
        """Test logging endpoint with a message."""
        test_message = "Test log message"
        response = test_client.get(f"/log?message={test_message}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "Message logged successfully" in data["message"]
        assert data["logged_message"] == test_message
        
        # Verify all log levels were called
        mock_logger.debug.assert_called_once_with(test_message)
        mock_logger.info.assert_called_once_with(test_message)
        mock_logger.warning.assert_called_once_with(test_message)
        mock_logger.error.assert_called_once_with(test_message)
    
    @patch('app.routes.app.logger')
    def test_log_endpoint_without_message(self, mock_logger, test_client):
        """Test logging endpoint without a message parameter."""
        response = test_client.get("/log")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "Message logged successfully" in data["message"]
        assert data["logged_message"] is None
        
        # Verify all log levels were called with None
        mock_logger.debug.assert_called_once_with(None)
        mock_logger.info.assert_called_once_with(None)
        mock_logger.warning.assert_called_once_with(None)
        mock_logger.error.assert_called_once_with(None)
    
    def test_log_endpoint_with_special_characters(self, test_client):
        """Test logging endpoint with special characters in message."""
        test_message = "Test with special chars: !@#$%^&*()"
        # Use JSON body instead of URL params to avoid encoding issues
        response = test_client.get("/log", params={"message": test_message})
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["logged_message"] == test_message
    
    def test_log_endpoint_with_newlines(self, test_client):
        """Test logging endpoint sanitizes newlines to prevent log injection."""
        test_message = "Test with\nnewlines\rand\r\ncarriage returns"
        # Use params to properly encode the message
        response = test_client.get("/log", params={"message": test_message})
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        # Newlines should be replaced with spaces
        assert "\n" not in data["logged_message"]
        assert "\r" not in data["logged_message"] 