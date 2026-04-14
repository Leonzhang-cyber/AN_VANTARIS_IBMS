# src/models/did_models.py
from src.core.database import db
from datetime import datetime


# ======================
# 表 1: DIDDocument（DID 文档表）
# 作用：存储系统中所有 DID（去中心化标识符）的基本信息和元数据。
# 每个 DID 对应一条记录，包括其类型、公钥、颁发者、扩展属性等。
# ======================
class DIDDocument(db.Model):
    __tablename__ = 'did_documents'  # 数据库中的表名

    # 主键，自增大整数 ID
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    # 去中心化标识符（DID），全局唯一，例如：did:ibms:employee:abc123
    did = db.Column(db.String(255), unique=True, nullable=False)

    # DID 的类型，用于区分不同角色或用途
    # 可选值：
    #   - 'root': 根机构（如平台超级管理员）
    #   - 'property': 物业公司
    #   - 'client': 客户（业主/住户）
    #   - 'temporary': 临时人员（如访客、施工人员）
    #   - 'employee': 员工（如保安、保洁）
    #   - 'device': 物联网设备（如传感器、摄像头、执行器）
    #   - 'area': 区域/空间（如小区、楼栋、楼层、房间）
    # did_type = db.Column(db.Enum('root', 'property', 'client', 'temporary', 'employee'), nullable=False)
    did_type = db.Column(
        db.Enum('root', 'property', 'client', 'temporary', 'employee', 'device', 'area', name='did_type_enum'),
        nullable=False)

    # 该 DID 对应的公钥（用于验证签名），通常为 JWK 或 PEM 格式字符串
    public_key = db.Column(db.Text, nullable=False)

    # 颁发该 DID 的上级 DID（issuer），例如员工 DID 的 issuer 是物业公司 DID
    # root 类型的 DID 此字段可为空
    issuer_did = db.Column(db.String(255), nullable=True)

    # 扩展元数据字段，以 JSON 格式存储业务相关属性
    # 示例（员工）：
    #   {"name": "张三", "phone": "13800138000", "position": "保安队长"}
    # 示例（物业）：
    #   {"company_name": "XX物业", "license_no": "ABC123"}
    # 该字段灵活支持不同 DID 类型的个性化信息
    extra_metadata = db.Column(db.JSON, nullable=True)  # 原 metadata 改为 extra_metadata

    # 记录创建时间，自动设置为当前 UTC 时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 记录最后更新时间，每次更新时自动刷新为当前 UTC 时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ======================
# 表 2: VCCredential（可验证凭证表）
# 作用：存储颁发给某个 DID 的权限凭证（Verifiable Credential, VC）。
# 每条记录代表一个有效的权限证明，包含前端/API 权限列表和有效期。
# ======================
class VCCredential(db.Model):
    __tablename__ = 'vc_credentials'  # 数据库中的表名

    # 主键，自增大整数 ID
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    # 凭证唯一标识符（VC ID），全局唯一，符合 W3C VC 规范
    vc_id = db.Column(db.String(255), unique=True, nullable=False)

    # 颁发该凭证的 DID（issuer），通常是上级机构（如物业公司）
    issuer_did = db.Column(db.String(255), nullable=False)

    # 凭证持有者的 DID（subject），即被授权人
    subject_did = db.Column(db.String(255), nullable=False)

    # 前端权限列表，JSON 数组，控制用户在前端可访问的页面或功能模块
    # 示例：["property_dashboard", "device_management"]
    frontend_permissions = db.Column(db.JSON, nullable=False)

    # API 权限列表，JSON 数组，控制用户可调用的后端接口
    # 示例：["GET /api/devices/*", "POST /api/alarms"]
    api_permissions = db.Column(db.JSON, nullable=False)

    # 凭证生效开始时间（UTC）
    valid_from = db.Column(db.DateTime, nullable=False)

    # 凭证失效时间（UTC），超过此时间凭证无效
    valid_until = db.Column(db.DateTime, nullable=False)

    # 是否已被撤销（软删除机制）
    revoked = db.Column(db.Boolean, default=False)

    # 撤销时间（仅当 revoked=True 时有效）
    revoked_at = db.Column(db.DateTime, nullable=True)

    # 完整的 VC JSON 内容（符合 W3C Verifiable Credentials 标准）
    # 用于审计、验证或未来兼容标准 VC 解析器
    vc_json = db.Column(db.JSON, nullable=False)

    # 凭证创建时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ======================
# 表 3: PermissionDefinition（权限定义表）
# 作用：集中管理系统中所有合法的权限项定义，作为权限分配的“白名单”。
# 防止随意分配不存在或拼写错误的权限。
# ======================
class PermissionDefinition(db.Model):
    __tablename__ = 'permission_definitions'  # 数据库中的表名

    # 主键，自增大整数 ID
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    # 权限类型：
    #   - 'frontend': 前端页面/组件级权限
    #   - 'api': 后端接口级权限
    perm_type = db.Column(db.Enum('frontend', 'api'), nullable=False)

    # 权限代码（唯一标识），例如：
    #   - frontend: "property_dashboard"
    #   - api: "/api/devices/*"
    code = db.Column(db.String(255), nullable=False)

    # HTTP 方法（仅对 API 权限有意义），例如：GET, POST, PUT, DELETE
    # 前端权限此字段可为空
    method = db.Column(db.String(10), nullable=True)

    # 权限描述，便于管理员理解用途
    # 示例："查看设备列表", "添加报警规则"
    description = db.Column(db.String(255), nullable=True)

    # 权限定义创建时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 联合唯一约束：确保 (perm_type, code, method) 组合全局唯一
    # 例如：不能有两个相同的 "GET /api/devices/*" API 权限定义
    __table_args__ = (db.UniqueConstraint('perm_type', 'code', 'method', name='uk_type_code'),)