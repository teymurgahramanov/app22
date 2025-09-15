import pytest
import os
from unittest.mock import patch, MagicMock
from fastapi import status


class TestSystemRoutes:
    """Test cases for system routes (/sys, /env, /crash)."""
    
    @patch('app.routes.system.psutil')
    @patch('app.routes.system.platform')
    @patch('app.routes.system.socket')
    @patch('app.routes.system.datetime')
    @patch('app.routes.system.time')
    def test_sys_endpoint(self, mock_time, mock_datetime, mock_socket, mock_platform, mock_psutil, test_client):
        """Test system information endpoint."""
        # Mock all dependencies
        mock_socket.gethostname.return_value = "test-host"
        mock_datetime.datetime.now.return_value = "2023-01-01T00:00:00"
        mock_time.time.return_value = 1000000
        mock_psutil.boot_time.return_value = 999000
        
        # Mock platform information
        mock_platform.system.return_value = "Linux"
        mock_platform.node.return_value = "test-node"
        mock_platform.release.return_value = "5.4.0"
        mock_platform.version.return_value = "test-version"
        mock_platform.machine.return_value = "x86_64"
        mock_platform.processor.return_value = "test-processor"
        mock_platform.architecture.return_value = ("64bit", "ELF")
        mock_platform.platform.return_value = "Linux-5.4.0"
        
        # Mock CPU information
        mock_psutil.cpu_count.side_effect = [4, 8]  # physical_cores, total_cores
        mock_freq = MagicMock()
        mock_freq.max = 3000.0
        mock_freq.current = 2500.0
        mock_psutil.cpu_freq.return_value = mock_freq
        mock_psutil.cpu_percent.return_value = 25.0
        
        # Mock memory information
        mock_memory = MagicMock()
        mock_memory.total = 8589934592  # 8GB
        mock_memory.available = 4294967296  # 4GB
        mock_memory.percent = 50.0
        mock_memory.used = 4294967296  # 4GB
        mock_memory.free = 4294967296  # 4GB
        mock_psutil.virtual_memory.return_value = mock_memory
        
        response = test_client.get("/sys")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify response structure
        assert "hostname" in data
        assert "timedate" in data
        assert "uptime" in data
        assert "platform" in data
        assert "cpu" in data
        assert "memory" in data
        
        # Verify platform data
        platform_data = data["platform"]
        assert platform_data["system"] == "Linux"
        assert platform_data["machine"] == "x86_64"
        
        # Verify CPU data
        cpu_data = data["cpu"]
        assert cpu_data["physical_cores"] == 4
        assert cpu_data["total_cores"] == 8
        assert cpu_data["max_frequency"] == 3000.0
        assert cpu_data["current_frequency"] == 2500.0
        assert cpu_data["cpu_usage_percent"] == 25.0
        
        # Verify memory data
        memory_data = data["memory"]
        assert memory_data["total"] == 8589934592
        assert memory_data["available"] == 4294967296
        assert memory_data["percent"] == 50.0
    
    @patch('app.routes.system.psutil.cpu_freq')
    def test_sys_endpoint_no_cpu_freq(self, mock_cpu_freq, test_client):
        """Test system endpoint when CPU frequency is not available."""
        mock_cpu_freq.return_value = None
        
        response = test_client.get("/sys")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        cpu_data = data["cpu"]
        assert cpu_data["max_frequency"] is None
        assert cpu_data["current_frequency"] is None
    
    def test_env_endpoint(self, test_client):
        """Test environment variables endpoint."""
        # Set some test environment variables
        test_env_vars = {
            "TEST_VAR_1": "test_value_1",
            "TEST_VAR_2": "test_value_2"
        }
        
        with patch.dict(os.environ, test_env_vars):
            response = test_client.get("/env")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify our test variables are in the response
        for key, value in test_env_vars.items():
            assert key in data
            assert data[key] == value
    
    def test_env_endpoint_empty_environment(self, test_client):
        """Test environment variables endpoint with minimal environment."""
        with patch.dict(os.environ, {}, clear=True):
            response = test_client.get("/env")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, dict)
    
    @patch('app.routes.system.os._exit')
    def test_crash_endpoint(self, mock_exit, test_client):
        """Test crash simulation endpoint."""
        response = test_client.get("/crash")
        
        # The endpoint should call os._exit(255)
        mock_exit.assert_called_once_with(255)
        
        # Note: In a real scenario, this would terminate the process
        # But our mock prevents that from happening in tests 