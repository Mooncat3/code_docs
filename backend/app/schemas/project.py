from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from app.schemas.user import User, UserOwner


class ProjectBase(BaseModel):
    title: str = Field(..., max_length=256, min_length=1)
    description: Optional[str] = Field(default=None, max_length=2**18)
    is_public: bool = False


class ProjectCreate(ProjectBase):
    pass


class ProjectOwner(BaseModel):
    owner: UserOwner


class ProjectUpdate(BaseModel):
    description: Optional[str] = Field(default=None, max_length=2**18)
    title: Optional[str] = Field(default=None, max_length=256, min_length=1)
    is_public: Optional[bool] = None


class Project(ProjectBase):
    id: UUID
    owner: User

    class Config:
        from_attributes = True


class ProjectsSearch(BaseModel):
    projects: List[Project]
    total_count: int
