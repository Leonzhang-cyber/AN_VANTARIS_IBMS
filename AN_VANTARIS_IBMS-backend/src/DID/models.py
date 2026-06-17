# src/DID/models.py
import uuid
from sqlalchemy import Column, String, JSON, DateTime, SmallInteger, ForeignKey, Index, text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def generate_uuid() -> str:
    return uuid.uuid4().hex


class EntityType(Base):
    __tablename__ = 'imbs_entity_type'
    __table_args__ = (
        Index('idx_parent', 'parent_type_id'),
        {'comment': '实体类型字典表'}
    )

    id = Column(String(32), primary_key=True, default=generate_uuid)
    type_code = Column(String(32), nullable=False, unique=True)
    type_name = Column(String(64), nullable=False)
    hierarchy_level = Column(SmallInteger, nullable=False)
    parent_type_id = Column(String(32), ForeignKey('imbs_entity_type.id', ondelete='RESTRICT'), nullable=True)
    created_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    parent_type = relationship('EntityType', remote_side=[id], backref='children')


class Permission(Base):
    __tablename__ = 'imbs_permission'
    __table_args__ = {'comment': '权限定义表'}

    id = Column(String(32), primary_key=True, default=generate_uuid)
    perm_code = Column(String(64), nullable=False, unique=True)
    description = Column(String(128), nullable=False)
    extra = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))


class EntityRelationship(Base):
    __tablename__ = 'imbs_relationship'
    __table_args__ = (
        Index('idx_parent', 'parent_did'),
        Index('idx_child', 'child_did'),
        {'comment': '实体层级关系表'}
    )

    id = Column(String(32), primary_key=True, default=generate_uuid)
    parent_did = Column(String(128), nullable=False)
    child_did = Column(String(128), nullable=False)
    relation_type = Column(String(32), server_default=text("'direct'"))
    created_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))


class User(Base):
    __tablename__ = 'imbs_users'
    __table_args__ = (
        Index('idx_did', 'did'),
        Index('idx_type', 'entity_type_id'),
        {'comment': '统一用户/实体表'}
    )

    id = Column(String(32), primary_key=True, default=generate_uuid)
    username = Column(String(64), nullable=False, unique=True)
    password_hash = Column(String(128), nullable=False, server_default=text("''"))
    did = Column(String(128), nullable=False, unique=True)
    entity_type_id = Column(String(32), ForeignKey('imbs_entity_type.id'), nullable=False)
    name = Column(String(128), nullable=False)
    public_key = Column(String(130), nullable=False)
    permission_codes = Column(JSON, nullable=True)
    extra = Column(JSON, nullable=True)
    active = Column(SmallInteger, server_default=text('1'))
    created_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    tx_hash = Column(String(66), nullable=True, comment='注册/更新时的上链交易哈希')
    metadata_hash = Column(String(66), nullable=True, comment='实体元数据的SHA256哈希（链上锚定）')

    entity_type = relationship('EntityType', backref='users')


class VCAnchor(Base):
    __tablename__ = 'imbs_vc_anchor'
    __table_args__ = {'comment': 'VC链上锚定记录表'}

    id = Column(String(32), primary_key=True, default=generate_uuid)
    vc_id = Column(String(128), nullable=False, unique=True, comment='VC的唯一标识')
    vc_hash = Column(String(66), nullable=False, comment='VC完整JSON的SHA256哈希（0x开头）')
    issuer_did = Column(String(128), nullable=False, comment='签发者DID')
    subject_did = Column(String(128), nullable=False, comment='持有者DID')
    tx_hash = Column(String(66), nullable=False, comment='上链交易哈希')
    anchored_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='锚定时间')


class VCRevocation(Base):
    __tablename__ = 'imbs_vc_revocation'
    __table_args__ = {'comment': 'VC撤销记录表'}

    vc_id = Column(String(128), primary_key=True, comment='被撤销的VC ID')
    revoked_by_did = Column(String(128), nullable=False, comment='撤销操作者DID')
    tx_hash = Column(String(66), nullable=False, comment='撤销交易哈希')
    revoked_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='撤销时间')