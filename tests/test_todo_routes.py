import pytest
import uuid
from fastapi import status
from app.routes.database import Tasks


class TestTodoRoutes:
    """Test cases for todo routes (CRUD operations on tasks)."""
    
    def test_create_task_success(self, test_client, sample_task_data):
        """Test successful task creation."""
        response = test_client.post("/tasks", json=sample_task_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert "title" in data
        assert "description" in data
        assert "done" in data
        assert "updated_at" in data
        
        # Verify data matches input
        assert data["title"] == sample_task_data["title"]
        assert data["description"] == sample_task_data["description"]
        assert data["done"] == sample_task_data["done"]
        
        # Verify ID is a valid UUID
        assert uuid.UUID(data["id"])
    
    def test_create_task_minimal_data(self, test_client):
        """Test task creation with minimal required data."""
        minimal_task = {"title": "Minimal Task"}
        
        response = test_client.post("/tasks", json=minimal_task)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert data["title"] == "Minimal Task"
        assert data["description"] == ""  # Should default to empty string
        assert data["done"] is False  # Should default to False
    
    def test_create_task_invalid_data(self, test_client):
        """Test task creation with invalid data."""
        # Missing required title field
        invalid_task = {"description": "Task without title"}
        
        response = test_client.post("/tasks", json=invalid_task)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_tasks_empty_list(self, test_client):
        """Test retrieving tasks when none exist."""
        response = test_client.get("/tasks")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_tasks_with_data(self, test_client, sample_task_data):
        """Test retrieving tasks when some exist."""
        # Create a few tasks first
        created_tasks = []
        for i in range(3):
            task_data = sample_task_data.copy()
            task_data["title"] = f"Task {i+1}"
            response = test_client.post("/tasks", json=task_data)
            created_tasks.append(response.json())
        
        # Retrieve tasks
        response = test_client.get("/tasks")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 3
        
        # Verify tasks are ordered by updated_at desc (most recent first)
        task_ids = [task["id"] for task in data]
        created_ids = [task["id"] for task in reversed(created_tasks)]  # Reverse due to desc order
        assert task_ids == created_ids
    
    def test_get_tasks_with_limit(self, test_client, sample_task_data):
        """Test retrieving tasks with limit parameter."""
        # Create more tasks than we'll request
        for i in range(5):
            task_data = sample_task_data.copy()
            task_data["title"] = f"Task {i+1}"
            test_client.post("/tasks", json=task_data)
        
        # Get with limit
        response = test_client.get("/tasks?limit=3")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 3
    
    def test_get_task_by_id_success(self, test_client, sample_task_data):
        """Test retrieving a specific task by ID."""
        # Create a task first
        create_response = test_client.post("/tasks", json=sample_task_data)
        created_task = create_response.json()
        task_id = created_task["id"]
        
        # Retrieve the task by ID
        response = test_client.get(f"/tasks/{task_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["id"] == task_id
        assert data["title"] == sample_task_data["title"]
        assert data["description"] == sample_task_data["description"]
        assert data["done"] == sample_task_data["done"]
    
    def test_get_task_by_id_not_found(self, test_client):
        """Test retrieving a non-existent task."""
        fake_id = str(uuid.uuid4())
        
        response = test_client.get(f"/tasks/{fake_id}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "Task not found"
    
    def test_update_task_success(self, test_client, sample_task_data, sample_task_update_data):
        """Test successful task update."""
        # Create a task first
        create_response = test_client.post("/tasks", json=sample_task_data)
        created_task = create_response.json()
        task_id = created_task["id"]
        
        # Update the task
        response = test_client.put(f"/tasks/{task_id}", json=sample_task_update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["id"] == task_id
        assert data["title"] == sample_task_update_data["title"]
        assert data["description"] == sample_task_update_data["description"]
        assert data["done"] == sample_task_update_data["done"]
        
        # Verify updated_at has changed
        assert data["updated_at"] != created_task["updated_at"]
    
    def test_update_task_partial(self, test_client, sample_task_data):
        """Test partial task update (only some fields)."""
        # Create a task first
        create_response = test_client.post("/tasks", json=sample_task_data)
        created_task = create_response.json()
        task_id = created_task["id"]
        
        # Update only the title
        partial_update = {"title": "Updated Title Only"}
        response = test_client.put(f"/tasks/{task_id}", json=partial_update)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["id"] == task_id
        assert data["title"] == "Updated Title Only"
        # Other fields should remain unchanged
        assert data["description"] == sample_task_data["description"]
        assert data["done"] == sample_task_data["done"]
    
    def test_update_task_not_found(self, test_client, sample_task_update_data):
        """Test updating a non-existent task."""
        fake_id = str(uuid.uuid4())
        
        response = test_client.put(f"/tasks/{fake_id}", json=sample_task_update_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "Task not found"
    
    def test_delete_task_success(self, test_client, sample_task_data):
        """Test successful task deletion."""
        # Create a task first
        create_response = test_client.post("/tasks", json=sample_task_data)
        created_task = create_response.json()
        task_id = created_task["id"]
        
        # Delete the task
        response = test_client.delete(f"/tasks/{task_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Task deleted successfully"
        
        # Verify task is actually deleted
        get_response = test_client.get(f"/tasks/{task_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_task_not_found(self, test_client):
        """Test deleting a non-existent task."""
        fake_id = str(uuid.uuid4())
        
        response = test_client.delete(f"/tasks/{fake_id}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"] == "Task not found"
    
    def test_task_crud_workflow(self, test_client):
        """Test complete CRUD workflow for tasks."""
        # Create
        task_data = {
            "title": "Workflow Test Task",
            "description": "Testing complete workflow",
            "done": False
        }
        create_response = test_client.post("/tasks", json=task_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        created_task = create_response.json()
        task_id = created_task["id"]
        
        # Read
        read_response = test_client.get(f"/tasks/{task_id}")
        assert read_response.status_code == status.HTTP_200_OK
        read_task = read_response.json()
        assert read_task["title"] == task_data["title"]
        
        # Update
        update_data = {"done": True, "title": "Completed Workflow Test"}
        update_response = test_client.put(f"/tasks/{task_id}", json=update_data)
        assert update_response.status_code == status.HTTP_200_OK
        updated_task = update_response.json()
        assert updated_task["done"] is True
        assert updated_task["title"] == "Completed Workflow Test"
        
        # Delete
        delete_response = test_client.delete(f"/tasks/{task_id}")
        assert delete_response.status_code == status.HTTP_200_OK
        
        # Verify deletion
        final_read_response = test_client.get(f"/tasks/{task_id}")
        assert final_read_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_task_data_persistence(self, test_client, sample_task_data):
        """Test that task data persists correctly across operations."""
        # Create multiple tasks
        task_ids = []
        for i in range(3):
            task_data = sample_task_data.copy()
            task_data["title"] = f"Persistence Test {i+1}"
            response = test_client.post("/tasks", json=task_data)
            task_ids.append(response.json()["id"])
        
        # Verify all tasks exist
        for task_id in task_ids:
            response = test_client.get(f"/tasks/{task_id}")
            assert response.status_code == status.HTTP_200_OK
        
        # Verify list contains all tasks
        list_response = test_client.get("/tasks")
        all_tasks = list_response.json()
        retrieved_ids = [task["id"] for task in all_tasks]
        
        for task_id in task_ids:
            assert task_id in retrieved_ids
    
    def test_invalid_task_id_format(self, test_client):
        """Test endpoints with invalid UUID format."""
        invalid_id = "not-a-uuid"
        
        # Test get, update, and delete with invalid ID
        get_response = test_client.get(f"/tasks/{invalid_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
        
        update_response = test_client.put(f"/tasks/{invalid_id}", json={"title": "Test"})
        assert update_response.status_code == status.HTTP_404_NOT_FOUND
        
        delete_response = test_client.delete(f"/tasks/{invalid_id}")
        assert delete_response.status_code == status.HTTP_404_NOT_FOUND 