from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Note: comprehensive tests would require a mock database or a test Supabase instance.
# Here we verify unauthenticated requests are rejected (401 Unauthorized or 403 Forbidden).

def test_add_resource_missing_auth():
    response = client.post("/api/tasks/task-123/resources", json={"url": "https://example.com", "title": "Example"})
    assert response.status_code in (401, 403)

def test_list_resources_missing_auth():
    response = client.get("/api/tasks/task-123/resources")
    assert response.status_code in (401, 403)

def test_delete_resource_missing_auth():
    response = client.delete("/api/tasks/task-123/resources/res-123")
    assert response.status_code in (401, 403)
