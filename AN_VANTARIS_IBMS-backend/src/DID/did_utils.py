# src/DID/did_utils.py
"""
DID 工具类：生成、校验、解析符合 IMBS 规范的分布式标识符
格式示例：
    - 根级：did:imbs:system:root:a1b2c3d4e5f6
    - 子级：did:imbs:system:root:property:zhonghai:f1e2d3c4b5a6
规则：最后两段分别为实体类型和12位十六进制后缀
"""

import re
import uuid
from typing import Optional, List

DID_PREFIX = "did:imbs"

# 放宽正则：允许中间有任意段，最后两段必须是 [a-z_]+ 和 [a-f0-9]{12}
DID_PATTERN = re.compile(rf"^{DID_PREFIX}(:[a-z_]+)+:[a-f0-9]{{12}}$")


def generate_unique_suffix() -> str:
    """生成12位十六进制唯一后缀"""
    return uuid.uuid4().hex[:12]


def _clean_identifier(identifier: str) -> str:
    """
    清理标识符，只保留字母数字下划线连字符。
    若清理后为空，则使用8位随机串作为后备。
    """
    cleaned = re.sub(r"[^a-zA-Z0-9_-]", "", identifier.replace(" ", "_"))
    if not cleaned:
        cleaned = uuid.uuid4().hex[:8]
    return cleaned.lower()


def generate_did(entity_type: str, identifier: str) -> str:
    """
    生成根级 DID
    示例：generate_did("system", "root") -> did:imbs:system:root:a1b2c3d4e5f6
    """
    clean = _clean_identifier(identifier)
    return f"{DID_PREFIX}:{entity_type}:{clean}:{generate_unique_suffix()}"


def generate_child_did(parent_did: str, child_type: str, child_identifier: str) -> str:
    """
    基于父 DID 生成子 DID
    示例：generate_child_did("did:imbs:system:root:abc123", "property", "zhonghai")
          -> did:imbs:system:root:property:zhonghai:def456789012
    """
    if not parent_did.startswith(DID_PREFIX):
        raise ValueError("无效的父DID")

    parts = parent_did.split(":")
    # 移除末尾的后缀（12位十六进制）及前一段类型（如果符合规范）
    if len(parts) >= 3 and re.match(r"^[a-f0-9]{12}$", parts[-1]):
        base = ":".join(parts[:-1])  # 去掉后缀，保留到类型段
    else:
        base = parent_did  # 非标准格式，直接追加

    clean = _clean_identifier(child_identifier)
    return f"{base}:{child_type}:{clean}:{generate_unique_suffix()}"


def validate_did(did: str) -> bool:
    """校验 DID 格式是否正确"""
    return bool(DID_PATTERN.match(did))


def get_parent_did(did: str) -> Optional[str]:
    """
    获取父级 DID（去除最后两段：类型和后缀）
    例如：did:imbs:system:root:property:zhonghai:abc123 -> did:imbs:system:root
    """
    if not validate_did(did):
        return None
    parts = did.split(":")
    # 至少包含前缀(2段)+类型+标识+后缀 = 5段
    if len(parts) <= 5:
        return f"{DID_PREFIX}:system"  # 根级父为系统
    # 去掉最后两段（类型+后缀）
    return ":".join(parts[:-2])


def extract_entity_type(did: str) -> Optional[str]:
    """从 DID 中提取最末级实体类型（倒数第二段）"""
    if not validate_did(did):
        return None
    parts = did.split(":")
    return parts[-2] if len(parts) >= 2 else None


def extract_suffix(did: str) -> Optional[str]:
    """从 DID 中提取唯一后缀（最后一段）"""
    if not validate_did(did):
        return None
    return did.split(":")[-1]


def did_to_path(did: str) -> List[str]:
    """
    将 DID 解析为层级路径列表
    例如：did:imbs:system:root:property:zhonghai:abc123
          -> ['did:imbs', 'system', 'root', 'property', 'zhonghai', 'abc123']
    """
    return did.split(":")