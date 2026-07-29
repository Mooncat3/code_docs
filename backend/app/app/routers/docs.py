from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.schemas.documentation import CodeEntity, CodeEntityUpdate
from app.database import get_db
from app.utils.security import get_current_user, get_current_user_if_exist
from app.models.documentation import CodeEntity as DBEntity
from app.models.project import Project
from app.models.file import CodeFile
from app.models.user import User
from app.services.documentation_generator import generate_html_documentation
from fastapi.responses import HTMLResponse
from uuid import UUID
from app.models import get_utc_timestamp
from . import get_project, get_entity as get_db_entity
from app.utils.insert_docstring import insert_docstring

router = APIRouter(prefix="/docs", tags=["documentation"])


@router.get("/entities/{entity_id}", response_model=CodeEntity)
def get_entity(
        entity_id: UUID,
        db: Session = Depends(get_db),
        current_user: User | None = Depends(get_current_user_if_exist)
):
    db_entity = get_db_entity(db, entity_id, current_user)

    if not db_entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    return db_entity


@router.put("/entities/{entity_id}", response_model=CodeEntity)
def update_entity_docs(
        entity_id: UUID,
        docs: CodeEntityUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    db_entity = db.query(DBEntity).join(CodeFile).join(Project).filter(and_(
        DBEntity.id == entity_id,
        Project.owner_id == current_user.id)
    ).first()

    if not db_entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    if docs.docs is not None:
        db_entity.modified_timestamp = get_utc_timestamp()

        db_entity.modified_docs = docs.docs
        content = db_entity.file.modified_content if db_entity.file.modified_content is not None \
            else db_entity.file.original_content
        db_entity.file.modified_content = insert_docstring(db_entity.file.language, content, db_entity, docs.docs)

    if docs.visibility is not None:
        db_entity.visibility = docs.visibility
    db.commit()
    db.refresh(db_entity)
    return db_entity


@router.get("/project/{project_id}/search")
def search_project_documentation(
        project_id: UUID,
        query: str = "",
        db: Session = Depends(get_db),
        current_user: User | None = Depends(get_current_user_if_exist)
):
    db_project = get_project(db, project_id, current_user)

    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    entities = db.query(DBEntity).join(CodeFile).filter(
        CodeFile.project_id == project_id
    )

    if query:
        query = f"%{' '.join(query.strip().lower().split())}%"
        entities = entities.filter(DBEntity.name.like(query))

    return HTMLResponse(content=generate_html_documentation(db_project, entities.all()), status_code=200)


@router.get("/project/{project_id}/html")
def get_project_documentation_html(
        project_id: UUID,
        db: Session = Depends(get_db),
        current_user: User | None = Depends(get_current_user_if_exist)
):
    db_project = get_project(db, project_id, current_user)

    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    entities = db.query(DBEntity).join(CodeFile).filter(
        CodeFile.project_id == project_id
    ).all()

    return HTMLResponse(content=generate_html_documentation(db_project, entities), status_code=200)
