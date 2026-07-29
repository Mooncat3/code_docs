from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session
from typing import List
from app.schemas.project import Project, ProjectCreate, ProjectUpdate, ProjectsSearch
from app.database import get_db
from app.utils.security import get_current_user, get_current_user_if_exist
from app.models.user import User
from app.models.project import Project as DBProject
from app.services.code_analysis import process_uploaded_file
from uuid import UUID
from . import get_project as get_db_project

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=Project, status_code=status.HTTP_201_CREATED)
def create_project(
        project: ProjectCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    db_project = DBProject(
        title=project.title,
        description=project.description,
        is_public=project.is_public,
        owner_id=current_user.id
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@router.put("/{project_id}", response_model=Project)
def update_project(
        project_id: UUID,
        project: ProjectUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    db_project = db.query(DBProject).filter(
        and_(DBProject.id == project_id,
             DBProject.owner_id == current_user.id)
    ).first()

    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.title is not None:
        db_project.title = project.title
    if project.description is not None:
        db_project.description = project.description
    if project.is_public is not None:
        db_project.is_public = project.is_public

    db.commit()
    db.refresh(db_project)
    return db_project


@router.delete("/{project_id}", response_model=dict)
def delete_project(
        project_id: UUID,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    db_project = db.query(DBProject).filter(
        and_(DBProject.id == project_id,
             DBProject.owner_id == current_user.id)
    ).first()

    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(db_project)
    db.commit()
    return {"message": "deleted"}


@router.get("/{project_id}", response_model=Project)
def get_project(
        project_id: UUID,
        db: Session = Depends(get_db),
        current_user: User | None = Depends(get_current_user_if_exist)
):
    db_project = get_db_project(db, project_id, current_user)

    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    return db_project


@router.get("/", response_model=ProjectsSearch)
def search_projects(
        skip: int = 0,
        limit: int = 100,
        query: str = "",
        db: Session = Depends(get_db)
):
    projects = db.query(DBProject).filter(DBProject.is_public)
    if query:
        query = f"%{' '.join(query.strip().lower().split())}%"
        projects = projects.filter(or_(DBProject.title.like(query),
                                       DBProject.description.like(query)))
    total_count = projects.count()
    projects = projects.offset(skip).limit(limit).all()
    return {
        "projects": projects,
        "total_count": total_count
    }


@router.get("/my/", response_model=List[Project])
def my_projects(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    projects = db.query(DBProject).filter(and_(DBProject.owner_id == current_user.id)).all()
    return projects


@router.post("/{project_id}/files", response_model=dict, status_code=status.HTTP_201_CREATED)
async def upload_file_to_project(
        project_id: UUID,
        files: List[UploadFile],
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    db_project = db.query(DBProject).filter(
        and_(DBProject.id == project_id,
             DBProject.owner_id == current_user.id)
    ).first()

    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    for file in files:
        if file.size is not None and file.size <= 8 * 1024 * 1024:
            content = await file.read()
            content_str = content.decode("utf-8", errors="ignore")
            process_uploaded_file(db, content_str, file.filename, project_id)
    return {"message": "Files uploaded"}
