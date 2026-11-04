import pytest
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Ensure mock Supabase env vars are set before importing the app
os.environ.setdefault("SUPABASE_URL", "https://mock.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "mock-service-key")
os.environ.setdefault("ENVIRONMENT", "test")

from app.main import app


@pytest.fixture
def client():
    with patch("app.main.run_cron_monitor", return_value=None):
        with TestClient(app) as test_client:
            yield test_client


def test_health_check_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_custom_docs_endpoint(client):
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")


def test_protected_route_unauthenticated(client):
    # Tasks endpoint requires authentication
    response = client.get("/api/tasks")
    assert response.status_code in (401, 403)


def test_dev_mock_jwt_disabled_in_production(client):
    with patch.dict(os.environ, {"DEBUG": "false", "ENVIRONMENT": "production", "DEV_MOCK_JWT": "dev_token"}):
        response = client.get("/api/tasks", headers={"Authorization": "Bearer dev_token"})
        assert response.status_code in (401, 403)


def test_dev_mock_jwt_enabled_in_development(client):
    with patch.dict(os.environ, {"DEBUG": "true", "ENVIRONMENT": "development", "DEV_MOCK_JWT": "dev_token"}):
        with patch("app.routes.tasks.get_supabase") as mock_supabase:
            mock_table = MagicMock()
            mock_table.select.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
            mock_supabase.return_value.table.return_value = mock_table

            response = client.get("/api/tasks", headers={"Authorization": "Bearer dev_token"})
            # Request should pass authentication and return empty task list
            assert response.status_code == 200
            assert response.json() == []
