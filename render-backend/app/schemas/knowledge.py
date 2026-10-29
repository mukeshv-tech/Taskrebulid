from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class KnowledgeType(str, Enum):
    CONCEPT = "concept"
    TOPIC = "topic"
    QUESTION = "question"
    INSIGHT = "insight"
    NOTE = "note"
    RESOURCE = "resource"

class KnowledgeStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"

class KnowledgeOrigin(str, Enum):
    USER = "user"
    AI_APPROVED = "ai_approved"

class RelationshipType(str, Enum):
    RELATED_TO = "related_to"
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    DEPENDS_ON = "depends_on"
    EXPLAINS = "explains"
    DERIVED_FROM = "derived_from"

class SourceType(str, Enum):
    TASK = "task"
    RESOURCE = "resource"
    ACTIVITY = "activity"
    AI_ANALYSIS = "ai_analysis"
    SNAPSHOT = "snapshot"
    OTHER = "other"

# --- Request / Input Models ---

class KnowledgeSourceInput(BaseModel):
    source_type: SourceType
    source_id: Optional[str] = None
    source_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class KnowledgeCreate(BaseModel):
    type: KnowledgeType
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(default="")
    summary: Optional[str] = None
    origin: KnowledgeOrigin = KnowledgeOrigin.USER
    confidence: Optional[float] = 1.0
    sources: Optional[List[KnowledgeSourceInput]] = Field(default_factory=list)
    related_knowledge_ids: Optional[List[str]] = Field(default_factory=list)

class KnowledgeUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    type: Optional[KnowledgeType] = None
    content: Optional[str] = None
    summary: Optional[str] = None

class KnowledgeEdgeCreate(BaseModel):
    target_knowledge_id: str
    relationship_type: RelationshipType

class DuplicateCheckRequest(BaseModel):
    title: str

class DuplicateCheckResponse(BaseModel):
    has_duplicate: bool
    duplicate_type: Optional[str] = None  # "exact", "normalized", "semantic"
    existing_items: List[Dict[str, Any]] = Field(default_factory=list)

# --- Response Models ---

class KnowledgeSourceResponse(BaseModel):
    id: str
    knowledge_id: str
    source_type: str
    source_id: Optional[str] = None
    source_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

class KnowledgeEdgeResponse(BaseModel):
    id: str
    source_knowledge_id: str
    target_knowledge_id: str
    relationship_type: str
    target_knowledge: Optional[Dict[str, Any]] = None
    created_at: datetime

class KnowledgeItemResponse(BaseModel):
    id: str
    user_id: str
    type: str
    title: str
    content: str
    summary: Optional[str] = None
    status: str
    origin: str
    confidence: Optional[float] = 1.0
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime] = None

class KnowledgeDetailResponse(KnowledgeItemResponse):
    sources: List[KnowledgeSourceResponse] = Field(default_factory=list)
    relationships: List[KnowledgeEdgeResponse] = Field(default_factory=list)
    backlinks: List[Dict[str, Any]] = Field(default_factory=list)

class KnowledgeListResponse(BaseModel):
    items: List[KnowledgeItemResponse]
    total: int
    limit: int
    offset: int

# --- AI Suggestions ---

class SuggestedKnowledgeItem(BaseModel):
    type: KnowledgeType
    title: str
    summary: str
    content: str
    confidence: float = 0.8
    source_name: Optional[str] = None
    source_type: Optional[SourceType] = SourceType.TASK
    source_id: Optional[str] = None

class SuggestedKnowledgeRelationship(BaseModel):
    source_knowledge_id: str
    target_knowledge_id: str
    relationship_type: RelationshipType
    reason: str
    confidence: float = 0.8

class AISuggestionsResponse(BaseModel):
    suggestions: List[SuggestedKnowledgeItem] = Field(default_factory=list)
    suggested_relationships: List[SuggestedKnowledgeRelationship] = Field(default_factory=list)

# --- Save From Task / Resource Helpers ---

class SaveFromTaskRequest(BaseModel):
    title: str
    type: KnowledgeType = KnowledgeType.CONCEPT
    content: str = ""
    summary: Optional[str] = None
    include_summary_as_source: bool = True
    include_task_as_source: bool = True

class SaveFromResourceRequest(BaseModel):
    title: Optional[str] = None
    type: KnowledgeType = KnowledgeType.RESOURCE
    content: Optional[str] = None
    summary: Optional[str] = None
