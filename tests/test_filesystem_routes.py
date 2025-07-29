import pytest
import os
import tempfile
import hashlib
from unittest.mock import patch, mock_open
from fastapi import status


class TestFilesystemRoutes:
    """Test cases for filesystem routes (/cat)."""
    
    def test_cat_endpoint_with_text_files(self, test_client, tmp_path):
        """Test cat endpoint with text files."""
        # Create temporary data directory structure
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        
        # Create test text file
        test_file_content = "Hello, World!\nThis is a test file."
        test_file = data_dir / "test.txt"
        test_file.write_text(test_file_content)
        
        # Calculate expected checksum
        expected_checksum = hashlib.md5(test_file_content.encode()).hexdigest()
        
        with patch('app.routes.filesystem.os.walk') as mock_walk:
            with patch('builtins.open', mock_open(read_data=test_file_content.encode())):
                with patch('app.routes.filesystem.os.path.abspath') as mock_abspath:
                    # Mock os.walk to return our test file
                    mock_walk.return_value = [("data", [], ["test.txt"])]
                    mock_abspath.return_value = str(test_file)
                    
                    response = test_client.get("/cat")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert str(test_file) in data
        file_data = data[str(test_file)]
        assert file_data["checksum"] == expected_checksum
        assert file_data["content"] == test_file_content
    
    def test_cat_endpoint_with_image_files(self, test_client, tmp_path):
        """Test cat endpoint with image files (should be ignored)."""
        # Create temporary data directory
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        
        # Create test image file
        image_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'  # PNG header
        test_file = data_dir / "test.png"
        test_file.write_bytes(image_content)
        
        # Calculate expected checksum
        expected_checksum = hashlib.md5(image_content).hexdigest()
        
        with patch('app.routes.filesystem.os.walk') as mock_walk:
            with patch('builtins.open', mock_open(read_data=image_content)):
                with patch('app.routes.filesystem.os.path.abspath') as mock_abspath:
                    # Mock os.walk to return our test file
                    mock_walk.return_value = [("data", [], ["test.png"])]
                    mock_abspath.return_value = str(test_file)
                    
                    response = test_client.get("/cat")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert str(test_file) in data
        file_data = data[str(test_file)]
        assert file_data["checksum"] == expected_checksum
        assert file_data["content"] == "-"  # Should be ignored for image files
    
    def test_cat_endpoint_with_binary_files(self, test_client, tmp_path):
        """Test cat endpoint with binary files that can't be decoded."""
        # Create temporary data directory
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        
        # Create test binary file with invalid UTF-8
        binary_content = b'\x80\x81\x82\x83\x84\x85'  # Invalid UTF-8 sequence
        test_file = data_dir / "test.bin"
        test_file.write_bytes(binary_content)
        
        # Calculate expected checksum
        expected_checksum = hashlib.md5(binary_content).hexdigest()
        
        with patch('app.routes.filesystem.os.walk') as mock_walk:
            with patch('builtins.open', mock_open(read_data=binary_content)):
                with patch('app.routes.filesystem.os.path.abspath') as mock_abspath:
                    # Mock os.walk to return our test file
                    mock_walk.return_value = [("data", [], ["test.bin"])]
                    mock_abspath.return_value = str(test_file)
                    
                    response = test_client.get("/cat")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert str(test_file) in data
        file_data = data[str(test_file)]
        assert file_data["checksum"] == expected_checksum
        assert file_data["content"] == "-"  # Should be "-" for non-decodable files
    
    def test_cat_endpoint_multiple_files(self, test_client, tmp_path):
        """Test cat endpoint with multiple files of different types."""
        # Create temporary data directory
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        
        # Create multiple test files
        files_data = [
            ("text.txt", "Text file content", False),
            ("image.jpg", b'\xff\xd8\xff\xe0', True),  # JPEG header
            ("config.json", '{"key": "value"}', False)
        ]
        
        expected_results = {}
        
        for filename, content, is_binary in files_data:
            if is_binary:
                file_content = content
                checksum = hashlib.md5(content).hexdigest()
            else:
                file_content = content.encode()
                checksum = hashlib.md5(file_content).hexdigest()
            
            filepath = str(data_dir / filename)
            expected_results[filepath] = {
                "checksum": checksum,
                "content": "-" if is_binary or filename.endswith('.jpg') else content
            }
        
        # Mock file data for each file
        def mock_open_func(filepath, mode='rb'):
            filename = os.path.basename(filepath)
            for fname, content, is_binary in files_data:
                if fname == filename:
                    if is_binary:
                        return mock_open(read_data=content).return_value
                    else:
                        return mock_open(read_data=content.encode()).return_value
            return mock_open(read_data=b'').return_value
        
        with patch('app.routes.filesystem.os.walk') as mock_walk:
            with patch('builtins.open', side_effect=mock_open_func):
                with patch('app.routes.filesystem.os.path.abspath', side_effect=lambda x: str(data_dir / os.path.basename(x))):
                    # Mock os.walk to return all test files
                    mock_walk.return_value = [("data", [], [f[0] for f in files_data])]
                    
                    response = test_client.get("/cat")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Verify all files are processed correctly
        for filepath, expected in expected_results.items():
            assert filepath in data
            assert data[filepath]["checksum"] == expected["checksum"]
            assert data[filepath]["content"] == expected["content"]
    
    def test_cat_endpoint_empty_directory(self, test_client):
        """Test cat endpoint with empty data directory."""
        with patch('app.routes.filesystem.os.walk') as mock_walk:
            # Mock os.walk to return empty directory
            mock_walk.return_value = [("data", [], [])]
            
            response = test_client.get("/cat")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data == {}
    
    def test_cat_endpoint_no_data_directory(self, test_client):
        """Test cat endpoint when data directory doesn't exist."""
        with patch('app.routes.filesystem.os.walk') as mock_walk:
            # Mock os.walk to raise an exception (directory not found)
            mock_walk.side_effect = FileNotFoundError("No such file or directory")
            
            # The endpoint should handle this gracefully or raise an error
            # This depends on the actual implementation behavior
            with pytest.raises(FileNotFoundError):
                response = test_client.get("/cat") 