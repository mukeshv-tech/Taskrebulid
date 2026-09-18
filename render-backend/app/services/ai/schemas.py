from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Topic(BaseModel):
    name: str
    confidence: float = Field(ge=0.0, le=1.0)

class ResourceAnalysis(BaseModel):
    resource_id: str
    relevance: float = Field(ge=0.0, le=1.0)
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
