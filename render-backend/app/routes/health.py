from fastapi import APIRouter

router = APIRouter()

@router.head("/health", include_in_schema=False)
@router.get("/health")
def health_check():
    return {"status": "Everything good gng"}
