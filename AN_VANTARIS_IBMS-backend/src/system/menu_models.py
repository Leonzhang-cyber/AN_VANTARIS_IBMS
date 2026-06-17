# src/system/menu_models.py
from sqlalchemy import text, Column, String, DateTime, Integer, Boolean, ForeignKey, SmallInteger, BigInteger
from sqlalchemy.orm import declarative_base, relationship
from src.common.core.database import db
import uuid
from datetime import datetime

Base = declarative_base()


# ==================== 版本模型 ====================
class SysVersion(Base):
    """系统版本表"""
    __tablename__ = 'sys_version'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='主键ID')
    version_code = Column(String(50), nullable=False, unique=True, comment='版本代码')
    version_name = Column(String(100), nullable=False, comment='版本名称')
    description = Column(String(500), nullable=True, comment='版本描述')
    icon = Column(String(50), nullable=True, comment='版本图标')
    sort_order = Column(Integer, default=0, comment='排序顺序')
    is_active = Column(SmallInteger, default=1, comment='是否启用: 0-禁用, 1-启用')
    is_default = Column(SmallInteger, default=0, comment='是否默认版本: 0-否, 1-是')
    created_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
    updated_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
                        comment='更新时间')


# ==================== 菜单模型 ====================
class SysMenu(Base):
    """菜单表"""
    __tablename__ = 'sys_menu'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='主键ID')
    parent_id = Column(BigInteger, default=0, comment='父菜单ID，0表示顶级菜单')
    menu_path = Column(String(200), nullable=False, unique=True, comment='菜单路径/唯一标识')
    menu_title = Column(String(100), nullable=False, comment='菜单标题')
    menu_icon = Column(String(50), nullable=True, comment='图标名称')
    menu_type = Column(String(20), default='menu', comment='菜单类型: menu-可点击跳转, container-仅作为容器不可点击')
    has_children = Column(SmallInteger, default=0, comment='是否有子菜单: 0-无, 1-有')
    redirect_path = Column(String(200), nullable=True, comment='重定向路径')
    sort_order = Column(Integer, default=0, comment='排序顺序')
    is_visible = Column(SmallInteger, default=1, comment='全局是否可见: 0-隐藏, 1-显示')
    remark = Column(String(255), nullable=True, comment='备注说明')
    created_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
    updated_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
                        comment='更新时间')

    # 注意：这里不定义 relationship 自关联，避免 ORM 映射问题
    # 如果需要父子关系，在 Service 层手动处理


# ==================== 版本菜单关联模型 ====================
class SysVersionMenu(Base):
    """版本菜单关联表"""
    __tablename__ = 'sys_version_menu'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='主键ID')
    version_code = Column(String(50), nullable=False, comment='版本代码')
    menu_id = Column(BigInteger, nullable=False, comment='菜单ID')
    menu_path = Column(String(200), nullable=False, comment='菜单路径（冗余字段）')
    is_visible = Column(SmallInteger, default=1, comment='该版本下此菜单是否可见: 0-隐藏, 1-显示')
    sort_order = Column(Integer, nullable=True, comment='该版本下的排序')
    created_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
    updated_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'),
                        comment='更新时间')