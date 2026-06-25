"""auto_layout assigns deterministic, sensible positions."""

from __future__ import annotations

from app.schemas.diagram import NodeType
from app.schemas.generate import GeneratedNode
from app.services.generation.layout import auto_layout


def _gen(node_id: str, node_type: NodeType) -> GeneratedNode:
    return GeneratedNode(id=node_id, type=node_type, label=node_id)


def test_frontend_leftmost() -> None:
    [front] = auto_layout([_gen("a", NodeType.FRONTEND)])
    assert front.position.x == 80


def test_database_rightmost() -> None:
    [db] = auto_layout([_gen("d", NodeType.DATABASE)])
    [front] = auto_layout([_gen("a", NodeType.FRONTEND)])
    [api] = auto_layout([_gen("b", NodeType.BACKEND)])
    # Database sits to the right of both frontend and backend.
    assert db.position.x > api.position.x > front.position.x


def test_backend_in_middle() -> None:
    [api] = auto_layout([_gen("a", NodeType.BACKEND)])
    assert 80 < api.position.x < 800


def test_external_service_top_row() -> None:
    [ext] = auto_layout([_gen("e", NodeType.EXTERNAL_SERVICE)])
    # external services live above the main row
    assert ext.position.y < 240


def test_cache_below_backend() -> None:
    cache_nodes = auto_layout([_gen("c", NodeType.CACHE)])
    backend_nodes = auto_layout([_gen("b", NodeType.BACKEND)])
    assert cache_nodes[0].position.y > backend_nodes[0].position.y


def test_same_type_stacks_vertically() -> None:
    positioned = auto_layout(
        [
            _gen("api1", NodeType.BACKEND),
            _gen("api2", NodeType.BACKEND),
            _gen("api3", NodeType.BACKEND),
        ]
    )
    xs = {p.position.x for p in positioned}
    ys = [p.position.y for p in positioned]
    assert len(xs) == 1  # same column
    assert len(set(ys)) == 3  # distinct ys
    # Gaps are consistent
    gaps = [ys[i + 1] - ys[i] for i in range(len(ys) - 1)]
    assert len(set(gaps)) == 1


def test_deterministic_across_calls() -> None:
    nodes = [
        _gen("a", NodeType.FRONTEND),
        _gen("b", NodeType.BACKEND),
        _gen("c", NodeType.DATABASE),
    ]
    first = auto_layout(nodes)
    second = auto_layout(nodes)
    for f, s in zip(first, second, strict=True):
        assert f.position == s.position


def test_preserves_label_and_id() -> None:
    nodes = [_gen("hello", NodeType.FRONTEND)]
    positioned = auto_layout(nodes)
    assert positioned[0].id == "hello"
    assert positioned[0].label == "hello"
