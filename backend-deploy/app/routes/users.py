from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_role
from app.models.user import User

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me")
def get_me(current_user: User = Depends(require_role("ADMIN", "ANALYST", "VIEWER"))):
    return current_user
