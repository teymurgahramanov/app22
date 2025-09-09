import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import create_app
from app.routes.database import get_db, Base
from config import Config


@pytest.fixture
def test_db():
    """Create a temporary SQLite database for testing."""
    # Create a temporary file for the database
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    
    # Create test database engine
    test_engine = create_engine(f"sqlite:///{db_path}", echo=False)
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    yield TestSessionLocal, test_engine
    
    # Cleanup
    os.unlink(db_path)


@pytest.fixture
def test_client(test_db):
    """Create a test client with test database."""
    TestSessionLocal, test_engine = test_db
    
    def override_get_db():
        try:
            db = TestSessionLocal()
            yield db
        finally:
            db.close()
    
    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client


@pytest.fixture
def test_config():
    """Create test configuration."""
    return Config(
        db_url="sqlite:///test.db",
        debug=True,
        secret_key="test-secret-key"
    )


@pytest.fixture
def sample_task_data():
    """Sample task data for testing."""
    return {
        "title": "Test Task",
        "description": "This is a test task",
        "done": False
    }


@pytest.fixture
def sample_task_update_data():
    """Sample task update data for testing."""
    return {
        "title": "Updated Test Task",
        "description": "This is an updated test task",
        "done": True
    }


@pytest.fixture
def mock_filesystem_data(tmp_path):
    """Create temporary files for filesystem testing."""
    # Create test data directory
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    
    # Create test files
    text_file = data_dir / "test.txt"
    text_file.write_text("Hello, World!")
    
    binary_file = data_dir / "test.jpg"
    binary_file.write_bytes(b'\x89PNG\r\n\x1a\n')  # PNG header
    
    return data_dir 