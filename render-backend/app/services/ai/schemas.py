from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Topic(BaseModel):
    name: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

class ResourceAnalysis(BaseModel):
    resource_id: str
    relevance: float = Field(default=1.0, ge=0.0, le=1.0)
    reason: str

class AIAnalysisResult(BaseModel):
    task_summary: str
    topics: List[Topic] = Field(default_factory=list)
    resource_analysis: List[ResourceAnalysis] = Field(default_factory=list)
    activity_summary: str
    suggested_next_steps: List[str] = Field(default_factory=list)

class TaskActivityInput(BaseModel):
    id: str
    event_type: str
    url: Optional[str]
    title: Optional[str]
    timestamp: str

class TaskResourceInput(BaseModel):
    id: str
    url: str
    title: Optional[str]

class AIAnalysisInput(BaseModel):
    task_id: str
    task_name: str
    resources: List[TaskResourceInput]
    activity: List[TaskActivityInput]

class GraphNode(BaseModel):
    label: str = Field(description="Normalized name of the topic, concept, question, or goal.")
    node_type: str = Field(description="One of: 'topic', 'concept', 'question', 'goal', 'resource'.")
    description: Optional[str] = Field(default=None, description="Brief explanation of this node.")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0.")

class GraphEdgeEvidence(BaseModel):
    resource_id: Optional[str] = Field(default=None, description="If evidence comes from a resource, its ID.")
    reason: str = Field(description="Brief explanation of why this edge exists based strictly on available context.")

class GraphEdge(BaseModel):
    source_label: str = Field(description="Label of the source node.")
    target_label: str = Field(description="Label of the target node.")
    relationship_type: str = Field(description="One of: 'related_to', 'about', 'requires', 'answers', 'part_of', 'references'.")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0.")
    evidence: List[GraphEdgeEvidence] = Field(default_factory=list, description="Evidence supporting this edge.")

class AIGraphAnalysisResult(BaseModel):
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)

class ResumeImportantResource(BaseModel):
    resource_id: str
    reason: str

class AIResumeResult(BaseModel):
    resume_summary: str
    what_you_were_doing: str
    last_known_progress: str
    important_resources: List[ResumeImportantResource] = Field(default_factory=list)
    open_questions: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

class AIResumeInput(BaseModel):
    task_id: str
    task_name: str
    resources: List[dict]
    activity: List[dict]
    latest_analysis: Optional[dict] = None
    task_graph: Optional[dict] = None
    previous_snapshot: Optional[dict] = None
