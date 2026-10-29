from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from app.auth import get_current_user
from app.supabase import get_supabase
from app.services.knowledge_service import knowledge_service
from app.services.ai.service import ai_service
from app.schemas.knowledge import (
    KnowledgeCreate,
    KnowledgeUpdate,
    KnowledgeItemResponse,
    KnowledgeDetailResponse,
    KnowledgeListResponse,
    KnowledgeEdgeCreate,
    KnowledgeEdgeResponse,
    KnowledgeSourceInput,
    KnowledgeSourceResponse,
    DuplicateCheckRequest,
    DuplicateCheckResponse,
    AISuggestionsResponse,
    SuggestedKnowledgeItem,
    SuggestedKnowledgeRelationship,
    SaveFromTaskRequest,
    SaveFromResourceRequest,
    KnowledgeType,
    KnowledgeOrigin,
    SourceType
)

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])

@router.post("", response_model=KnowledgeItemResponse)
def create_knowledge(data: KnowledgeCreate, user = Depends(get_current_user)):
    """Create a new personal knowledge item for the authenticated user."""
    return knowledge_service.create_knowledge(user.id, data)

@router.get("", response_model=KnowledgeListResponse)
def list_knowledge(
    type: Optional[str] = Query(None, description="Filter by type (concept, topic, question, insight, note, resource)"),
    status: Optional[str] = Query("active", description="Filter by status (active, archived)"),
    task_id: Optional[str] = Query(None, description="Filter by source task ID"),
    source_id: Optional[str] = Query(None, description="Filter by generic source ID"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user = Depends(get_current_user)
):
    """List knowledge items belonging strictly to the authenticated user."""
    return knowledge_service.list_knowledge(
        user_id=user.id,
        type=type,
        status=status,
        task_id=task_id,
        source_id=source_id,
        limit=limit,
        offset=offset
    )

@router.post("/check-duplicate", response_model=DuplicateCheckResponse)
def check_duplicate(req: DuplicateCheckRequest, user = Depends(get_current_user)):
    """Check for existing similar knowledge items before creation."""
    return knowledge_service.check_duplicate(user.id, req.title)

@router.get("/{id}", response_model=KnowledgeDetailResponse)
def get_knowledge_detail(id: str, user = Depends(get_current_user)):
    """Get full details of a knowledge item including sources, relationships, and backlinks."""
    return knowledge_service.get_knowledge(user.id, id)

@router.patch("/{id}", response_model=KnowledgeItemResponse)
def update_knowledge(id: str, data: KnowledgeUpdate, user = Depends(get_current_user)):
    """Update title, type, content, or summary of a knowledge item."""
    return knowledge_service.update_knowledge(user.id, id, data)

@router.delete("/{id}")
def delete_knowledge(id: str, user = Depends(get_current_user)):
    """Permanently delete a knowledge item and its edges/sources."""
    return knowledge_service.delete_knowledge(user.id, id)

@router.post("/{id}/archive", response_model=KnowledgeItemResponse)
def archive_knowledge(id: str, user = Depends(get_current_user)):
    """Archive a knowledge item."""
    return knowledge_service.archive_knowledge(user.id, id)

@router.post("/{id}/restore", response_model=KnowledgeItemResponse)
def restore_knowledge(id: str, user = Depends(get_current_user)):
    """Restore an archived knowledge item."""
    return knowledge_service.restore_knowledge(user.id, id)

@router.get("/{id}/sources", response_model=List[KnowledgeSourceResponse])
def get_sources(id: str, user = Depends(get_current_user)):
    """List sources attached to this knowledge item."""
    item = knowledge_service.get_knowledge(user.id, id)
    return item.get("sources", [])

@router.post("/{id}/sources", response_model=KnowledgeSourceResponse)
def add_source(id: str, src: KnowledgeSourceInput, user = Depends(get_current_user)):
    """Attach a source to a knowledge item."""
    return knowledge_service.add_source(
        user_id=user.id,
        knowledge_id=id,
        source_type=src.source_type,
        source_id=src.source_id,
        source_name=src.source_name,
        metadata=src.metadata
    )

@router.delete("/{id}/sources/{source_id}")
def delete_source(id: str, source_id: str, user = Depends(get_current_user)):
    """Remove a source reference from a knowledge item."""
    return knowledge_service.delete_source(user.id, source_id)

@router.get("/{id}/related")
def get_related_graph(id: str, depth: int = Query(1, ge=1, le=3), user = Depends(get_current_user)):
    """Get the bounded knowledge graph around this item."""
    return knowledge_service.get_related_knowledge_graph(user.id, id, depth=depth)

@router.post("/{id}/relationships", response_model=KnowledgeEdgeResponse)
def create_relationship(id: str, edge: KnowledgeEdgeCreate, user = Depends(get_current_user)):
    """Connect this knowledge item to another knowledge item belonging to the user."""
    return knowledge_service.add_relationship(
        user_id=user.id,
        source_id=id,
        target_id=edge.target_knowledge_id,
        rel_type=edge.relationship_type
    )

@router.delete("/{id}/relationships/{relationship_id}")
def delete_relationship(id: str, relationship_id: str, user = Depends(get_current_user)):
    """Delete a relationship between knowledge items."""
    return knowledge_service.delete_relationship(user.id, relationship_id)

# --- Task Integration Routes ---

task_router = APIRouter(prefix="/api/tasks/{task_id}/knowledge", tags=["knowledge"])

@task_router.post("/suggestions", response_model=AISuggestionsResponse)
async def get_task_knowledge_suggestions(task_id: str, user = Depends(get_current_user)):
    """AI suggests reusable knowledge items and relationships based on task activity and resources."""
    supabase = get_supabase()

    # Verify task ownership
    task_res = supabase.table("tasks").select("*").eq("id", task_id).eq("user_id", user.id).execute()
    if not task_res.data:
        raise HTTPException(status_code=403, detail="Task not found or not owned by user")
    task = task_res.data[0]

    # Gather task resources & activity
    res_res = supabase.table("task_resources").select("id, url, title").eq("task_id", task_id).execute()
    act_res = supabase.table("task_activity").select("id, event_type, url, title, timestamp").eq("task_id", task_id).order("timestamp", desc=True).limit(10).execute()
    
    # Gather up to 10 existing knowledge items to allow the AI to suggest relationships
    existing_k = supabase.table("knowledge_items").select("id, title, type").eq("user_id", user.id).limit(10).execute().data or []

    task_payload = {
        "id": task_id,
        "name": task["name"],
        "resources": res_res.data or [],
        "activity": act_res.data or []
    }

    raw_suggestions = await ai_service.suggest_knowledge(task_payload, existing_k)

    # Strictly validate suggestions
    validated_items = []
    for s in raw_suggestions.get("suggestions", []):
        try:
            k_type = s.get("type", "concept")
            if k_type not in [t.value for t in KnowledgeType]:
                k_type = "concept"
            validated_items.append(SuggestedKnowledgeItem(
                type=KnowledgeType(k_type),
                title=s.get("title", f"Knowledge from {task['name']}"),
                summary=s.get("summary", ""),
                content=s.get("content", ""),
                confidence=float(s.get("confidence", 0.8)),
                source_name=task["name"],
                source_type=SourceType.TASK,
                source_id=task_id
            ))
        except Exception:
            continue

    validated_rels = []
    for r in raw_suggestions.get("suggested_relationships", []):
        try:
            rel_type = r.get("relationship_type", "related_to")
            from app.schemas.knowledge import RelationshipType
            if rel_type not in [rt.value for rt in RelationshipType]:
                rel_type = "related_to"
            validated_rels.append(SuggestedKnowledgeRelationship(
                source_knowledge_id=r.get("source_knowledge_id", ""),
                target_knowledge_id=r.get("target_knowledge_id", ""),
                relationship_type=RelationshipType(rel_type),
                reason=r.get("reason", "Related concepts"),
                confidence=float(r.get("confidence", 0.8))
            ))
        except Exception:
            continue

    return AISuggestionsResponse(
        suggestions=validated_items,
        suggested_relationships=validated_rels
    )

@task_router.post("/save-from-task", response_model=KnowledgeItemResponse)
def save_from_task(task_id: str, req: SaveFromTaskRequest, user = Depends(get_current_user)):
    """Saves useful task summary/concepts directly as user knowledge with preserved provenance."""
    supabase = get_supabase()
    task_res = supabase.table("tasks").select("*").eq("id", task_id).eq("user_id", user.id).execute()
    if not task_res.data:
        raise HTTPException(status_code=403, detail="Task not found or not owned by user")
    task = task_res.data[0]

    sources = []
    if req.include_task_as_source:
        sources.append(KnowledgeSourceInput(
            source_type=SourceType.TASK,
            source_id=task_id,
            source_name=task["name"]
        ))

    # Check for latest task AI analysis to include as reference
    if req.include_summary_as_source:
        analysis_res = supabase.table("task_ai_analyses")\
            .select("id, result")\
            .eq("task_id", task_id)\
            .order("created_at", desc=True)\
            .limit(1)\
            .execute()
        if analysis_res.data:
            sources.append(KnowledgeSourceInput(
                source_type=SourceType.AI_ANALYSIS,
                source_id=analysis_res.data[0]["id"],
                source_name=f"AI Analysis of {task['name']}"
            ))

    k_data = KnowledgeCreate(
        type=req.type,
        title=req.title,
        content=req.content or req.summary or f"Knowledge extracted from task '{task['name']}'.",
        summary=req.summary,
        origin=KnowledgeOrigin.USER,
        sources=sources
    )

    return knowledge_service.create_knowledge(user.id, k_data)

@task_router.post("/resources/{resource_id}/save-as-knowledge", response_model=KnowledgeItemResponse)
def save_from_resource(task_id: str, resource_id: str, req: SaveFromResourceRequest, user = Depends(get_current_user)):
    """Turns a saved resource into a permanent knowledge item, preserving the resource as a source."""
    supabase = get_supabase()
    res_data = supabase.table("task_resources")\
        .select("*")\
        .eq("id", resource_id)\
        .eq("task_id", task_id)\
        .eq("user_id", user.id)\
        .execute()

    if not res_data.data:
        raise HTTPException(status_code=404, detail="Resource not found or not owned by user")
    resource = res_data.data[0]

    title = req.title or resource.get("title") or resource.get("url") or "Saved Resource Knowledge"
    content = req.content or f"Knowledge item created from resource: {resource.get('url')}\nTitle: {resource.get('title')}"

    sources = [
        KnowledgeSourceInput(
            source_type=SourceType.RESOURCE,
            source_id=resource_id,
            source_name=resource.get("title") or resource.get("url"),
            metadata={"url": resource.get("url")}
        ),
        KnowledgeSourceInput(
            source_type=SourceType.TASK,
            source_id=task_id,
            source_name="Task"
        )
    ]

    k_data = KnowledgeCreate(
        type=req.type,
        title=title,
        content=content,
        summary=req.summary or resource.get("title"),
        origin=KnowledgeOrigin.USER,
        sources=sources
    )

    return knowledge_service.create_knowledge(user.id, k_data)
