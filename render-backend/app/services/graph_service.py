import re
from difflib import SequenceMatcher
from typing import List, Dict, Any, Optional
from app.supabase import get_supabase


def normalize_label(label: str) -> str:
    """
    Standardize entity/concept labels:
    - Strips leading/trailing punctuation and markdown markers
    - Replaces internal underscores/hyphens with single spaces
    - Collapses consecutive whitespace
    """
    if not label:
        return ""
    cleaned = re.sub(r"^[`'\"\*\#\-\s]+|[`'\"\*\#\-\s]+$", "", label.strip())
    cleaned = re.sub(r"[\-_\s]+", " ", cleaned)
    return cleaned.strip()


def are_labels_semantically_equivalent(label_a: str, label_b: str, threshold: float = 0.88) -> bool:
    """
    Check if two node labels represent the identical underlying entity or concept.
    Accounts for singular/plural, hyphens vs spaces, and high token overlap.
    """
    norm_a = normalize_label(label_a).lower()
    norm_b = normalize_label(label_b).lower()

    if norm_a == norm_b:
        return True

    # Check pluralization (e.g. "resource" vs "resources", "activity" vs "activities")
    if norm_a + "s" == norm_b or norm_b + "s" == norm_a:
        return True
    if (norm_a.endswith("y") and norm_a[:-1] + "ies" == norm_b) or (
        norm_b.endswith("y") and norm_b[:-1] + "ies" == norm_a
    ):
        return True

    # Sequence similarity for minor typos or capitalization differences
    if SequenceMatcher(None, norm_a, norm_b).ratio() >= threshold:
        return True

    return False


def find_canonical_node_key(label: str, existing_canonical_keys: List[str]) -> Optional[str]:
    """Find matching canonical key among known nodes if equivalent."""
    norm = normalize_label(label).lower()
    for existing_key in existing_canonical_keys:
        if are_labels_semantically_equivalent(norm, existing_key):
            return existing_key
    return None


def get_task_graph(task_id: str, user_id: str) -> Dict[str, Any]:
    supabase = get_supabase()

    # Verify task ownership
    task = supabase.table("tasks").select("id").eq("id", task_id).eq("user_id", user_id).execute()
    if not task.data:
        raise ValueError("Task not found or not owned by user")

    nodes = supabase.table("task_nodes").select("*").eq("task_id", task_id).execute()
    edges = supabase.table("task_edges").select("*").eq("task_id", task_id).execute()

    return {
        "nodes": nodes.data or [],
        "edges": edges.data or []
    }


def delete_node(task_id: str, node_id: str, user_id: str):
    supabase = get_supabase()
    task = supabase.table("tasks").select("id").eq("id", task_id).eq("user_id", user_id).execute()
    if not task.data:
        raise ValueError("Task not found or not owned by user")
    supabase.table("task_nodes").delete().eq("id", node_id).eq("task_id", task_id).eq("user_id", user_id).execute()


def delete_edge(task_id: str, edge_id: str, user_id: str):
    supabase = get_supabase()
    task = supabase.table("tasks").select("id").eq("id", task_id).eq("user_id", user_id).execute()
    if not task.data:
        raise ValueError("Task not found or not owned by user")
    supabase.table("task_edges").delete().eq("id", edge_id).eq("task_id", task_id).eq("user_id", user_id).execute()


def reject_edge(task_id: str, edge_id: str, user_id: str):
    supabase = get_supabase()
    task = supabase.table("tasks").select("id").eq("id", task_id).eq("user_id", user_id).execute()
    if not task.data:
        raise ValueError("Task not found or not owned by user")
    supabase.table("task_edges").update({"is_rejected": True}).eq("id", edge_id).eq("task_id", task_id).eq("user_id", user_id).execute()


def save_ai_graph(task_id: str, user_id: str, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]):
    """
    Overhauled graph persistence with:
    1. Semantic entity deduplication & label canonicalization
    2. Confidence weighting updates
    3. Self-referential & duplicate edge filtering
    4. Rejection preservation
    """
    supabase = get_supabase()

    # Get existing nodes and edges for this task
    existing_nodes = supabase.table("task_nodes").select("*").eq("task_id", task_id).execute().data or []
    existing_edges = supabase.table("task_edges").select("*").eq("task_id", task_id).execute().data or []

    # Map normalized canonical key -> db node record
    node_map: Dict[str, Dict[str, Any]] = {}
    for n in existing_nodes:
        norm_key = normalize_label(n["label"]).lower()
        node_map[norm_key] = n

    saved_nodes: Dict[str, str] = {}  # alias/label -> node_id

    # 1. Deduplicate & Save Nodes
    for node in nodes:
        raw_label = (node.get("label") or "").strip()
        if not raw_label:
            continue

        clean_label = normalize_label(raw_label)
        norm_key = clean_label.lower()

        # Find existing canonical match
        canonical_key = find_canonical_node_key(norm_key, list(node_map.keys()))

        if canonical_key and canonical_key in node_map:
            db_node = node_map[canonical_key]
            node_id = db_node["id"]
            saved_nodes[raw_label] = node_id
            saved_nodes[raw_label.lower()] = node_id
            saved_nodes[clean_label] = node_id
            saved_nodes[norm_key] = node_id

            # Update description / confidence if newly extracted info is richer or higher confidence
            new_conf = float(node.get("confidence", 0.5))
            current_conf = float(db_node.get("confidence") or 0.5)
            update_payload = {}
            if new_conf > current_conf:
                update_payload["confidence"] = new_conf
            if not db_node.get("description") and node.get("description"):
                update_payload["description"] = node.get("description")

            if update_payload:
                supabase.table("task_nodes").update(update_payload).eq("id", node_id).execute()
        else:
            # Insert new canonical node
            new_node = {
                "task_id": task_id,
                "user_id": user_id,
                "node_type": node.get("node_type", "concept"),
                "label": clean_label,
                "description": node.get("description"),
                "is_ai_generated": True,
                "confidence": float(node.get("confidence", 0.5))
            }
            res = supabase.table("task_nodes").insert(new_node).execute()
            if res.data:
                created_record = res.data[0]
                node_id = created_record["id"]
                saved_nodes[raw_label] = node_id
                saved_nodes[raw_label.lower()] = node_id
                saved_nodes[clean_label] = node_id
                saved_nodes[norm_key] = node_id
                node_map[norm_key] = created_record

    # 2. Process & Deduplicate Edges
    edge_map = {(e["source_node_id"], e["target_node_id"], e["relationship_type"]): e for e in existing_edges}

    for edge in edges:
        src_raw = (edge.get("source_label") or "").strip()
        tgt_raw = (edge.get("target_label") or "").strip()
        rel_type = (edge.get("relationship_type") or "related_to").strip()

        src_id = (
            saved_nodes.get(src_raw)
            or saved_nodes.get(src_raw.lower())
            or saved_nodes.get(normalize_label(src_raw).lower())
        )
        tgt_id = (
            saved_nodes.get(tgt_raw)
            or saved_nodes.get(tgt_raw.lower())
            or saved_nodes.get(normalize_label(tgt_raw).lower())
        )

        # Fallback to finding canonical node key
        if not src_id:
            canon = find_canonical_node_key(src_raw, list(node_map.keys()))
            if canon:
                src_id = node_map[canon]["id"]

        if not tgt_id:
            canon = find_canonical_node_key(tgt_raw, list(node_map.keys()))
            if canon:
                tgt_id = node_map[canon]["id"]

        if not src_id or not tgt_id or src_id == tgt_id:
            continue

        key = (src_id, tgt_id, rel_type)

        if key in edge_map:
            existing_edge = edge_map[key]
            if existing_edge.get("is_rejected"):
                continue  # Never resurrect rejected edges

            if existing_edge.get("is_ai_generated"):
                new_conf = float(edge.get("confidence", existing_edge.get("confidence", 0.5)))
                supabase.table("task_edges").update({
                    "confidence": new_conf,
                    "evidence": edge.get("evidence", existing_edge.get("evidence", []))
                }).eq("id", existing_edge["id"]).execute()
        else:
            new_edge = {
                "task_id": task_id,
                "user_id": user_id,
                "source_node_id": src_id,
                "target_node_id": tgt_id,
                "relationship_type": rel_type,
                "is_ai_generated": True,
                "confidence": float(edge.get("confidence", 0.5)),
                "evidence": edge.get("evidence", [])
            }
            res = supabase.table("task_edges").insert(new_edge).execute()
            if res.data:
                edge_map[key] = res.data[0]
