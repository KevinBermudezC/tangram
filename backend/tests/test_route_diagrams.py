"""Route tests for diagram persistence (POST/GET/DELETE /diagrams)."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app


@pytest.fixture(autouse=True)
def _data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    get_settings.cache_clear()
    return tmp_path


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def _diagram_body(diagram_id: str = "", *, name: str = "Test") -> dict:
    now = datetime.now(UTC).isoformat()
    return {
        "version": "0.1.0",
        "id": diagram_id,
        "metadata": {
            "name": name,
            "description": None,
            "createdAt": now,
            "updatedAt": now,
        },
        "nodes": [{"id": "n1", "type": "backend", "label": "API", "position": {"x": 0, "y": 0}}],
        "edges": [],
    }


def test_post_creates_and_assigns_id(client: TestClient) -> None:
    response = client.post("/diagrams", json=_diagram_body(""))
    assert response.status_code == 201
    body = response.json()
    assert body["id"]  # server assigned a ULID
    assert body["metadata"]["name"] == "Test"


def test_post_then_get_by_id(client: TestClient) -> None:
    created = client.post("/diagrams", json=_diagram_body("", name="Fetch me")).json()
    response = client.get(f"/diagrams/{created['id']}")
    assert response.status_code == 200
    assert response.json()["metadata"]["name"] == "Fetch me"


def test_list_returns_summaries(client: TestClient) -> None:
    client.post("/diagrams", json=_diagram_body(""))
    client.post("/diagrams", json=_diagram_body(""))
    response = client.get("/diagrams")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 2
    # Summary shape: counts + thumb present, full arrays absent.
    assert set(items[0]) == {
        "id",
        "name",
        "description",
        "createdAt",
        "updatedAt",
        "nodeCount",
        "edgeCount",
        "thumb",
    }
    assert items[0]["nodeCount"] == 1
    assert items[0]["edgeCount"] == 0
    # Thumb is a geometry-only projection (no labels/properties).
    assert items[0]["thumb"]["nodes"][0]["type"] == "backend"
    assert "label" not in items[0]["thumb"]["nodes"][0]


def test_get_missing_returns_typed_404(client: TestClient) -> None:
    response = client.get("/diagrams/01HZZZZZZZZZZZZZZZZZZZZZZZ")
    assert response.status_code == 404
    body = response.json()
    assert isinstance(body["detail"], str)
    assert body["code"] == "diagram_not_found"


def test_delete_then_get_returns_404(client: TestClient) -> None:
    created = client.post("/diagrams", json=_diagram_body("")).json()
    deleted = client.delete(f"/diagrams/{created['id']}")
    assert deleted.status_code == 204
    assert client.get(f"/diagrams/{created['id']}").status_code == 404


def test_delete_missing_returns_typed_404(client: TestClient) -> None:
    response = client.delete("/diagrams/01HZZZZZZZZZZZZZZZZZZZZZZZ")
    assert response.status_code == 404
    assert response.json()["code"] == "diagram_not_found"


def test_malformed_id_rejected_before_filesystem(client: TestClient) -> None:
    # A non-ULID id is rejected at the routing layer (422), never reaching storage.
    response = client.get("/diagrams/not-a-ulid")
    assert response.status_code == 422
