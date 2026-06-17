from sqlalchemy.orm import Session
from src.system.models import EntityType, Permission
from src.Iot.models import IMSStandardField, IMSStandardMethod


class EntityTypeDAO:
    @staticmethod
    def create(session: Session, **kwargs) -> EntityType:
        entity = EntityType(**kwargs)
        session.add(entity)
        session.flush()
        return entity

    @staticmethod
    def update(session: Session, entity: EntityType, **kwargs) -> EntityType:
        for key, value in kwargs.items():
            if hasattr(entity, key) and value is not None:
                setattr(entity, key, value)
        session.flush()
        return entity

    @staticmethod
    def delete(session: Session, entity: EntityType):
        session.delete(entity)
        session.flush()

    @staticmethod
    def get_by_id(session: Session, entity_id: str) -> EntityType:
        return session.query(EntityType).filter(EntityType.id == entity_id).first()

    @staticmethod
    def get_by_code(session: Session, type_code: str) -> EntityType:
        return session.query(EntityType).filter(EntityType.type_code == type_code).first()

    @staticmethod
    def get_all(session: Session, limit: int = 100, offset: int = 0):
        return session.query(EntityType).order_by(EntityType.hierarchy_level.asc()).offset(offset).limit(limit).all()

    @staticmethod
    def get_tree(session: Session):
        """获取层级树（自关联）"""
        all_types = session.query(EntityType).all()
        type_map = {t.id: t for t in all_types}
        roots = []
        for t in all_types:
            if t.parent_type_id and t.parent_type_id in type_map:
                parent = type_map[t.parent_type_id]
                if not hasattr(parent, 'children'):
                    parent.children = []
                parent.children.append(t)
            else:
                roots.append(t)
        return roots


class PermissionDAO:
    @staticmethod
    def create(session: Session, **kwargs) -> Permission:
        perm = Permission(**kwargs)
        session.add(perm)
        session.flush()
        return perm

    @staticmethod
    def update(session: Session, perm: Permission, **kwargs) -> Permission:
        for key, value in kwargs.items():
            if hasattr(perm, key) and value is not None:
                setattr(perm, key, value)
        session.flush()
        return perm

    @staticmethod
    def delete(session: Session, perm: Permission):
        session.delete(perm)
        session.flush()

    @staticmethod
    def get_by_id(session: Session, perm_id: str) -> Permission:
        return session.query(Permission).filter(Permission.id == perm_id).first()

    @staticmethod
    def get_by_code(session: Session, perm_code: str) -> Permission:
        return session.query(Permission).filter(Permission.perm_code == perm_code).first()

    @staticmethod
    def get_all(session: Session, limit: int = 100, offset: int = 0):
        return session.query(Permission).offset(offset).limit(limit).all()







# ==================== 标准字段 DAO ====================
class StandardFieldDAO:
    """标准字段表 CRUD"""

    @staticmethod
    def create(session: Session, **kwargs) -> IMSStandardField:
        field = IMSStandardField(**kwargs)
        session.add(field)
        session.flush()
        return field

    @staticmethod
    def update(session: Session, field: IMSStandardField, **kwargs) -> IMSStandardField:
        for key, value in kwargs.items():
            if hasattr(field, key) and value is not None:
                setattr(field, key, value)
        session.flush()
        return field

    @staticmethod
    def delete(session: Session, field: IMSStandardField):
        session.delete(field)
        session.flush()

    @staticmethod
    def get_by_id(session: Session, field_id: str) -> IMSStandardField | None:
        return session.query(IMSStandardField).filter(IMSStandardField.id == field_id).first()

    @staticmethod
    def get_by_code(session: Session, field_code: str) -> IMSStandardField | None:
        return session.query(IMSStandardField).filter(IMSStandardField.field_code == field_code).first()

    @staticmethod
    def get_all(session: Session, limit: int = 100, offset: int = 0):
        return session.query(IMSStandardField).offset(offset).limit(limit).all()

    @staticmethod
    def get_all_no_pagination(session: Session):
        return session.query(IMSStandardField).all()


# ==================== 标准方法 DAO ====================
class StandardMethodDAO:
    """标准方法表 CRUD"""

    @staticmethod
    def create(session: Session, **kwargs) -> IMSStandardMethod:
        method = IMSStandardMethod(**kwargs)
        session.add(method)
        session.flush()
        return method

    @staticmethod
    def update(session: Session, method: IMSStandardMethod, **kwargs) -> IMSStandardMethod:
        for key, value in kwargs.items():
            if hasattr(method, key) and value is not None:
                setattr(method, key, value)
        session.flush()
        return method

    @staticmethod
    def delete(session: Session, method: IMSStandardMethod):
        session.delete(method)
        session.flush()

    @staticmethod
    def get_by_id(session: Session, method_id: str) -> IMSStandardMethod | None:
        return session.query(IMSStandardMethod).filter(IMSStandardMethod.id == method_id).first()

    @staticmethod
    def get_by_code(session: Session, method_code: str) -> IMSStandardMethod | None:
        return session.query(IMSStandardMethod).filter(IMSStandardMethod.method_code == method_code).first()

    @staticmethod
    def get_all(session: Session, limit: int = 100, offset: int = 0):
        return session.query(IMSStandardMethod).offset(offset).limit(limit).all()

    @staticmethod
    def get_all_no_pagination(session: Session):
        return session.query(IMSStandardMethod).all()