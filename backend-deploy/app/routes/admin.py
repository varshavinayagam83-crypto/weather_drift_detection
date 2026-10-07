from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_role
from app.models.user import User

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users")
def list_users(db: Session = Depends(get_db), current_user: User = Depends(require_role("ADMIN"))):
    return {"items": db.query(User).all()}


@router.put("/users/{user_id}")
def update_user(user_id: int, payload: dict, db: Session = Depends(get_db), current_user: User = Depends(require_role("ADMIN"))):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if "role" in payload:
        user.role = payload["role"]
    if "is_active" in payload:
        user.is_active = bool(payload["is_active"])
    db.commit()
    return {"message": "User updated"}


@router.post("/import/stations")
def import_stations(payload: dict, db: Session = Depends(get_db), current_user: User = Depends(require_role("ADMIN"))):
    return {"message": "Station import job accepted", "count": len(payload.get("stations", []))}


@router.post("/import/weather")
def import_weather(payload: dict, db: Session = Depends(get_db), current_user: User = Depends(require_role("ADMIN"))):
    return {"message": "Weather import job accepted", "count": len(payload.get("weather_records", []))}
