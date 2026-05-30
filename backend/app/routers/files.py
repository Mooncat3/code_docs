from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session
from app.schemas.documentation import CodeEntity
from app.schemas.file import CodeFile, CodeFileClean
from app.database import get_db
from app.utils.security import get_current_user_if_exist, get_current_user
from app.models.user import User
from uuid import UUID
from . import get_project, get_file
from app.models.file import CodeFile as DBFile
from app.models.project import Project as DBProject

router = APIRouter(prefix="/files", tags=["files"])


@router.get("/{file_id}", response_model=CodeFile)
def read_file(
        file_id: UUID,
        db: Session = Depends(get_db),
        current_user: User | None = Depends(get_current_user_if_exist)
):
    db_file = get_file(db, file_id, current_user)

    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    return db_file


@router.delete("/{file_id}", response_model=dict)
def delete_file(
        file_id: UUID,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    db_file = db.query(DBFile).join(DBProject).filter(and_(
        DBFile.id == file_id,
        DBProject.owner_id == current_user.id)
    ).first()

    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    db.delete(db_file)
    db.commit()
    return {"message": "deleted"}


@router.get("/entities/{file_id}", response_model=List[CodeEntity])
def get_file_entities(
        file_id: UUID,
        db: Session = Depends(get_db),
        current_user: User | None = Depends(get_current_user_if_exist)
):
    db_file = get_file(db, file_id, current_user)

    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    return db_file.entities


@router.get("/project/{project_id}", response_model=List[CodeFileClean])
async def get_project_files(
        project_id: UUID,
        db: Session = Depends(get_db),
        current_user: User | None = Depends(get_current_user_if_exist)
):
    db_project = get_project(db, project_id, current_user)

    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    return db_project.files
