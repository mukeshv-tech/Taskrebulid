from app.services.graph_service import (
    normalize_label,
    are_labels_semantically_equivalent,
    find_canonical_node_key
)


def test_normalize_label():
    assert normalize_label("  `FastAPI`  ") == "FastAPI"
    assert normalize_label("**PostgreSQL**") == "PostgreSQL"
    assert normalize_label("vector_search") == "vector search"
    assert normalize_label("vector-search") == "vector search"
    assert normalize_label("   hybrid   search  ") == "hybrid search"


def test_are_labels_semantically_equivalent():
    # Exact case-insensitive
    assert are_labels_semantically_equivalent("FastAPI", "fastapi")
    # Pluralization
    assert are_labels_semantically_equivalent("resource", "resources")
    assert are_labels_semantically_equivalent("activity", "activities")
    # Hyphen vs space
    assert are_labels_semantically_equivalent("vector-search", "vector search")
    # Not equivalent
    assert not are_labels_semantically_equivalent("Python", "Rust")
    assert not are_labels_semantically_equivalent("PostgreSQL", "SQLite")


def test_find_canonical_node_key():
    existing_keys = ["fastapi", "postgresql", "hybrid search", "resources"]
    assert find_canonical_node_key("FastAPI", existing_keys) == "fastapi"
    assert find_canonical_node_key("resource", existing_keys) == "resources"
    assert find_canonical_node_key("hybrid-search", existing_keys) == "hybrid search"
    assert find_canonical_node_key("Unknown Concept", existing_keys) is None
