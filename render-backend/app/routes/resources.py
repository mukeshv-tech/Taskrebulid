from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl
from app.auth import get_current_user
from app.services.resource_service import create_resource, list_resources, delete_resource
from urllib.parse import urlparse

router = APIRouter()

class ResourceCreate(BaseModel):
    url: str
    title: str = ""

@router.get("/api/tasks/{task_id}/resources")
def get_task_resources(task_id: str, user = Depends(get_current_user)):
    try:
        resources = list_resources(task_id, user.id)
        return resources
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch resources: {str(e)}")

@router.post("/api/tasks/{task_id}/resources")
def add_task_resource(task_id: str, resource: ResourceCreate, user = Depends(get_current_user)):
    try:
        # Simple URL validation
        parsed = urlparse(resource.url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise HTTPException(status_code=400, detail="Invalid URL format")
            
        new_resource = create_resource(task_id, user.id, resource.url, resource.title)
        return new_resource
    except ValueError as e:
        if str(e) == "Resource already exists in this task":
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=403, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add resource: {str(e)}")

@router.delete("/api/tasks/{task_id}/resources/{resource_id}")
def remove_task_resource(task_id: str, resource_id: str, user = Depends(get_current_user)):
    try:
        delete_resource(task_id, resource_id, user.id)
        return {"status": "deleted"}
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete resource: {str(e)}")
