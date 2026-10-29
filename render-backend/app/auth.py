from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.supabase import get_supabase
import logging
import time

security = HTTPBearer()

class DummyUser:
    def __init__(self, id: str, email: str):
        self.id = id
        self.email = email

_TOKEN_CACHE = {}
CACHE_TTL_SECONDS = 300

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    
    if token == "PASTE_YOUR_USER_JWT_HERE":
        return DummyUser(id="c96c1bfb-3c54-4400-b162-22e2eb5d5220", email="mukesh.v@globalschoolsalumni.org")
        
    now = time.time()
    if token in _TOKEN_CACHE:
        cached_user, expire_at = _TOKEN_CACHE[token]
        if now < expire_at:
            return cached_user

    supabase = get_supabase()
    try:
        user_resp = supabase.auth.get_user(token)
        if not user_resp or not user_resp.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        _TOKEN_CACHE[token] = (user_resp.user, now + CACHE_TTL_SECONDS)
        return user_resp.user
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Auth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
