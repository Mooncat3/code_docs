from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from . import Base, get_utc_timestamp
from sqlalchemy_utils import UUIDType
import uuid


class CodeFile(Base):
    __tablename__ = "code_files"

    id = Column(UUIDType(binary=False), primary_key=True, index=True, default=uuid.uuid4)
    filename = Column(String)
    language = Column(String)
    original_content = Column(Text)
    modified_content = Column(Text, nullable=True, default=None)
    project_id = Column(UUIDType(binary=False), ForeignKey("projects.id"))
    modified_timestamp = Column(Integer, nullable=False, default=get_utc_timestamp)

    project = relationship("Project", back_populates="files")
    entities = relationship("CodeEntity", back_populates="file", cascade="all, delete-orphan")
