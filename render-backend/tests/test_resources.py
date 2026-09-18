import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Note: comprehensive tests would require a mock database or a test Supabase instance.
# Here we mock the `get_supabase` and `get_current_user` to simulate behavior.

def test_add_resource_missing_auth():
    response = client.post("/api/tasks/task-123/resources", json={"url": "https://example.com", "title": "Example"})
    assert response.status_code == 401

def test_list_resources_missing_auth():
    response = client.get("/api/tasks/task-123/resources")
    assert response.status_code == 401

def test_delete_resource_missing_auth():
    response = client.delete("/api/tasks/task-123/resources/res-123")
    assert response.status_code == 401

# The remaining tests require valid auth and DB simulation.
# In a real setup, these would be integration tests hitting a test database.
