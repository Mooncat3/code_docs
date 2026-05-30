from sqlalchemy import Column, String, Boolean, ForeignKey, Integer
from sqlalchemy.orm import relationship
from . import Base, get_utc_timestamp
from sqlalchemy_utils import UUIDType
import uuid


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUIDType(binary=False), primary_key=True, index=True, default=uuid.uuid4)
    title = Column(String, index=True)
    description = Column(String)
    is_public = Column(Boolean, default=False)
    owner_id = Column(UUIDType(binary=False), ForeignKey("users.id"))
    created_timestamp = Column(Integer, nullable=False, default=get_utc_timestamp)

    owner = relationship("User", back_populates="projects")
    files = relationship("CodeFile", back_populates="project", cascade="all, delete-orphan")
