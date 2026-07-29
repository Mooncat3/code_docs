from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from app.schemas.project import Project, ProjectOwner


class CodeFileBase(BaseModel):
    filename: str
    language: Optional[str] = None


class CodeFileCreate(CodeFileBase):
    content: str


class CodeFileClean(CodeFileBase):
    id: UUID
    project_id: UUID
    project: ProjectOwner
    modified_timestamp: int

    class Config:
        from_attributes = True


class CodeFile(CodeFileBase):
    id: UUID
    project_id: UUID
    project: Project
    original_content: str
    modified_content: Optional[str] = None
    modified_timestamp: int

    class Config:
        from_attributes = True
