from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from . import Base, get_utc_timestamp
from sqlalchemy_utils import UUIDType
import uuid


class User(Base):
    __tablename__ = "users"

    id = Column(UUIDType(binary=False), primary_key=True, index=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user", nullable=False)
    register_timestamp = Column(Integer, nullable=False, default=get_utc_timestamp)

    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
