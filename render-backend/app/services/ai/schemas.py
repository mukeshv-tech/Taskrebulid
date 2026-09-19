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
    topics: List[Topic]
    resource_analysis: List[ResourceAnalysis]
    activity_summary: str
    suggested_next_steps: List[str]

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
    evidence: List[GraphEdgeEvidence] = Field(description="Evidence supporting this edge.")

class AIGraphAnalysisResult(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
