import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app.main import app
from app.auth import get_current_user, DummyUser

client = TestClient(app)

USER_A = DummyUser(id="11111111-1111-1111-1111-111111111111", email="userA@test.com")
USER_B = DummyUser(id="22222222-2222-2222-2222-222222222222", email="userB@test.com")

class MockTable:
    def __init__(self, name, db):
        self.name = name
        self.db = db
        self._filter_user_id = None
        self._filter_id = None
        self._filter_type = None
        self._filter_status = None
        self._filter_ilike_field = None
        self._filter_ilike_val = None
        self._limit_val = None
        self._offset_val = 0

    def select(self, *args, **kwargs):
        return self

    def insert(self, payload):
        self._insert_payload = payload
        return self

    def update(self, payload):
        self._update_payload = payload
        return self

    def delete(self):
        self._is_delete = True
        return self

    def eq(self, field, value):
        if field == "user_id":
            self._filter_user_id = value
        elif field == "id":
            self._filter_id = value
        elif field == "type":
            self._filter_type = value
        elif field == "status":
            self._filter_status = value
        elif field == "source_knowledge_id":
            self._filter_source_k_id = value
        elif field == "target_knowledge_id":
            self._filter_target_k_id = value
        return self

    def ilike(self, field, value):
        self._filter_ilike_field = field
        self._filter_ilike_val = value.lower()
        return self

    def limit(self, val):
        self._limit_val = val
        return self

    def range(self, start, end):
        self._offset_val = start
        self._range_end = end
        return self

    def order(self, *args, **kwargs):
        return self

    def or_(self, *args, **kwargs):
        return self

    def in_(self, field, values):
        return self

    def execute(self):
        rows = self.db.setdefault(self.name, [])
        res = MagicMock()

        if hasattr(self, '_insert_payload'):
            payloads = self._insert_payload if isinstance(self._insert_payload, list) else [self._insert_payload]
            inserted = []
            for p in payloads:
                item = dict(p)
                if "id" not in item:
                    import uuid
                    item["id"] = str(uuid.uuid4())
                rows.append(item)
                inserted.append(item)
            res.data = inserted
            return res

        if getattr(self, '_is_delete', False):
            remaining = []
            deleted = []
            for r in rows:
                match = True
                if self._filter_user_id and r.get("user_id") != self._filter_user_id:
                    match = False
                if self._filter_id and r.get("id") != self._filter_id:
                    match = False
                if match:
                    deleted.append(r)
                else:
                    remaining.append(r)
            self.db[self.name] = remaining
            res.data = deleted
            return res

        if hasattr(self, '_update_payload'):
            updated = []
            for r in rows:
                match = True
                if self._filter_user_id and r.get("user_id") != self._filter_user_id:
                    match = False
                if self._filter_id and r.get("id") != self._filter_id:
                    match = False
                if match:
                    r.update(self._update_payload)
                    updated.append(r)
            res.data = updated
            return res

        # Filter for SELECT
        result = []
        for r in rows:
            if self._filter_user_id and r.get("user_id") != self._filter_user_id:
                continue
            if self._filter_id and r.get("id") != self._filter_id:
                continue
            if self._filter_type and r.get("type") != self._filter_type:
                continue
            if self._filter_status and r.get("status") != self._filter_status:
                continue
            if self._filter_ilike_field and self._filter_ilike_val:
                val = str(r.get(self._filter_ilike_field, '')).lower()
                if self._filter_ilike_val not in val:
                    continue
            result.append(r)

        total_count = len(result)
        if hasattr(self, '_range_end'):
            result = result[self._offset_val:self._range_end + 1]
        elif self._limit_val is not None:
            result = result[self._offset_val:self._offset_val + self._limit_val]

        res.data = result
        res.count = total_count
        return res

@pytest.fixture
def mock_supabase():
    db = {}
    mock_client = MagicMock()
    mock_client.table.side_effect = lambda name: MockTable(name, db)
    with patch("app.supabase.get_supabase", return_value=mock_client), \
         patch("app.services.knowledge_service.get_supabase", return_value=mock_client), \
         patch("app.routes.knowledge.get_supabase", return_value=mock_client):
        yield db

def test_knowledge_crud(mock_supabase):
    app.dependency_overrides[get_current_user] = lambda: USER_A

    # 1. Create Knowledge
    payload = {
        "type": "concept",
        "title": "Prior Art in Software Patents",
        "summary": "Crucial for determining software novelty",
        "content": "Prior art consists of all information made available to the public before a patent filing.",
        "sources": [
            {
                "source_type": "task",
                "source_id": "00000000-0000-0000-0000-000000000001",
                "source_name": "Patent Task"
            }
        ]
    }
    res = client.post("/api/knowledge", json=payload)
    assert res.status_code == 200, res.text
    k_id = res.json()["id"]
    assert res.json()["title"] == "Prior Art in Software Patents"
    assert res.json()["status"] == "active"
    assert res.json()["origin"] == "user"

    # 2. Read Knowledge Detail
    detail_res = client.get(f"/api/knowledge/{k_id}")
    assert detail_res.status_code == 200
    assert detail_res.json()["title"] == "Prior Art in Software Patents"
    assert len(detail_res.json()["sources"]) == 1
    assert detail_res.json()["sources"][0]["source_name"] == "Patent Task"

    # 3. Update Knowledge
    update_res = client.patch(f"/api/knowledge/{k_id}", json={
        "title": "Prior Art & Patent Search Strategy",
        "summary": "Updated summary"
    })
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Prior Art & Patent Search Strategy"
    assert update_res.json()["summary"] == "Updated summary"

    # 4. Archive & Restore
    arch_res = client.post(f"/api/knowledge/{k_id}/archive")
    assert arch_res.status_code == 200
    assert arch_res.json()["status"] == "archived"

    rest_res = client.post(f"/api/knowledge/{k_id}/restore")
    assert rest_res.status_code == 200
    assert rest_res.json()["status"] == "active"

    # 5. Delete Knowledge
    del_res = client.delete(f"/api/knowledge/{k_id}")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "success"

    # Verify deleted
    verify_res = client.get(f"/api/knowledge/{k_id}")
    assert verify_res.status_code == 404
    app.dependency_overrides.clear()

def test_duplicate_detection(mock_supabase):
    app.dependency_overrides[get_current_user] = lambda: USER_A

    client.post("/api/knowledge", json={
        "type": "insight",
        "title": "Browser Extension Content Scripts",
        "content": "Run in the context of webpages."
    })

    # Exact Match
    dup1 = client.post("/api/knowledge/check-duplicate", json={"title": "Browser Extension Content Scripts"})
    assert dup1.status_code == 200
    assert dup1.json()["has_duplicate"] is True
    assert dup1.json()["duplicate_type"] == "exact"

    # Normalized Match (whitespace/casing/punctuation)
    dup2 = client.post("/api/knowledge/check-duplicate", json={"title": "browser extension content scripts!"})
    assert dup2.status_code == 200
    assert dup2.json()["has_duplicate"] is True

    # No Match
    no_dup = client.post("/api/knowledge/check-duplicate", json={"title": "Completely Unrelated Subject"})
    assert no_dup.status_code == 200
    assert no_dup.json()["has_duplicate"] is False
    app.dependency_overrides.clear()

def test_cross_user_isolation(mock_supabase):
    # User A creates knowledge
    app.dependency_overrides[get_current_user] = lambda: USER_A
    res_a = client.post("/api/knowledge", json={
        "type": "note",
        "title": "User A Secret Concept",
        "content": "Confidential research"
    })
    k_id_a = res_a.json()["id"]

    # Switch to User B
    app.dependency_overrides[get_current_user] = lambda: USER_B

    # User B cannot read User A's knowledge
    read_b = client.get(f"/api/knowledge/{k_id_a}")
    assert read_b.status_code == 404

    # User B cannot update User A's knowledge
    update_b = client.patch(f"/api/knowledge/{k_id_a}", json={"title": "Hacked Title"})
    assert update_b.status_code == 404

    # User B cannot delete User A's knowledge
    delete_b = client.delete(f"/api/knowledge/{k_id_a}")
    assert delete_b.status_code == 404

    # User B creates their own knowledge item
    res_b = client.post("/api/knowledge", json={
        "type": "note",
        "title": "User B Concept",
        "content": "User B notes"
    })
    k_id_b = res_b.json()["id"]

    # User B cannot create an edge linking to User A's knowledge
    edge_res = client.post(f"/api/knowledge/{k_id_b}/relationships", json={
        "target_knowledge_id": k_id_a,
        "relationship_type": "related_to"
    })
    assert edge_res.status_code == 403
    app.dependency_overrides.clear()

def test_relationship_rules(mock_supabase):
    app.dependency_overrides[get_current_user] = lambda: USER_A

    res1 = client.post("/api/knowledge", json={"type": "concept", "title": "Node 1", "content": "..."})
    res2 = client.post("/api/knowledge", json={"type": "concept", "title": "Node 2", "content": "..."})
    id1 = res1.json()["id"]
    id2 = res2.json()["id"]

    # Cannot link to self
    self_loop = client.post(f"/api/knowledge/{id1}/relationships", json={
        "target_knowledge_id": id1,
        "relationship_type": "supports"
    })
    assert self_loop.status_code == 400

    # Valid relationship
    rel = client.post(f"/api/knowledge/{id1}/relationships", json={
        "target_knowledge_id": id2,
        "relationship_type": "supports"
    })
    assert rel.status_code == 200
    assert rel.json()["relationship_type"] == "supports"
    app.dependency_overrides.clear()

def test_ai_suggestions_resilience(mock_supabase):
    app.dependency_overrides[get_current_user] = lambda: USER_A
    task_id = "00000000-0000-0000-0000-000000000099"

    # Seed mock task belonging to User A
    mock_supabase["tasks"] = [{
        "id": task_id,
        "user_id": USER_A.id,
        "name": "Distributed Consensus Research"
    }]
    mock_supabase["task_resources"] = []
    mock_supabase["task_activity"] = []

    res = client.post(f"/api/tasks/{task_id}/knowledge/suggestions")
    assert res.status_code == 200
    data = res.json()
    assert "suggestions" in data
    assert len(data["suggestions"]) > 0
    sug = data["suggestions"][0]
    assert sug["type"] in ["concept", "topic", "question", "insight", "note", "resource"]
    assert "title" in sug
    assert "summary" in sug
    app.dependency_overrides.clear()

def test_performance_bulk_list(mock_supabase):
    app.dependency_overrides[get_current_user] = lambda: USER_A
    import time
    t0 = time.time()
    for i in range(100):
        client.post("/api/knowledge", json={
            "type": "concept",
            "title": f"Bulk Concept {i}",
            "content": f"Content for concept {i}"
        })
    insert_duration = time.time() - t0

    t1 = time.time()
    list_res = client.get("/api/knowledge?limit=50")
    list_duration = time.time() - t1

    assert list_res.status_code == 200
    assert len(list_res.json()["items"]) == 50
    assert list_res.json()["total"] >= 100
    assert list_duration < 2.0  # Fast latency for 100 items
    app.dependency_overrides.clear()

def test_bounded_graph_traversal(mock_supabase):
    app.dependency_overrides[get_current_user] = lambda: USER_A
    k1 = client.post("/api/knowledge", json={"type": "concept", "title": "Graph Root", "content": "..."}).json()["id"]
    k2 = client.post("/api/knowledge", json={"type": "concept", "title": "Graph Child", "content": "..."}).json()["id"]

    client.post(f"/api/knowledge/{k1}/relationships", json={"target_knowledge_id": k2, "relationship_type": "explains"})

    rel_graph = client.get(f"/api/knowledge/{k1}/related?depth=2")
    assert rel_graph.status_code == 200
    data = rel_graph.json()
    assert data["root_id"] == k1
    assert data["depth"] <= 3
    assert len(data["nodes"]) >= 2
    app.dependency_overrides.clear()
