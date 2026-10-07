from datetime import datetime

from sqlalchemy.orm import Session

from app.models.user import User
from app.security import create_access_token, get_password_hash, verify_password


def register_user(db: Session, username: str, email: str, password: str, full_name: str | None = None) -> User:
    existing = db.query(User).filter((User.username == username) | (User.email == email.lower())).first()
    if existing:
        raise ValueError("User already exists")

    user = User(
        username=username,
        email=email.lower(),
        password_hash=get_password_hash(password),
        full_name=full_name,
        role="VIEWER",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = db.query(User).filter((User.username == username) | (User.email == username.lower())).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    user.last_login = datetime.utcnow()
    db.commit()
    return user


def user_to_token_payload(user: User) -> dict:
    return {"sub": user.username, "role": user.role}
