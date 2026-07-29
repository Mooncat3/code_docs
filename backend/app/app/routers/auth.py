from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from datetime import timedelta, UTC, datetime
from app.schemas.user import UserCreate, UserLogin, User as UserSchema
from app.services.auth import authenticate_user, create_user
from app.utils.security import create_access_token
from app.database import get_db
from app.config import settings
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=UserSchema)
async def login_for_access_token(
        response: Response,
        form_data: UserLogin,
        db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token_expires = timedelta(hours=settings.access_token_expire_hours)
    access_token, expire_date = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    cookie_attributes = [
        f"code_docs_token={access_token}",
        f"Expires={expire_date.strftime('%a, %d %b %Y %H:%M:%S GMT')}",
        "Path=/",
        # "Secure",
        "HttpOnly",
        "SameSite=Lax",
        "Partitioned",
    ]
    response.headers.append("Set-Cookie", "; ".join(cookie_attributes))
    return user


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserSchema)
async def register_user(
        user: UserCreate,
        db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db=db, user=user)


@router.post("/logout", response_model=dict)
def logout_user(response: Response):
    expired_time = datetime.now(UTC) - timedelta(days=1)
    cookie_attributes = [
        "code_docs_token=",
        f"Expires={expired_time.strftime('%a, %d %b %Y %H:%M:%S GMT')}",
        "Path=/",
        # "Secure",
        "HttpOnly",
        "SameSite=Lax",
        "Partitioned",
    ]
    response.headers.append("Set-Cookie", "; ".join(cookie_attributes))
    return {"message": "User logged out successfully"}
