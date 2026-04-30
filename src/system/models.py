# src/system/models.py
from sqlalchemy import text
from sqlalchemy.orm import declarative_base
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, SmallInteger
from src.common.core.database import db

from src.Iot.models import IMSStandardField, IMSStandardMethod

Base = declarative_base()

def generate_uuid() -> str:
    return uuid.uuid4().hex

class EntityType(Base):
    __tablename__ = 'imbs_entity_type'
    id = Column(String(32), primary_key=True, default=generate_uuid)
    type_code = Column(String(32), nullable=False, unique=True)
    type_name = Column(String(64), nullable=False)
    hierarchy_level = Column(SmallInteger, nullable=False)
    parent_type_id = Column(String(32), ForeignKey('imbs_entity_type.id'), nullable=True)
    created_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

class Permission(Base):
    __tablename__ = 'imbs_permission'
    id = Column(String(32), primary_key=True, default=generate_uuid)
    perm_code = Column(String(64), nullable=False, unique=True)
    description = Column(String(128), nullable=False)
    extra = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
