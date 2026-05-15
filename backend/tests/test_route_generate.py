"""POST /generate end-to-end with FastAPI TestClient + mocked LLM."""

from __future__ import annotations

import chromadb
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.diagram import NodeType
from app.schemas.generate import (
    GeneratedDiagramContent,
    GeneratedEdge,
    GeneratedNode,
)
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
from tests._fake_embedder import FakeEmbedder
from tests._fake_llm import FakeLLMProvider


def _good_content() -> GeneratedDiagramContent:
    return GeneratedDiagramContent(
        name="Delivery app",
        description="From the prompt",
        nodes=[
            GeneratedNode(id="front", type=NodeType.FRONTEND, label="App"),
            GeneratedNode(id="api", type=NodeType.BACKEND, label="API"),
            GeneratedNode(id="db", type=NodeType.DATABASE, label="DB"),
        ],
        edges=[
            GeneratedEdge(id="e1", source="front", target="api"),
            GeneratedEdge(id="e2", source="api", target="db"),
        ],
    )


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Per-test client with in-memory Chroma + fake embedder.

    The LLM provider override is set per-test by patching the generator's
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


def test_happy_path_returns_200_and_diagram(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake_llm = FakeLLMProvider(structured_response=_good_content())
    monkeypatch.setattr("app.services.generation.generator.get_llm", lambda: fake_llm)

    response = client.post("/generate", json={"prompt": "delivery app"})
    assert response.status_code == 200
    body = response.json()
    assert body["metadata"]["name"] == "Delivery app"
    assert len(body["nodes"]) == 3
    assert len(body["edges"]) == 2
    # Every node has a position
    for node in body["nodes"]:
        assert "x" in node["position"]
        assert "y" in node["position"]


def test_empty_prompt_returns_422(client: TestClient) -> None:
    response = client.post("/generate", json={"prompt": ""})
    assert response.status_code == 422


def test_missing_prompt_returns_422(client: TestClient) -> None:
    response = client.post("/generate", json={})
    assert response.status_code == 422


def test_oversized_prompt_returns_413(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    from app.core.config import get_settings

    settings = get_settings()
    oversize = "x" * (settings.max_input_chars + 1)
    response = client.post("/generate", json={"prompt": oversize})
    assert response.status_code == 413
    body = response.json()
    assert body["code"] == "prompt_too_long"


def test_llm_config_error_returns_503(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    fake_llm = FakeLLMProvider(structured_error=LLMConfigError("OPENAI_API_KEY is required"))
    monkeypatch.setattr("app.services.generation.generator.get_llm", lambda: fake_llm)

    response = client.post("/generate", json={"prompt": "anything"})
    assert response.status_code == 503
    assert response.json()["code"] == "llm_config_error"


def test_llm_timeout_returns_504(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    fake_llm = FakeLLMProvider(structured_error=LLMTimeoutError("timed out"))
    monkeypatch.setattr("app.services.generation.generator.get_llm", lambda: fake_llm)

    response = client.post("/generate", json={"prompt": "anything"})
    assert response.status_code == 504
    assert response.json()["code"] == "llm_timeout"


def test_llm_rate_limited_returns_429(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    fake_llm = FakeLLMProvider(structured_error=LLMRateLimited("slow down"))
    monkeypatch.setattr("app.services.generation.generator.get_llm", lambda: fake_llm)

    response = client.post("/generate", json={"prompt": "anything"})
    assert response.status_code == 429
    assert response.json()["code"] == "llm_rate_limited"


def test_llm_invalid_response_returns_502(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake_llm = FakeLLMProvider(structured_error=LLMInvalidResponse("garbage"))
    monkeypatch.setattr("app.services.generation.generator.get_llm", lambda: fake_llm)

    response = client.post("/generate", json={"prompt": "anything"})
    assert response.status_code == 502
    assert response.json()["code"] == "llm_invalid_response"


def test_llm_input_too_large_returns_413(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake_llm = FakeLLMProvider(structured_error=LLMInputTooLarge("too big"))
    monkeypatch.setattr("app.services.generation.generator.get_llm", lambda: fake_llm)

    response = client.post("/generate", json={"prompt": "anything"})
    assert response.status_code == 413
    assert response.json()["code"] == "llm_input_too_large"


def test_error_body_is_flat_not_nested(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """Regression test: detail and code must be top-level keys.

    Earlier implementation passed a dict to HTTPException(detail=...) which
    FastAPI wrapped under an extra "detail" key, producing
    `{"detail": {"detail": "...", "code": "..."}}`. This test pins the flat
    shape that matches the documented ErrorBody response model.
    """
    fake_llm = FakeLLMProvider(structured_error=LLMConfigError("missing key"))
    monkeypatch.setattr("app.services.generation.generator.get_llm", lambda: fake_llm)

    response = client.post("/generate", json={"prompt": "anything"})
    body = response.json()

    # Top-level keys exist and are strings (not dicts).
    assert isinstance(body.get("detail"), str), (
        f"`detail` must be a top-level string, got {type(body.get('detail')).__name__}"
    )
    assert isinstance(body.get("code"), str), (
        f"`code` must be a top-level string, got {type(body.get('code')).__name__}"
    )
    # No accidental nesting.
    assert "detail" not in body.get("detail") if isinstance(body.get("detail"), dict) else True
    assert body["code"] == "llm_config_error"
