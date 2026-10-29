import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from fastapi import HTTPException
from app.supabase import get_supabase
from app.schemas.knowledge import (
    KnowledgeCreate,
    KnowledgeUpdate,
    KnowledgeType,
    KnowledgeStatus,
    KnowledgeOrigin,
    RelationshipType,
    SourceType,
    KnowledgeSourceInput
)
from app.services.search_indexer import search_indexer

MAX_KNOWLEDGE_DEPTH = 3
MAX_KNOWLEDGE_NODES = 50
MAX_KNOWLEDGE_EDGES = 100
MAX_CONTEXT_ITEMS = 10

class KnowledgeService:
    def __init__(self):
        pass

    def _normalize_title(self, title: str) -> str:
        """Removes punctuation and normalizes whitespace for duplicate detection."""
        return re.sub(r'[\W_]+', ' ', title.lower()).strip()

    def check_duplicate(self, user_id: str, title: str) -> Dict[str, Any]:
        """Detects likely duplicates using exact and normalized title matching."""
        supabase = get_supabase()
        clean_title = title.strip()
        norm_title = self._normalize_title(clean_title)

        # 1. Exact match (case-insensitive)
        exact_res = supabase.table("knowledge_items")\
            .select("id, title, type, status, summary")\
            .eq("user_id", user_id)\
            .ilike("title", clean_title)\
            .execute()

        if exact_res.data and len(exact_res.data) > 0:
            return {
                "has_duplicate": True,
                "duplicate_type": "exact",
                "existing_items": exact_res.data
            }

        # 2. Normalized title match
        all_items = supabase.table("knowledge_items")\
            .select("id, title, type, status, summary")\
            .eq("user_id", user_id)\
            .limit(200)\
            .execute().data or []

        matched = []
        for item in all_items:
            if self._normalize_title(item.get("title", "")) == norm_title:
                matched.append(item)

        if matched:
            return {
                "has_duplicate": True,
                "duplicate_type": "normalized",
                "existing_items": matched
            }

        return {
            "has_duplicate": False,
            "duplicate_type": None,
            "existing_items": []
        }

    def create_knowledge(self, user_id: str, data: KnowledgeCreate) -> Dict[str, Any]:
        """Creates a personal knowledge item with validated ownership and sources."""
        supabase = get_supabase()

        insert_payload = {
            "user_id": user_id,
            "type": data.type.value,
            "title": data.title.strip(),
            "content": data.content,
            "summary": data.summary or (data.content[:150] + "..." if len(data.content) > 150 else data.content),
            "status": KnowledgeStatus.ACTIVE.value,
            "origin": data.origin.value,
            "confidence": data.confidence if data.confidence is not None else 1.0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

        res = supabase.table("knowledge_items").insert(insert_payload).execute()
        if not res.data:
            raise HTTPException(status_code=500, detail="Failed to create knowledge item")

        created_item = res.data[0]
        knowledge_id = created_item["id"]

        # Insert sources if provided
        if data.sources:
            sources_payload = []
            for src in data.sources:
                sources_payload.append({
                    "user_id": user_id,
                    "knowledge_id": knowledge_id,
                    "source_type": src.source_type.value,
                    "source_id": src.source_id,
                    "source_name": src.source_name,
                    "metadata": src.metadata or {},
                    "created_at": datetime.now(timezone.utc).isoformat()
                })
            supabase.table("knowledge_sources").insert(sources_payload).execute()

        # Connect related knowledge if IDs provided
        if data.related_knowledge_ids:
            edges_payload = []
            for target_id in data.related_knowledge_ids:
                if target_id == knowledge_id:
                    continue
                # Verify target belongs to same user
                target_check = supabase.table("knowledge_items")\
                    .select("id")\
                    .eq("id", target_id)\
                    .eq("user_id", user_id)\
                    .execute()
                if target_check.data:
                    edges_payload.append({
                        "user_id": user_id,
                        "source_knowledge_id": knowledge_id,
                        "target_knowledge_id": target_id,
                        "relationship_type": RelationshipType.RELATED_TO.value,
                        "created_at": datetime.now(timezone.utc).isoformat()
                    })
            if edges_payload:
                try:
                    supabase.table("knowledge_edges").insert(edges_payload).execute()
                except Exception as e:
                    # Ignore duplicate edge constraint collisions
                    pass

        # Index into search_documents for Phase 8 integration
        try:
            search_indexer.index_document(
                user_id=user_id,
                task_id=None,
                source_type="knowledge",
                source_id=knowledge_id,
                title=created_item["title"],
                content=f"{created_item['title']}\n{created_item.get('summary', '')}\n{created_item['content']}",
                metadata={"type": created_item["type"], "origin": created_item["origin"]}
            )
        except Exception as e:
            # Non-blocking search indexing
            pass

        return created_item

    def get_knowledge(self, user_id: str, knowledge_id: str) -> Dict[str, Any]:
        """Fetches a single knowledge item with sources, relationships, and backlinks."""
        supabase = get_supabase()

        res = supabase.table("knowledge_items")\
            .select("*")\
            .eq("id", knowledge_id)\
            .eq("user_id", user_id)\
            .execute()

        if not res.data:
            raise HTTPException(status_code=404, detail="Knowledge item not found or not owned by user")

        item = res.data[0]

        # Sources
        sources_res = supabase.table("knowledge_sources")\
            .select("*")\
            .eq("knowledge_id", knowledge_id)\
            .eq("user_id", user_id)\
            .execute()
        item["sources"] = sources_res.data or []

        # Outgoing & Incoming Relationships
        edges_res = supabase.table("knowledge_edges")\
            .select("*, target_knowledge:target_knowledge_id(id, title, type, status)")\
            .eq("source_knowledge_id", knowledge_id)\
            .eq("user_id", user_id)\
            .execute()
        item["relationships"] = edges_res.data or []

        # Backlinks: other knowledge items linking TO this one, or tasks where this knowledge is referenced
        incoming_edges = supabase.table("knowledge_edges")\
            .select("*, source_knowledge:source_knowledge_id(id, title, type, status)")\
            .eq("target_knowledge_id", knowledge_id)\
            .eq("user_id", user_id)\
            .execute().data or []

        backlinks = []
        for edge in incoming_edges:
            src = edge.get("source_knowledge") or {}
            backlinks.append({
                "type": "knowledge",
                "id": edge["source_knowledge_id"],
                "title": src.get("title", "Untitled Knowledge"),
                "relationship": edge["relationship_type"]
            })

        # Tasks referencing this knowledge via sources
        task_refs = supabase.table("knowledge_sources")\
            .select("source_id, source_name")\
            .eq("knowledge_id", knowledge_id)\
            .eq("source_type", "task")\
            .execute().data or []
        for ref in task_refs:
            if ref.get("source_id"):
                backlinks.append({
                    "type": "task",
                    "id": ref["source_id"],
                    "title": ref.get("source_name") or "Referenced Task",
                    "relationship": "derived_from_task"
                })

        item["backlinks"] = backlinks
        return item

    def list_knowledge(
        self,
        user_id: str,
        type: Optional[str] = None,
        status: Optional[str] = "active",
        task_id: Optional[str] = None,
        source_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Paginated list of knowledge items with filtering."""
        supabase = get_supabase()

        query = supabase.table("knowledge_items")\
            .select("*", count="exact")\
            .eq("user_id", user_id)

        if status:
            query = query.eq("status", status)

        if type:
            query = query.eq("type", type)

        # Filter by task_id via knowledge_sources if requested
        if task_id:
            src_res = supabase.table("knowledge_sources")\
                .select("knowledge_id")\
                .eq("user_id", user_id)\
                .eq("source_type", "task")\
                .eq("source_id", task_id)\
                .execute()
            k_ids = [r["knowledge_id"] for r in (src_res.data or [])]
            if not k_ids:
                return {"items": [], "total": 0, "limit": limit, "offset": offset}
            query = query.in_("id", k_ids)

        if source_id:
            src_res = supabase.table("knowledge_sources")\
                .select("knowledge_id")\
                .eq("user_id", user_id)\
                .eq("source_id", source_id)\
                .execute()
            k_ids = [r["knowledge_id"] for r in (src_res.data or [])]
            if not k_ids:
                return {"items": [], "total": 0, "limit": limit, "offset": offset}
            query = query.in_("id", k_ids)

        query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
        res = query.execute()

        return {
            "items": res.data or [],
            "total": res.count or len(res.data or []),
            "limit": limit,
            "offset": offset
        }

    def update_knowledge(self, user_id: str, knowledge_id: str, data: KnowledgeUpdate) -> Dict[str, Any]:
        """Edits title, type, content, or summary while preserving created_at and origin."""
        supabase = get_supabase()

        # Verify existence and ownership
        existing = supabase.table("knowledge_items")\
            .select("*")\
            .eq("id", knowledge_id)\
            .eq("user_id", user_id)\
            .execute()

        if not existing.data:
            raise HTTPException(status_code=404, detail="Knowledge item not found or not owned by user")

        update_payload = {"updated_at": datetime.now(timezone.utc).isoformat()}
        if data.title is not None:
            update_payload["title"] = data.title.strip()
        if data.type is not None:
            update_payload["type"] = data.type.value
        if data.content is not None:
            update_payload["content"] = data.content
        if data.summary is not None:
            update_payload["summary"] = data.summary

        res = supabase.table("knowledge_items")\
            .update(update_payload)\
            .eq("id", knowledge_id)\
            .eq("user_id", user_id)\
            .execute()

        updated_item = res.data[0]

        # Update search index
        try:
            search_indexer.index_document(
                user_id=user_id,
                task_id=None,
                source_type="knowledge",
                source_id=knowledge_id,
                title=updated_item["title"],
                content=f"{updated_item['title']}\n{updated_item.get('summary', '')}\n{updated_item['content']}",
                metadata={"type": updated_item["type"], "origin": updated_item["origin"]}
            )
        except Exception:
            pass

        return updated_item

    def archive_knowledge(self, user_id: str, knowledge_id: str) -> Dict[str, Any]:
        """Sets status to archived without deleting data."""
        supabase = get_supabase()
        res = supabase.table("knowledge_items")\
            .update({
                "status": KnowledgeStatus.ARCHIVED.value,
                "archived_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            })\
            .eq("id", knowledge_id)\
            .eq("user_id", user_id)\
            .execute()

        if not res.data:
            raise HTTPException(status_code=404, detail="Knowledge item not found")

        return res.data[0]

    def restore_knowledge(self, user_id: str, knowledge_id: str) -> Dict[str, Any]:
        """Restores an archived knowledge item back to active status."""
        supabase = get_supabase()
        res = supabase.table("knowledge_items")\
            .update({
                "status": KnowledgeStatus.ACTIVE.value,
                "archived_at": None,
                "updated_at": datetime.now(timezone.utc).isoformat()
            })\
            .eq("id", knowledge_id)\
            .eq("user_id", user_id)\
            .execute()

        if not res.data:
            raise HTTPException(status_code=404, detail="Knowledge item not found")

        return res.data[0]

    def delete_knowledge(self, user_id: str, knowledge_id: str) -> Dict[str, Any]:
        """Permanently deletes a knowledge item, cleaning up sources, edges, and search indices."""
        supabase = get_supabase()

        # Delete edges where this knowledge is either source or target
        supabase.table("knowledge_edges")\
            .delete()\
            .eq("user_id", user_id)\
            .or_(f"source_knowledge_id.eq.{knowledge_id},target_knowledge_id.eq.{knowledge_id}")\
            .execute()

        # Delete sources
        supabase.table("knowledge_sources")\
            .delete()\
            .eq("knowledge_id", knowledge_id)\
            .eq("user_id", user_id)\
            .execute()

        # Delete knowledge item
        res = supabase.table("knowledge_items")\
            .delete()\
            .eq("id", knowledge_id)\
            .eq("user_id", user_id)\
            .execute()

        if not res.data:
            raise HTTPException(status_code=404, detail="Knowledge item not found")

        # Clean search document
        try:
            supabase.table("search_documents")\
                .delete()\
                .eq("source_type", "knowledge")\
                .eq("source_id", knowledge_id)\
                .eq("user_id", user_id)\
                .execute()
        except Exception:
            pass

        return {"status": "success", "deleted_id": knowledge_id}

    def add_relationship(
        self,
        user_id: str,
        source_id: str,
        target_id: str,
        rel_type: RelationshipType
    ) -> Dict[str, Any]:
        """Connects two knowledge items belonging to the same user."""
        if source_id == target_id:
            raise HTTPException(status_code=400, detail="Cannot create self-referencing relationship")

        supabase = get_supabase()

        # Verify both items exist and belong to user
        items = supabase.table("knowledge_items")\
            .select("id")\
            .eq("user_id", user_id)\
            .in_("id", [source_id, target_id])\
            .execute().data or []

        if len(items) < 2:
            raise HTTPException(status_code=403, detail="Both knowledge items must belong to the authenticated user")

        payload = {
            "user_id": user_id,
            "source_knowledge_id": source_id,
            "target_knowledge_id": target_id,
            "relationship_type": rel_type.value,
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        try:
            res = supabase.table("knowledge_edges").insert(payload).execute()
            return res.data[0]
        except Exception as e:
            if "uq_knowledge_relationship" in str(e) or "duplicate" in str(e).lower():
                raise HTTPException(status_code=409, detail="Relationship already exists")
            raise HTTPException(status_code=500, detail=str(e))

    def delete_relationship(self, user_id: str, relationship_id: str) -> Dict[str, Any]:
        """Removes a knowledge relationship edge."""
        supabase = get_supabase()
        res = supabase.table("knowledge_edges")\
            .delete()\
            .eq("id", relationship_id)\
            .eq("user_id", user_id)\
            .execute()

        if not res.data:
            raise HTTPException(status_code=404, detail="Relationship not found")

        return {"status": "success", "deleted_id": relationship_id}

    def add_source(
        self,
        user_id: str,
        knowledge_id: str,
        source_type: SourceType,
        source_id: Optional[str] = None,
        source_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Attaches a source to an existing knowledge item."""
        supabase = get_supabase()

        # Check knowledge ownership
        k_check = supabase.table("knowledge_items")\
            .select("id")\
            .eq("id", knowledge_id)\
            .eq("user_id", user_id)\
            .execute()
        if not k_check.data:
            raise HTTPException(status_code=404, detail="Knowledge item not found")

        # If source is a task, verify ownership
        if source_type == SourceType.TASK and source_id:
            task_check = supabase.table("tasks")\
                .select("id")\
                .eq("id", source_id)\
                .eq("user_id", user_id)\
                .execute()
            if not task_check.data:
                raise HTTPException(status_code=403, detail="Cannot link source task from another user")

        # If source is a resource, verify ownership
        if source_type == SourceType.RESOURCE and source_id:
            res_check = supabase.table("task_resources")\
                .select("id")\
                .eq("id", source_id)\
                .eq("user_id", user_id)\
                .execute()
            if not res_check.data:
                raise HTTPException(status_code=403, detail="Cannot link resource from another user")

        payload = {
            "user_id": user_id,
            "knowledge_id": knowledge_id,
            "source_type": source_type.value,
            "source_id": source_id,
            "source_name": source_name,
            "metadata": metadata or {},
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        res = supabase.table("knowledge_sources").insert(payload).execute()
        return res.data[0]

    def delete_source(self, user_id: str, source_id: str) -> Dict[str, Any]:
        """Removes a source reference from a knowledge item."""
        supabase = get_supabase()
        res = supabase.table("knowledge_sources")\
            .delete()\
            .eq("id", source_id)\
            .eq("user_id", user_id)\
            .execute()

        if not res.data:
            raise HTTPException(status_code=404, detail="Source not found")

        return {"status": "success", "deleted_id": source_id}

    def get_related_knowledge_graph(self, user_id: str, knowledge_id: str, depth: int = 1) -> Dict[str, Any]:
        """Performs bounded graph traversal starting from a knowledge item."""
        clamped_depth = min(max(1, depth), MAX_KNOWLEDGE_DEPTH)
        supabase = get_supabase()

        visited_node_ids = {knowledge_id}
        frontier = {knowledge_id}
        collected_edges = []
        collected_nodes = {}

        # Fetch starting node
        root = supabase.table("knowledge_items")\
            .select("id, title, type, status, summary")\
            .eq("id", knowledge_id)\
            .eq("user_id", user_id)\
            .execute()
        if not root.data:
            raise HTTPException(status_code=404, detail="Knowledge item not found")
        collected_nodes[knowledge_id] = root.data[0]

        for _ in range(clamped_depth):
            if not frontier or len(collected_nodes) >= MAX_KNOWLEDGE_NODES:
                break

            current_ids = list(frontier)
            edges_res = supabase.table("knowledge_edges")\
                .select("*")\
                .eq("user_id", user_id)\
                .in_("source_knowledge_id", current_ids)\
                .limit(MAX_KNOWLEDGE_EDGES)\
                .execute().data or []

            next_frontier = set()
            for edge in edges_res:
                collected_edges.append(edge)
                target_id = edge["target_knowledge_id"]
                if target_id not in visited_node_ids and len(collected_nodes) < MAX_KNOWLEDGE_NODES:
                    visited_node_ids.add(target_id)
                    next_frontier.add(target_id)

            if next_frontier:
                nodes_res = supabase.table("knowledge_items")\
                    .select("id, title, type, status, summary")\
                    .eq("user_id", user_id)\
                    .in_("id", list(next_frontier))\
                    .execute().data or []
                for node in nodes_res:
                    collected_nodes[node["id"]] = node

            frontier = next_frontier

        return {
            "root_id": knowledge_id,
            "depth": clamped_depth,
            "nodes": list(collected_nodes.values()),
            "edges": collected_edges[:MAX_KNOWLEDGE_EDGES]
        }

knowledge_service = KnowledgeService()
