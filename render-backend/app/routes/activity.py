from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.auth import get_current_user
from app.services.activity_service import record_activity, get_activity

router = APIRouter()

class ActivityEvent(BaseModel):
    event_type: str
    url: Optional[str] = None
    title: Optional[str] = None
    tab_id: Optional[str] = None
    window_id: Optional[str] = None
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None

class ActivityBatch(BaseModel):
    events: List[ActivityEvent]

from fastapi import BackgroundTasks
import time

def index_activities_bg(user_id: str, task_id: str, inserted_events: List[Dict[str, Any]]):
    from app.services.search_indexer import search_indexer
    for act in inserted_events:
        if not act.get("title") and not act.get("url"):
            continue
        try:
            search_indexer.index_document(
                user_id=user_id,
                task_id=task_id,
                source_type="activity",
                source_id=act.get("id"),
                title=act.get("title") or "Browser Activity",
                content=act.get("url") or ""
            )
        except Exception as e:
            print(f"Background activity indexing failed: {e}")
        time.sleep(0.2) # Yield CPU

@router.post("/api/tasks/{task_id}/activity")
def add_task_activity(task_id: str, batch: ActivityBatch, background_tasks: BackgroundTasks, user = Depends(get_current_user)):
    try:
        # Convert Pydantic models to dicts
        events_dict = [event.model_dump() for event in batch.events]
        result = record_activity(task_id, user.id, events_dict)
        if result:
            background_tasks.add_task(index_activities_bg, user.id, task_id, result)
        return {"status": "success", "count": len(result)}
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record activity: {str(e)}")

@router.get("/api/tasks/{task_id}/activity")
def list_task_activity(task_id: str, user = Depends(get_current_user)):
    try:
        return get_activity(task_id, user.id)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch activity: {str(e)}")

@router.delete("/api/tasks/{task_id}/activity/{activity_id}")
def delete_task_activity(task_id: str, activity_id: str, user = Depends(get_current_user)):
    from app.services.activity_service import delete_activity
    try:
        delete_activity(task_id, activity_id, user.id)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete activity: {str(e)}")

@router.delete("/api/tasks/{task_id}/activity")
def clear_task_activity(task_id: str, user = Depends(get_current_user)):
    from app.services.activity_service import delete_all_activity
    try:
        delete_all_activity(task_id, user.id)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear activity: {str(e)}")
