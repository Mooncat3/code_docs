from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import User, UserUpdate
from app.models.user import User as DBUser
from app.utils.security import get_current_user, role_required
from app.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/", response_model=User)
async def read_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/", response_model=List[User])
async def read_users(db: Session = Depends(get_db),
                     _: User = Depends(role_required("admin"))):
    db_users = db.query(DBUser).all()
    return db_users


@router.delete("/{user_id}", response_model=dict)
async def delete_user(user_id: UUID, db: Session = Depends(get_db),
                      _: User = Depends(role_required("admin"))):
    db_user = db.query(DBUser).filter(DBUser.id == user_id).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()
    return {"message": "deleted"}


@router.put("/{user_id}", response_model=User)
async def edit_user(user_id: UUID, user_data: UserUpdate, db: Session = Depends(get_db),
                    _: User = Depends(role_required("admin"))):
    db_user = db.query(DBUser).filter(DBUser.id == user_id).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_data.is_active is not None:
        db_user.is_active = user_data.is_active
    db.commit()
    return db_user
