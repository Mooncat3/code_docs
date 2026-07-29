from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from . import Base, get_utc_timestamp
from sqlalchemy_utils import UUIDType
import uuid


class CodeEntity(Base):
    __tablename__ = "code_entities"

    id = Column(UUIDType(binary=False), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String)
    type = Column(String)
    line_start = Column(Integer)
    line_end = Column(Integer)
    original_docs = Column(Text)
    modified_docs = Column(Text)
    file_id = Column(UUIDType(binary=False), ForeignKey("code_files.id"))
    modified_timestamp = Column(Integer, nullable=False, default=get_utc_timestamp)
    visibility = Column(Boolean, default=True)

    file = relationship("CodeFile", back_populates="entities")
