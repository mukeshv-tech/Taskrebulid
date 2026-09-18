from fastapi import APIRouter, Depends
from app.auth import get_current_user

router = APIRouter()

@router.get("/api/me")
def get_me(user = Depends(get_current_user)):
    return {"id": user.id, "email": user.email}
