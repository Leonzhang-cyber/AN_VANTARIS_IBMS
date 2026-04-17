# src/DID/dao.py
"""
DID 模块数据访问对象 (DAO)
提供对 imbs_entity_type, imbs_permission, imbs_relationship, imbs_users, imbs_vc_anchor, imbs_vc_revocation 的完整 CRUD 及高级查询
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from .models import EntityType, Permission, EntityRelationship, User, VCAnchor, VCRevocation


class VCAnchorDAO:
    """VC 链上锚定记录表 DAO"""
    def __init__(self, session: Session):
        self.session = session

    def create(self, vc_id: str, vc_hash: str, issuer_did: str, subject_did: str, tx_hash: str) -> VCAnchor:
        """创建 VC 锚定记录"""
        anchor = VCAnchor(
            vc_id=vc_id,
            vc_hash=vc_hash,
            issuer_did=issuer_did,
            subject_did=subject_did,
            tx_hash=tx_hash
        )
        self.session.add(anchor)
        self.session.commit()
        self.session.refresh(anchor)
        return anchor

    def get_by_vc_id(self, vc_id: str) -> Optional[VCAnchor]:
        """根据 VC ID 查询锚定记录"""
        return self.session.query(VCAnchor).filter_by(vc_id=vc_id).first()

    def get_by_issuer(self, issuer_did: str) -> List[VCAnchor]:
        """根据签发者 DID 查询"""
        return self.session.query(VCAnchor).filter_by(issuer_did=issuer_did).all()

    def get_by_subject(self, subject_did: str) -> List[VCAnchor]:
        """根据持有者 DID 查询"""
        return self.session.query(VCAnchor).filter_by(subject_did=subject_did).all()


class VCRevocationDAO:
    """VC 撤销记录表 DAO"""
    def __init__(self, session: Session):
        self.session = session

    def revoke(self, vc_id: str, revoked_by_did: str, tx_hash: str) -> VCRevocation:
        """撤销 VC，若已存在则覆盖（或忽略）"""
        existing = self.session.query(VCRevocation).filter_by(vc_id=vc_id).first()
        if existing:
            # 如果已存在，可选择更新或忽略，这里选择更新
            existing.revoked_by_did = revoked_by_did
            existing.tx_hash = tx_hash
            self.session.commit()
            return existing
        rev = VCRevocation(vc_id=vc_id, revoked_by_did=revoked_by_did, tx_hash=tx_hash)
        self.session.add(rev)
        self.session.commit()
        self.session.refresh(rev)
        return rev

    def is_revoked(self, vc_id: str) -> bool:
        """检查 VC 是否已被撤销"""
        return self.session.query(VCRevocation).filter_by(vc_id=vc_id).first() is not None

    def get_revocation_info(self, vc_id: str) -> Optional[VCRevocation]:
        """获取撤销详情"""
        return self.session.query(VCRevocation).filter_by(vc_id=vc_id).first()


class EntityTypeDAO:
    """实体类型字典表 DAO"""
    def __init__(self, session: Session):
        self.session = session

    # ---------- 增 ----------
    def create(self, type_code: str, type_name: str, hierarchy_level: int,
               parent_type_id: Optional[str] = None) -> EntityType:
        """创建新的实体类型"""
        entity_type = EntityType(
            type_code=type_code,
            type_name=type_name,
            hierarchy_level=hierarchy_level,
            parent_type_id=parent_type_id
        )
        self.session.add(entity_type)
        self.session.commit()
        self.session.refresh(entity_type)
        return entity_type

    # ---------- 删 ----------
    def delete(self, type_id: str) -> bool:
        """根据ID删除实体类型（物理删除）"""
        entity_type = self.get_by_id(type_id)
        if entity_type:
            self.session.delete(entity_type)
            self.session.commit()
            return True
        return False

    def delete_by_code(self, type_code: str) -> bool:
        """根据类型编码删除"""
        entity_type = self.get_by_code(type_code)
        if entity_type:
            self.session.delete(entity_type)
            self.session.commit()
            return True
        return False

    # ---------- 改 ----------
    def update(self, type_id: str, **kwargs) -> Optional[EntityType]:
        """更新实体类型字段"""
        entity_type = self.get_by_id(type_id)
        if entity_type:
            for k, v in kwargs.items():
                if hasattr(entity_type, k):
                    setattr(entity_type, k, v)
            self.session.commit()
            self.session.refresh(entity_type)
        return entity_type

    # ---------- 查 ----------
    def get_by_id(self, type_id: str) -> Optional[EntityType]:
        return self.session.query(EntityType).filter_by(id=type_id).first()

    def get_by_code(self, type_code: str) -> Optional[EntityType]:
        return self.session.query(EntityType).filter_by(type_code=type_code).first()

    def get_all(self) -> List[EntityType]:
        return self.session.query(EntityType).order_by(EntityType.hierarchy_level).all()

    def get_by_hierarchy_level(self, level: int) -> List[EntityType]:
        return self.session.query(EntityType).filter_by(hierarchy_level=level).all()

    def get_children_types(self, parent_type_id: str) -> List[EntityType]:
        """获取指定父类型下的所有子类型"""
        return self.session.query(EntityType).filter_by(parent_type_id=parent_type_id).all()

    def get_root_types(self) -> List[EntityType]:
        """获取根类型（无父类型）"""
        return self.session.query(EntityType).filter_by(parent_type_id=None).all()

    def exists_code(self, type_code: str) -> bool:
        return self.get_by_code(type_code) is not None


class PermissionDAO:
    """权限定义表 DAO"""
    def __init__(self, session: Session):
        self.session = session

    # ---------- 增 ----------
    def create(self, perm_code: str, description: str, extra: Optional[Dict] = None) -> Permission:
        permission = Permission(
            perm_code=perm_code,
            description=description,
            extra=extra
        )
        self.session.add(permission)
        self.session.commit()
        self.session.refresh(permission)
        return permission

    # ---------- 删 ----------
    def delete(self, perm_id: str) -> bool:
        perm = self.get_by_id(perm_id)
        if perm:
            self.session.delete(perm)
            self.session.commit()
            return True
        return False

    def delete_by_code(self, perm_code: str) -> bool:
        perm = self.get_by_code(perm_code)
        if perm:
            self.session.delete(perm)
            self.session.commit()
            return True
        return False

    # ---------- 改 ----------
    def update(self, perm_id: str, **kwargs) -> Optional[Permission]:
        perm = self.get_by_id(perm_id)
        if perm:
            for k, v in kwargs.items():
                if hasattr(perm, k):
                    setattr(perm, k, v)
            self.session.commit()
            self.session.refresh(perm)
        return perm

    # ---------- 查 ----------
    def get_by_id(self, perm_id: str) -> Optional[Permission]:
        return self.session.query(Permission).filter_by(id=perm_id).first()

    def get_by_code(self, perm_code: str) -> Optional[Permission]:
        return self.session.query(Permission).filter_by(perm_code=perm_code).first()

    def get_all(self) -> List[Permission]:
        return self.session.query(Permission).order_by(Permission.created_at.desc()).all()

    def get_by_codes(self, perm_codes: List[str]) -> List[Permission]:
        """根据权限编码列表批量查询"""
        return self.session.query(Permission).filter(Permission.perm_code.in_(perm_codes)).all()

    def search(self, keyword: str) -> List[Permission]:
        """根据编码或描述模糊搜索"""
        return self.session.query(Permission).filter(
            or_(
                Permission.perm_code.contains(keyword),
                Permission.description.contains(keyword)
            )
        ).all()

    def exists_code(self, perm_code: str) -> bool:
        return self.get_by_code(perm_code) is not None


class UserDAO:
    """统一用户/实体表 DAO"""
    def __init__(self, session: Session):
        self.session = session

    # ---------- 增 ----------
    def create(self, username: str, password_hash: str, did: str, entity_type_id: str,
               name: str, public_key: str, permission_codes: Optional[List[str]] = None,
               extra: Optional[Dict] = None, tx_hash: str = "", metadata_hash: str = "") -> User:
        user = User(
            username=username,
            password_hash=password_hash,
            did=did,
            entity_type_id=entity_type_id,
            name=name,
            public_key=public_key,
            permission_codes=permission_codes,
            extra=extra,
            tx_hash=tx_hash,
            metadata_hash=metadata_hash,
            active=1
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    # ---------- 删 ----------
    def delete(self, user_id: str) -> bool:
        """物理删除（慎用）"""
        user = self.get_by_id(user_id)
        if user:
            self.session.delete(user)
            self.session.commit()
            return True
        return False

    def soft_delete(self, did: str) -> bool:
        """软删除：设置 active=0"""
        user = self.get_by_did(did)
        if user:
            user.active = 0
            self.session.commit()
            return True
        return False

    def restore(self, did: str) -> bool:
        """恢复软删除：设置 active=1"""
        user = self.get_by_did(did)
        if user:
            user.active = 1
            self.session.commit()
            return True
        return False

    # ---------- 改 ----------
    def update(self, did: str, **kwargs) -> Optional[User]:
        user = self.get_by_did(did)
        if user:
            for k, v in kwargs.items():
                if hasattr(user, k):
                    setattr(user, k, v)
            self.session.commit()
            self.session.refresh(user)
        return user

    def update_permissions(self, did: str, permission_codes: List[str]) -> Optional[User]:
        """快捷更新权限列表"""
        return self.update(did, permission_codes=permission_codes)

    # ---------- 查 ----------
    def get_by_id(self, user_id: str) -> Optional[User]:
        return self.session.query(User).filter_by(id=user_id).first()

    def get_by_did(self, did: str) -> Optional[User]:
        return self.session.query(User).filter_by(did=did).first()

    def get_by_username(self, username: str) -> Optional[User]:
        return self.session.query(User).filter_by(username=username).first()

    def get_by_public_key(self, public_key: str) -> Optional[User]:
        return self.session.query(User).filter_by(public_key=public_key).first()

    def get_by_type(self, type_code: str) -> List[User]:
        return self.session.query(User).join(EntityType).filter(
            EntityType.type_code == type_code,
            User.active == 1
        ).all()

    def get_all_active(self) -> List[User]:
        return self.session.query(User).filter_by(active=1).all()

    def get_all(self, include_inactive: bool = False) -> List[User]:
        """获取所有用户（可选包含禁用）"""
        q = self.session.query(User)
        if not include_inactive:
            q = q.filter_by(active=1)
        return q.all()

    def search_by_name(self, keyword: str) -> List[User]:
        """根据名称模糊搜索"""
        return self.session.query(User).filter(
            User.name.contains(keyword),
            User.active == 1
        ).all()

    def get_with_permission(self, perm_code: str) -> List[User]:
        """查询拥有指定权限的所有实体（利用 JSON 数组查询，适用于 MySQL 5.7+）"""
        return self.session.query(User).filter(
            func.json_contains(User.permission_codes, f'"{perm_code}"'),
            User.active == 1
        ).all()

    def count_by_type(self, type_code: str) -> int:
        """统计某类型实体数量"""
        return self.session.query(User).join(EntityType).filter(
            EntityType.type_code == type_code,
            User.active == 1
        ).count()

    def exists_did(self, did: str) -> bool:
        return self.get_by_did(did) is not None

    def exists_username(self, username: str) -> bool:
        return self.get_by_username(username) is not None

    def exists_public_key(self, public_key: str) -> bool:
        return self.get_by_public_key(public_key) is not None

    def paginate(self, page: int = 1, per_page: int = 20, **filters) -> List[User]:
        """分页查询，支持简单过滤条件"""
        q = self.session.query(User)
        for attr, value in filters.items():
            if hasattr(User, attr):
                q = q.filter(getattr(User, attr) == value)
        return q.offset((page - 1) * per_page).limit(per_page).all()


class RelationshipDAO:
    """实体层级关系表 DAO"""
    def __init__(self, session: Session):
        self.session = session

    # ---------- 增 ----------
    def add_relation(self, parent_did: str, child_did: str, relation_type: str = 'direct') -> bool:
        """添加父子关系，若已存在则忽略"""
        existing = self.session.query(EntityRelationship).filter_by(
            parent_did=parent_did, child_did=child_did
        ).first()
        if not existing:
            rel = EntityRelationship(
                parent_did=parent_did,
                child_did=child_did,
                relation_type=relation_type
            )
            self.session.add(rel)
            self.session.commit()
            return True
        return False

    # ---------- 删 ----------
    def remove_relation(self, parent_did: str, child_did: str) -> bool:
        """删除指定父子关系"""
        rel = self.session.query(EntityRelationship).filter_by(
            parent_did=parent_did, child_did=child_did
        ).first()
        if rel:
            self.session.delete(rel)
            self.session.commit()
            return True
        return False

    def remove_all_relations_for_did(self, did: str) -> int:
        """删除所有以该 DID 为父或子的关系"""
        count = self.session.query(EntityRelationship).filter(
            or_(
                EntityRelationship.parent_did == did,
                EntityRelationship.child_did == did
            )
        ).delete(synchronize_session=False)
        self.session.commit()
        return count

    # ---------- 查 ----------
    def get_children(self, parent_did: str) -> List[str]:
        """获取直接子 DID 列表"""
        rels = self.session.query(EntityRelationship).filter_by(parent_did=parent_did).all()
        return [r.child_did for r in rels]

    def get_parents(self, child_did: str) -> List[str]:
        """获取直接父 DID 列表"""
        rels = self.session.query(EntityRelationship).filter_by(child_did=child_did).all()
        return [r.parent_did for r in rels]

    def get_all_descendants(self, root_did: str) -> List[str]:
        """递归获取所有后代 DID（深度优先）"""
        result = []
        children = self.get_children(root_did)
        for child in children:
            result.append(child)
            result.extend(self.get_all_descendants(child))
        return result

    def get_all_ancestors(self, did: str) -> List[str]:
        """递归获取所有祖先 DID"""
        result = []
        parents = self.get_parents(did)
        for parent in parents:
            result.append(parent)
            result.extend(self.get_all_ancestors(parent))
        return result

    def is_descendant(self, ancestor_did: str, descendant_did: str) -> bool:
        """判断 descendant_did 是否为 ancestor_did 的后代"""
        descendants = self.get_all_descendants(ancestor_did)
        return descendant_did in descendants

    def get_relation_tree(self, root_did: str) -> Dict[str, Any]:
        """获取以 root_did 为根的完整关系树（嵌套字典）"""
        def build_tree(did):
            children = self.get_children(did)
            return {
                "did": did,
                "children": [build_tree(child) for child in children]
            }
        return build_tree(root_did)

    def count_children(self, parent_did: str) -> int:
        """统计直接子节点数量"""
        return self.session.query(EntityRelationship).filter_by(parent_did=parent_did).count()

    def relation_exists(self, parent_did: str, child_did: str) -> bool:
        """检查关系是否存在"""
        return self.session.query(EntityRelationship).filter_by(
            parent_did=parent_did, child_did=child_did
        ).first() is not None