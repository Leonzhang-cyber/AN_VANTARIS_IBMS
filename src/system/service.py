from sqlalchemy.orm import Session

from src.system.dao import EntityTypeDAO, PermissionDAO, StandardFieldDAO, StandardMethodDAO
from src.system.exceptions import PermissionDenied, NotFoundError, DuplicateError
from src.system.models import EntityType, Permission, IMSStandardField, IMSStandardMethod


class SystemService:
    def __init__(self, session: Session):
        self.session = session

    # ---------- 实体类型管理 ----------
    def create_entity_type(self, type_code: str, type_name: str, hierarchy_level: int,
                           parent_type_id: str = None) -> EntityType:
        # 检查code唯一性
        if EntityTypeDAO.get_by_code(self.session, type_code):
            raise DuplicateError(f"Entity type code '{type_code}' already exists")
        return EntityTypeDAO.create(self.session, type_code=type_code, type_name=type_name,
                                    hierarchy_level=hierarchy_level, parent_type_id=parent_type_id)

    def update_entity_type(self, type_id: str, **kwargs) -> EntityType:
        entity = EntityTypeDAO.get_by_id(self.session, type_id)
        if not entity:
            raise NotFoundError(f"Entity type id '{type_id}' not found")
        # 如果修改type_code, 需检查唯一性
        if 'type_code' in kwargs and kwargs['type_code'] != entity.type_code:
            if EntityTypeDAO.get_by_code(self.session, kwargs['type_code']):
                raise DuplicateError(f"Entity type code '{kwargs['type_code']}' already exists")
        return EntityTypeDAO.update(self.session, entity, **kwargs)

    def delete_entity_type(self, type_id: str):
        entity = EntityTypeDAO.get_by_id(self.session, type_id)
        if not entity:
            raise NotFoundError(f"Entity type id '{type_id}' not found")
        # 检查是否被其他类型或用户引用（可通过关联表检查，简化版暂略）
        EntityTypeDAO.delete(self.session, entity)

    def get_entity_type(self, type_id: str) -> EntityType:
        entity = EntityTypeDAO.get_by_id(self.session, type_id)
        if not entity:
            raise NotFoundError(f"Entity type id '{type_id}' not found")
        return entity

    def list_entity_types(self, limit: int = 100, offset: int = 0):
        return EntityTypeDAO.get_all(self.session, limit, offset)

    def get_entity_type_tree(self):
        return EntityTypeDAO.get_tree(self.session)

    # ---------- 权限管理 ----------
    def create_permission(self, perm_code: str, description: str, extra: dict = None) -> Permission:
        if PermissionDAO.get_by_code(self.session, perm_code):
            raise DuplicateError(f"Permission code '{perm_code}' already exists")
        return PermissionDAO.create(self.session, perm_code=perm_code,
                                    description=description, extra=extra)

    def update_permission(self, perm_id: str, **kwargs) -> Permission:
        perm = PermissionDAO.get_by_id(self.session, perm_id)
        if not perm:
            raise NotFoundError(f"Permission id '{perm_id}' not found")
        if 'perm_code' in kwargs and kwargs['perm_code'] != perm.perm_code:
            if PermissionDAO.get_by_code(self.session, kwargs['perm_code']):
                raise DuplicateError(f"Permission code '{kwargs['perm_code']}' already exists")
        return PermissionDAO.update(self.session, perm, **kwargs)

    def delete_permission(self, perm_id: str):
        perm = PermissionDAO.get_by_id(self.session, perm_id)
        if not perm:
            raise NotFoundError(f"Permission id '{perm_id}' not found")
        PermissionDAO.delete(self.session, perm)

    def get_permission(self, perm_id: str) -> Permission:
        perm = PermissionDAO.get_by_id(self.session, perm_id)
        if not perm:
            raise NotFoundError(f"Permission id '{perm_id}' not found")
        return perm

    def list_permissions(self, limit: int = 100, offset: int = 0):
        return PermissionDAO.get_all(self.session, limit, offset)

    # ---------- 标准字段管理 ----------
    def create_standard_field(self, **kwargs) -> IMSStandardField:
        """创建标准字段"""
        if 'field_code' in kwargs and StandardFieldDAO.get_by_code(self.session, kwargs['field_code']):
            raise DuplicateError(f"Field code '{kwargs['field_code']}' already exists")
        return StandardFieldDAO.create(self.session, **kwargs)

    def update_standard_field(self, field_id: str, **kwargs) -> IMSStandardField:
        field = StandardFieldDAO.get_by_id(self.session, field_id)
        if not field:
            raise NotFoundError(f"Standard field id '{field_id}' not found")
        if 'field_code' in kwargs and kwargs['field_code'] != field.field_code:
            if StandardFieldDAO.get_by_code(self.session, kwargs['field_code']):
                raise DuplicateError(f"Field code '{kwargs['field_code']}' already exists")
        return StandardFieldDAO.update(self.session, field, **kwargs)

    def delete_standard_field(self, field_id: str):
        field = StandardFieldDAO.get_by_id(self.session, field_id)
        if not field:
            raise NotFoundError(f"Standard field id '{field_id}' not found")
        StandardFieldDAO.delete(self.session, field)

    def get_standard_field(self, field_id: str) -> IMSStandardField:
        field = StandardFieldDAO.get_by_id(self.session, field_id)
        if not field:
            raise NotFoundError(f"Standard field id '{field_id}' not found")
        return field

    def list_standard_fields(self, limit: int = 100, offset: int = 0):
        return StandardFieldDAO.get_all(self.session, limit, offset)

    # ---------- 标准方法管理 ----------
    def create_standard_method(self, **kwargs) -> IMSStandardMethod:
        """创建标准方法"""
        if 'method_code' in kwargs and StandardMethodDAO.get_by_code(self.session, kwargs['method_code']):
            raise DuplicateError(f"Method code '{kwargs['method_code']}' already exists")
        return StandardMethodDAO.create(self.session, **kwargs)

    def update_standard_method(self, method_id: str, **kwargs) -> IMSStandardMethod:
        method = StandardMethodDAO.get_by_id(self.session, method_id)
        if not method:
            raise NotFoundError(f"Standard method id '{method_id}' not found")
        if 'method_code' in kwargs and kwargs['method_code'] != method.method_code:
            if StandardMethodDAO.get_by_code(self.session, kwargs['method_code']):
                raise DuplicateError(f"Method code '{kwargs['method_code']}' already exists")
        return StandardMethodDAO.update(self.session, method, **kwargs)

    def delete_standard_method(self, method_id: str):
        method = StandardMethodDAO.get_by_id(self.session, method_id)
        if not method:
            raise NotFoundError(f"Standard method id '{method_id}' not found")
        StandardMethodDAO.delete(self.session, method)

    def get_standard_method(self, method_id: str) -> IMSStandardMethod:
        method = StandardMethodDAO.get_by_id(self.session, method_id)
        if not method:
            raise NotFoundError(f"Standard method id '{method_id}' not found")
        return method

    def list_standard_methods(self, limit: int = 100, offset: int = 0):
        return StandardMethodDAO.get_all(self.session, limit, offset)