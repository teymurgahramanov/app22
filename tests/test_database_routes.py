import pytest
import datetime
from unittest.mock import patch, MagicMock
from fastapi import status
from sqlalchemy.orm import Session
from app.routes.database import Requests


class TestDatabaseRoutes:
    """Test cases for database routes (/database)."""
    
    def test_database_endpoint_successful_operation(self, test_client):
        """Test database endpoint with successful database operations."""
        response = test_client.get("/database")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify response structure
        assert "db" in data
        assert "connected" in data
        assert "writable" in data
        assert "data" in data
        
        # Should be connected and writable with test database
        assert data["connected"] is True
        assert data["writable"] is True
        assert isinstance(data["data"], list)
        
        # Should contain database URI information
        assert "sqlite" in data["db"]
    
    def test_database_endpoint_with_limit_parameter(self, test_client):
        """Test database endpoint with custom limit parameter."""
        # First, create some test records
        for i in range(5):
            test_client.get("/database")
        
        # Now test with different limits
        response = test_client.get("/database?limit=3")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should return at most 3 records
        assert len(data["data"]) <= 3
    
    def test_database_endpoint_multiple_requests(self, test_client):
        """Test database endpoint logs multiple requests correctly."""
        # Make multiple requests
        num_requests = 3
        for i in range(num_requests):
            response = test_client.get("/database")
            assert response.status_code == status.HTTP_200_OK
        
        # Get the latest state
        response = test_client.get("/database?limit=10")
        data = response.json()
        
        # Should have at least the requests we made (plus one from the last call)
        assert len(data["data"]) >= num_requests
        
        # Verify the structure of returned records
        for record in data["data"]:
            assert "id" in record
            assert "timestamp" in record
            assert "source" in record
            assert isinstance(record["id"], int)
    
    def test_database_endpoint_default_limit(self, test_client):
        """Test database endpoint uses default limit of 5."""
        # Create more than 5 requests
        for i in range(7):
            test_client.get("/database")
        
        # Get without specifying limit (should default to 5)
        response = test_client.get("/database")
        data = response.json()
        
        # Should return at most 5 records (default limit)
        assert len(data["data"]) <= 5
    
    def test_database_endpoint_records_client_ip(self, test_client):
        """Test that database endpoint records client IP correctly."""
        response = test_client.get("/database")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should have at least one record
        assert len(data["data"]) >= 1
        
        # The test client should provide a source IP
        latest_record = data["data"][0]  # Records are ordered by ID desc
        assert "source" in latest_record
        assert latest_record["source"] == "testclient"  # TestClient default
    
    def test_database_endpoint_with_db_write_error(self, test_client, test_db):
        """Test database endpoint when write operations fail."""
        TestSessionLocal, test_engine = test_db
        
        with patch('app.routes.database.get_db') as mock_get_db:
            # Create a mock session that raises an exception on commit
            mock_session = MagicMock()
            mock_session.commit.side_effect = Exception("Database write error")
            mock_session.query.return_value.order_by.return_value.limit.return_value.all.return_value = []
            
            mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_get_db.return_value.__exit__ = MagicMock()
            
            response = test_client.get("/database")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should indicate write failure
        assert data["writable"] is False
        assert "exception" in data
        assert data["connected"] is True  # Read operations still work
    
    def test_database_endpoint_with_db_read_error(self, test_client, test_db):
        """Test database endpoint when read operations fail."""
        TestSessionLocal, test_engine = test_db
        
        with patch('app.routes.database.get_db') as mock_get_db:
            # Create a mock session that raises an exception on query
            mock_session = MagicMock()
            mock_session.commit.return_value = None  # Write succeeds
            mock_session.query.side_effect = Exception("Database read error")
            
            mock_get_db.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_get_db.return_value.__exit__ = MagicMock()
            
            response = test_client.get("/database")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should indicate connection failure
        assert data["connected"] is False
        assert "exception" in data
        assert data["writable"] is True  # Write operation succeeded
    
    def test_database_endpoint_records_timestamp(self, test_client):
        """Test that database endpoint records timestamps correctly."""
        before_request = datetime.datetime.now()
        
        response = test_client.get("/database")
        
        after_request = datetime.datetime.now()
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should have at least one record
        assert len(data["data"]) >= 1
        
        # Check that timestamp is reasonable (between before and after)
        latest_record = data["data"][0]
        timestamp_str = latest_record["timestamp"]
        
        # Parse the timestamp (assuming ISO format)
        recorded_time = datetime.datetime.fromisoformat(timestamp_str.replace('Z', '+00:00').replace('+00:00', ''))
        
        # Should be within reasonable time range
        time_diff = abs((recorded_time - before_request).total_seconds())
        assert time_diff < 60  # Should be within a minute
    
    def test_database_endpoint_limit_edge_cases(self, test_client):
        """Test database endpoint with edge case limit values."""
        # Test with limit 0
        response = test_client.get("/database?limit=0")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 0
        
        # Test with very large limit
        response = test_client.get("/database?limit=1000")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should work without error, though may return fewer records
        assert isinstance(data["data"], list)
    
    def test_database_endpoint_invalid_limit(self, test_client):
        """Test database endpoint with invalid limit parameter."""
        # Test with non-integer limit
        response = test_client.get("/database?limit=invalid")
        
        # FastAPI should return 422 for invalid query parameters
        assert response.status_code == 422 