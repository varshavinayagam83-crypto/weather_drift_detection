from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.security import create_access_token
from app.services.auth_service import authenticate_user, register_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register")
def register(payload: dict, db: Session = Depends(get_db)):
    try:
        user = register_user(db, payload["username"], payload["email"], payload["password"], payload.get("full_name"))
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
    return {"message": "User registered", "user": {"id": user.id, "username": user.username, "email": user.email, "role": user.role}}


@router.post("/login")
def login(payload: dict, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload["username"], payload["password"])
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(user.username, timedelta(minutes=30))
    return {"access_token": token, "token_type": "bearer", "user": {"id": user.id, "username": user.username, "role": user.role}}


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username, "email": current_user.email, "role": current_user.role}


@router.post("/logout")
def logout():
    return {"message": "Logged out successfully"}
