from pydantic import BaseModel, Field
from typing import Optional
from app.schemas.file import CodeFileClean
from uuid import UUID


class CodeEntityBase(BaseModel):
    name: str
    type: str
    line_start: int
    line_end: int


class CodeEntityCreate(CodeEntityBase):
    original_docs: Optional[str] = None


class CodeEntityUpdate(BaseModel):
    docs: Optional[str] = Field(default=None, max_length=2**16)
    visibility: Optional[bool] = None


class CodeEntity(CodeEntityBase):
    id: UUID
    file_id: UUID
    original_docs: Optional[str] = None
    modified_docs: Optional[str] = None
    modified_timestamp: int
    file: CodeFileClean
    visibility: bool

    class Config:
        from_attributes = True
