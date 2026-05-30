"""POST /analyze end-to-end with FastAPI TestClient + mocked LLM."""

from __future__ import annotations

import chromadb
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.diagram import NodeType
from app.services.llm import (
    LLMConfigError,
    LLMInputTooLarge,
    LLMInvalidResponse,
    LLMRateLimited,
    LLMTimeoutError,
)
from app.services.modes import reset_for_tests as reset_modes
from app.services.patterns import reset_for_tests as reset_patterns
from app.services.retrieval import store
from tests._diagram_factories import make_diagram, make_edge, make_node
from tests._fake_embedder import FakeEmbedder
from tests._fake_llm import FakeLLMProvider


def _violating_payload() -> dict:
    diagram = make_diagram(
        nodes=[
            make_node("front", NodeType.FRONTEND),
            make_node("db", NodeType.DATABASE),
        ],
        edges=[make_edge("e1", "front", "db")],
    )
    return {"diagram": diagram.model_dump(by_alias=True, mode="json")}


def _clean_payload() -> dict:
    diagram = make_diagram(
        nodes=[
            make_node("front", NodeType.FRONTEND),
            make_node("api", NodeType.BACKEND),
        ],
        edges=[make_edge("e1", "front", "api")],
    )
    return {"diagram": diagram.model_dump(by_alias=True, mode="json")}


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Per-test client with in-memory Chroma + fake embedder.

    The LLM provider override is set per-test by patching the analyzer's
    `get_llm` reference.
    """
    store.set_client_for_tests(chromadb.EphemeralClient())
    store.delete_collection()
    fake_emb = FakeEmbedder()
    monkeypatch.setattr("app.services.retrieval.builder.get_embedder", lambda: fake_emb)
    monkeypatch.setattr("app.services.retrieval.retriever.get_embedder", lambda: fake_emb)
    reset_patterns()
    reset_modes()
    yield TestClient(app)
    store.delete_collection()
    store.set_client_for_tests(None)
    reset_patterns()
    reset_modes()


def test_happy_path_returns_findings_and_feedback(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake_llm = FakeLLMProvider(text_response="Frontend hits the DB directly — add an API.")
    monkeypatch.setattr("app.services.analysis.analyzer.get_llm", lambda: fake_llm)

    response = client.post("/analyze", json=_violating_payload())
    assert response.status_code == 200
    body = response.json()
    assert body["feedback"] == "Frontend hits the DB directly — add an API."
    rule_ids = {f["rule_id"] for f in body["findings"]}
    assert "no-direct-frontend-to-database" in rule_ids


def test_clean_diagram_empty_findings_nonempty_feedback(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake_llm = FakeLLMProvider(text_response="Clean little stack.")
    monkeypatch.setattr("app.services.analysis.analyzer.get_llm", lambda: fake_llm)

    response = client.post("/analyze", json=_clean_payload())
    assert response.status_code == 200
    body = response.json()
    assert body["findings"] == []
    assert body["feedback"] == "Clean little stack."


def test_read_only_no_persistence_and_no_backend_id(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake_llm = FakeLLMProvider(text_response="ok")
    monkeypatch.setattr("app.services.analysis.analyzer.get_llm", lambda: fake_llm)

    def _boom(*args: object, **kwargs: object) -> None:
        raise AssertionError("analyze must not write to storage")

    monkeypatch.setattr("app.services.storage.repository.save_diagram", _boom)

    response = client.post("/analyze", json=_clean_payload())
    assert response.status_code == 200
    # Response carries only findings + feedback — no backend-assigned id.
    assert set(response.json().keys()) == {"findings", "feedback"}


def test_malformed_body_returns_422(client: TestClient) -> None:
    response = client.post("/analyze", json={"diagram": {"not": "a diagram"}})
    assert response.status_code == 422


def test_missing_diagram_returns_422(client: TestClient) -> None:
    response = client.post("/analyze", json={})
    assert response.status_code == 422


def test_unknown_mode_returns_422(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    fake_llm = FakeLLMProvider(text_response="never reached")
    monkeypatch.setattr("app.services.analysis.analyzer.get_llm", lambda: fake_llm)

    payload = _clean_payload()
    payload["modeId"] = "does-not-exist"
    response = client.post("/analyze", json=payload)
    assert response.status_code == 422
    assert response.json()["code"] == "unknown_mode"


def test_oversized_diagram_returns_413(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    from app.core.config import get_settings

    # A guard that fires before any LLM call: patch generate to blow up so we
    # prove the 413 happens first.
    fake_llm = FakeLLMProvider(text_response="should not be called")
    monkeypatch.setattr("app.services.analysis.analyzer.get_llm", lambda: fake_llm)

    settings = get_settings()
    payload = _clean_payload()
    # Inflate the diagram description past the cap.
    payload["diagram"]["metadata"]["description"] = "x" * (settings.max_input_chars + 1)

    response = client.post("/analyze", json=payload)
    assert response.status_code == 413
    assert response.json()["code"] == "diagram_too_large"


@pytest.mark.parametrize(
    ("error", "expected_status", "expected_code"),
    [
        (LLMConfigError("missing key"), 503, "llm_config_error"),
        (LLMTimeoutError("timed out"), 504, "llm_timeout"),
        (LLMRateLimited("slow down"), 429, "llm_rate_limited"),
        (LLMInvalidResponse("garbage"), 502, "llm_invalid_response"),
        (LLMInputTooLarge("too big"), 413, "llm_input_too_large"),
    ],
)
def test_llm_errors_map_to_status(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    error: Exception,
    expected_status: int,
    expected_code: str,
) -> None:
    fake_llm = FakeLLMProvider(structured_error=error)
    monkeypatch.setattr("app.services.analysis.analyzer.get_llm", lambda: fake_llm)

    response = client.post("/analyze", json=_violating_payload())
    assert response.status_code == expected_status
    assert response.json()["code"] == expected_code


def test_error_body_is_flat(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    fake_llm = FakeLLMProvider(structured_error=LLMConfigError("missing key"))
    monkeypatch.setattr("app.services.analysis.analyzer.get_llm", lambda: fake_llm)

    body = client.post("/analyze", json=_violating_payload()).json()
    assert isinstance(body.get("detail"), str)
    assert isinstance(body.get("code"), str)
    assert body["code"] == "llm_config_error"
