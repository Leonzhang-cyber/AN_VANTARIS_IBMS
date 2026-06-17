# src/Iot/models.py
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, Integer, Enum, ForeignKey, SmallInteger, Boolean, DECIMAL
from sqlalchemy.dialects.mysql import CHAR, VARCHAR, TINYINT
from sqlalchemy.orm import relationship
from src.common.core.database import db


def generate_uuid():
    return uuid.uuid4().hex


class IMSDevice(db.Model):
    """设备表"""
    __tablename__ = 'imbs_device'

    id = Column(CHAR(32), primary_key=True, default=generate_uuid)
    device_name = Column(VARCHAR(128), nullable=False, comment='设备名称')
    device_code = Column(VARCHAR(64), nullable=False, unique=True, comment='设备编号')
    did = Column(VARCHAR(128), nullable=False, unique=True, index=True, comment='设备DID')
    public_key = Column(VARCHAR(130), nullable=False, comment='设备公钥')
    private_key = Column(VARCHAR(66), nullable=False, comment='设备私钥')
    vc_json = Column(JSON, nullable=False, comment='设备VC')
    parent_did = Column(VARCHAR(128), nullable=True, index=True, comment='父设备DID')
    protocol = Column(VARCHAR(32), nullable=False, comment='通讯协议')
    connect_config = Column(JSON, nullable=True, comment='连接参数')
    status = Column(SmallInteger, default=1, comment='0离线/1在线/2异常')
    extra = Column(JSON, nullable=True, comment='扩展字段')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')


class IMSStandardField(db.Model):
    """标准字段字典表"""
    __tablename__ = 'imbs_standard_field'

    id = Column(CHAR(32), primary_key=True, default=generate_uuid)
    field_code = Column(VARCHAR(64), nullable=False, unique=True, comment='标准字段编码')
    field_name = Column(VARCHAR(128), nullable=False, comment='标准字段名称')
    field_type = Column(VARCHAR(32), nullable=False, comment='字段类型（float/int/string/bool/json）')
    unit = Column(VARCHAR(32), nullable=True, comment='单位（如 ℃、%、m/s）')
    description = Column(VARCHAR(256), nullable=True, comment='字段描述')
    min_value = Column(DECIMAL(20, 6), nullable=True, comment='最小值')
    max_value = Column(DECIMAL(20, 6), nullable=True, comment='最大值')
    is_critical = Column(Boolean, default=False, comment='是否为关键数据（需要上链）')
    extra = Column(JSON, nullable=True, comment='扩展字段')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')


class IMSFieldMapping(db.Model):
    """字段映射表"""
    __tablename__ = 'imbs_field_mapping'

    id = Column(CHAR(32), primary_key=True, default=generate_uuid)
    did = Column(VARCHAR(128), nullable=False, index=True, comment='设备DID（*表示全局）')
    protocol = Column(VARCHAR(32), nullable=False, index=True, comment='协议')
    raw_field = Column(VARCHAR(64), nullable=False, comment='原始字段名')
    standard_field = Column(VARCHAR(64), nullable=False, comment='标准字段名')
    standard_field_id = Column(CHAR(32), ForeignKey('imbs_standard_field.id'), nullable=True, comment='标准字段ID')
    transform = Column(VARCHAR(32), nullable=True, comment='转换规则')
    extra = Column(JSON, nullable=True, comment='扩展字段')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')

    # 关系
    standard_field_ref = relationship('IMSStandardField', backref='mappings')


class IMSMethodMapping(db.Model):
    """方法映射表"""
    __tablename__ = 'imbs_method_mapping'

    id = Column(CHAR(32), primary_key=True, default=generate_uuid)
    did = Column(VARCHAR(128), nullable=False, index=True, comment='设备DID（*表示全局）')
    protocol = Column(VARCHAR(32), nullable=False, index=True, comment='协议')
    direction = Column(Enum('uplink', 'downlink'), nullable=False, comment='方向')
    raw_path = Column(VARCHAR(255), nullable=False, comment='原始路径/Topic')
    standard_method = Column(VARCHAR(64), nullable=False, comment='标准方法名')
    extra = Column(JSON, nullable=True, comment='扩展字段')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')


class IMSStandardMethod(db.Model):
    """标准方法字典表"""
    __tablename__ = 'imbs_standard_method'

    id = Column(CHAR(32), primary_key=True, default=generate_uuid)
    method_code = Column(VARCHAR(64), nullable=False, unique=True, comment='方法编码')
    method_name = Column(VARCHAR(128), nullable=False, comment='方法名称')
    description = Column(VARCHAR(256), nullable=True, comment='方法描述')
    category = Column(VARCHAR(32), nullable=True, comment='分类(control/query/config)')
    params_schema = Column(JSON, nullable=True, comment='参数JSON Schema定义')
    response_schema = Column(JSON, nullable=True, comment='响应JSON Schema定义')
    is_active = Column(Boolean, default=True, comment='是否启用')
    extra = Column(JSON, nullable=True, comment='扩展字段')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')