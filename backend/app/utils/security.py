from typing import Type
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta, UTC
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy import or_
from app.config import settings
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(hours=settings.access_token_expire_hours)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt, expire


def read_user(db: Session, username: str) -> Type[User]:
    return db.query(User).filter(or_(User.username == username,
                                     User.email == username)).first()


def get_current_user(request: Request, db: Session = Depends(get_db)) -> Type[User]:
    token = request.cookies.get("code_docs_token")
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    user = read_user(db=db, username=username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are banned")
    return user


def get_current_user_if_exist(request: Request, db: Session = Depends(get_db)) -> Type[User] | None:
    try:
        return get_current_user(request, db)
    except HTTPException:
        return None


def role_required(required_role: str):
    def dependency(current_user: User = Depends(get_current_user)):
        role = str(current_user.role)
        if role == "admin":
            return current_user
        if role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return current_user

    return dependency
