# src/api/system/system_api.py

from flask import Blueprint, request, jsonify, g, current_app
from src.common.core.database import db
from src.system.service import SystemService
from src.common.utils.jwt_util import jwt_required, get_current_did
from src.system.exceptions import NotFoundError, DuplicateError
from src.common.models.response import Result
from src.api import api_bp

# ==================== 实体类型管理 ====================

@api_bp.route('/system/entity-types', methods=['POST'])
@jwt_required
def create_entity_type():
    """创建实体类型"""
    data = request.json
    required = ['type_code', 'type_name', 'hierarchy_level']
    if not all(k in data for k in required):
        return Result.error('MISSING_FIELDS', 'type_code, type_name, hierarchy_level required', 400)

    service = SystemService(db.session)
    try:
        entity = service.create_entity_type(
            type_code=data['type_code'],
            type_name=data['type_name'],
            hierarchy_level=data['hierarchy_level'],
            parent_type_id=data.get('parent_type_id')
        )
        db.session.commit()
        return Result.success({
            'id': entity.id,
            'type_code': entity.type_code,
            'type_name': entity.type_name,
            'hierarchy_level': entity.hierarchy_level,
            'parent_type_id': entity.parent_type_id,
            'created_at': entity.created_at.isoformat() if entity.created_at else None
        })
    except DuplicateError as e:
        db.session.rollback()
        return Result.error('DUPLICATE', str(e), 409)
    except Exception as e:
        db.session.rollback()
        return Result.error('INTERNAL_ERROR', str(e), 500)


@api_bp.route('/system/entity-types/<type_id>', methods=['PUT'])
@jwt_required
def update_entity_type(type_id):
    """更新实体类型"""
    data = request.json
    service = SystemService(db.session)
    try:
        entity = service.update_entity_type(type_id, **data)
        db.session.commit()
        return Result.success({
            'id': entity.id,
            'type_code': entity.type_code,
            'type_name': entity.type_name,
            'hierarchy_level': entity.hierarchy_level,
            'parent_type_id': entity.parent_type_id
        })
    except NotFoundError as e:
        db.session.rollback()
        return Result.error('NOT_FOUND', str(e), 404)
    except DuplicateError as e:
        db.session.rollback()
        return Result.error('DUPLICATE', str(e), 409)
    except Exception as e:
        db.session.rollback()
        return Result.error('INTERNAL_ERROR', str(e), 500)


@api_bp.route('/system/entity-types/<type_id>', methods=['DELETE'])
@jwt_required
def delete_entity_type(type_id):
    """删除实体类型"""
    service = SystemService(db.session)
    try:
        service.delete_entity_type(type_id)
        db.session.commit()
        return Result.success(None, 'Deleted')
    except NotFoundError as e:
        db.session.rollback()
        return Result.error('NOT_FOUND', str(e), 404)
    except Exception as e:
        db.session.rollback()
        return Result.error('INTERNAL_ERROR', str(e), 500)


@api_bp.route('/system/entity-types/<type_id>', methods=['GET'])
@jwt_required
def get_entity_type(type_id):
    """查询单个实体类型"""
    service = SystemService(db.session)
    try:
        entity = service.get_entity_type(type_id)
        return Result.success({
            'id': entity.id,
            'type_code': entity.type_code,
            'type_name': entity.type_name,
            'hierarchy_level': entity.hierarchy_level,
            'parent_type_id': entity.parent_type_id,
            'created_at': entity.created_at.isoformat() if entity.created_at else None
        })
    except NotFoundError as e:
        return Result.error('NOT_FOUND', str(e), 404)


@api_bp.route('/system/entity-types', methods=['GET'])
@jwt_required
def list_entity_types():
    """分页查询实体类型列表"""
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))
    service = SystemService(db.session)
    entities = service.list_entity_types(limit, offset)
    return Result.success([{
        'id': e.id,
        'type_code': e.type_code,
        'type_name': e.type_name,
        'hierarchy_level': e.hierarchy_level,
        'parent_type_id': e.parent_type_id
    } for e in entities])


@api_bp.route('/system/entity-types/tree', methods=['GET'])
@jwt_required
def get_entity_type_tree():
    """获取实体类型树（层级结构）"""
    service = SystemService(db.session)
    tree = service.get_entity_type_tree()

    def serialize(node):
        return {
            'id': node.id,
            'type_code': node.type_code,
            'type_name': node.type_name,
            'hierarchy_level': node.hierarchy_level,
            'parent_type_id': node.parent_type_id,
            'children': [serialize(c) for c in getattr(node, 'children', [])]
        }

    return Result.success([serialize(root) for root in tree])


# ==================== 权限管理 ====================

@api_bp.route('/system/permissions', methods=['POST'])
@jwt_required
def create_permission():
    """创建权限"""
    data = request.json
    if not data.get('perm_code') or not data.get('description'):
        return Result.error('MISSING_FIELDS', 'perm_code and description are required', 400)

    service = SystemService(db.session)
    try:
        perm = service.create_permission(
            perm_code=data['perm_code'],
            description=data['description'],
            extra=data.get('extra')
        )
        db.session.commit()
        return Result.success({
            'id': perm.id,
            'perm_code': perm.perm_code,
            'description': perm.description,
            'extra': perm.extra,
            'created_at': perm.created_at.isoformat() if perm.created_at else None
        })
    except DuplicateError as e:
        db.session.rollback()
        return Result.error('DUPLICATE', str(e), 409)
    except Exception as e:
        db.session.rollback()
        return Result.error('INTERNAL_ERROR', str(e), 500)


@api_bp.route('/system/permissions/<perm_id>', methods=['PUT'])
@jwt_required
def update_permission(perm_id):
    """更新权限"""
    data = request.json
    service = SystemService(db.session)
    try:
        perm = service.update_permission(perm_id, **data)
        db.session.commit()
        return Result.success({
            'id': perm.id,
            'perm_code': perm.perm_code,
            'description': perm.description,
            'extra': perm.extra
        })
    except NotFoundError as e:
        db.session.rollback()
        return Result.error('NOT_FOUND', str(e), 404)
    except DuplicateError as e:
        db.session.rollback()
        return Result.error('DUPLICATE', str(e), 409)
    except Exception as e:
        db.session.rollback()
        return Result.error('INTERNAL_ERROR', str(e), 500)


@api_bp.route('/system/permissions/<perm_id>', methods=['DELETE'])
@jwt_required
def delete_permission(perm_id):
    """删除权限"""
    service = SystemService(db.session)
    try:
        service.delete_permission(perm_id)
        db.session.commit()
        return Result.success(None, 'Deleted')
    except NotFoundError as e:
        db.session.rollback()
        return Result.error('NOT_FOUND', str(e), 404)
    except Exception as e:
        db.session.rollback()
        return Result.error('INTERNAL_ERROR', str(e), 500)


@api_bp.route('/system/permissions/<perm_id>', methods=['GET'])
@jwt_required
def get_permission(perm_id):
    """查询单个权限"""
    service = SystemService(db.session)
    try:
        perm = service.get_permission(perm_id)
        return Result.success({
            'id': perm.id,
            'perm_code': perm.perm_code,
            'description': perm.description,
            'extra': perm.extra,
            'created_at': perm.created_at.isoformat() if perm.created_at else None
        })
    except NotFoundError as e:
        return Result.error('NOT_FOUND', str(e), 404)


@api_bp.route('/system/permissions', methods=['GET'])
@jwt_required
def list_permissions():
    """分页查询权限列表"""
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))
    try:
        service = SystemService(db.session)
        perms = service.list_permissions(limit, offset)
        return Result.success([{
            'id': p.id,
            'perm_code': p.perm_code,
            'description': p.description,
            'extra': p.extra
        } for p in perms])
    except Exception as e:
        current_app.logger.warning("list_permissions failed: %s", type(e).__name__)
        return Result.error(code=500, message="Failed to load permissions")



# ==================== 标准字段管理 ====================

@api_bp.route('/system/create-standard-fields', methods=['POST'])
@jwt_required
def sys_create_standard_field():
    """创建标准字段"""
    data = request.json
    required = ['field_code', 'field_name', 'field_type']
    if not all(k in data for k in required):
        return Result.error('MISSING_FIELDS', 'field_code, field_name, field_type required', 400)

    service = SystemService(db.session)
    try:
        field = service.create_standard_field(**data)
        db.session.commit()
        return Result.success({
            'id': field.id,
            'field_code': field.field_code,
            'field_name': field.field_name,
            'field_type': field.field_type,
            'unit': field.unit,
            'description': field.description,
            'min_value': float(field.min_value) if field.min_value else None,
            'max_value': float(field.max_value) if field.max_value else None,
            'is_critical': field.is_critical,
            'extra': field.extra,
            'created_at': field.created_at.isoformat() if field.created_at else None,
            'updated_at': field.updated_at.isoformat() if field.updated_at else None
        })
    except DuplicateError as e:
        db.session.rollback()
        return Result.error('DUPLICATE', str(e), 409)
    except Exception as e:
        db.session.rollback()
        return Result.error('INTERNAL_ERROR', str(e), 500)


@api_bp.route('/system/update-standard-fields/<field_id>', methods=['PUT'])
@jwt_required
def sys_update_standard_field(field_id):
    """更新标准字段"""
    data = request.json
    service = SystemService(db.session)
    try:
        field = service.update_standard_field(field_id, **data)
        db.session.commit()
        return Result.success({
            'id': field.id,
            'field_code': field.field_code,
            'field_name': field.field_name,
            'field_type': field.field_type,
            'unit': field.unit,
            'description': field.description,
            'min_value': float(field.min_value) if field.min_value else None,
            'max_value': float(field.max_value) if field.max_value else None,
            'is_critical': field.is_critical,
            'extra': field.extra,
            'updated_at': field.updated_at.isoformat() if field.updated_at else None
        })
    except NotFoundError as e:
        db.session.rollback()
        return Result.error('NOT_FOUND', str(e), 404)
    except DuplicateError as e:
        db.session.rollback()
        return Result.error('DUPLICATE', str(e), 409)
    except Exception as e:
        db.session.rollback()
        return Result.error('INTERNAL_ERROR', str(e), 500)


@api_bp.route('/system/delete-standard-fields/<field_id>', methods=['DELETE'])
@jwt_required
def sys_delete_standard_field(field_id):
    """删除标准字段"""
    service = SystemService(db.session)
    try:
        service.delete_standard_field(field_id)
        db.session.commit()
        return Result.success(None, 'Deleted')
    except NotFoundError as e:
        db.session.rollback()
        return Result.error('NOT_FOUND', str(e), 404)
    except Exception as e:
        db.session.rollback()
        return Result.error('INTERNAL_ERROR', str(e), 500)


@api_bp.route('/system/getById-standard-fields/<field_id>', methods=['GET'])
@jwt_required
def sys_get_standard_field(field_id):
    """查询单个标准字段"""
    service = SystemService(db.session)
    try:
        field = service.get_standard_field(field_id)
        return Result.success({
            'id': field.id,
            'field_code': field.field_code,
            'field_name': field.field_name,
            'field_type': field.field_type,
            'unit': field.unit,
            'description': field.description,
            'min_value': float(field.min_value) if field.min_value else None,
            'max_value': float(field.max_value) if field.max_value else None,
            'is_critical': field.is_critical,
            'extra': field.extra,
            'created_at': field.created_at.isoformat() if field.created_at else None,
            'updated_at': field.updated_at.isoformat() if field.updated_at else None
        })
    except NotFoundError as e:
        return Result.error('NOT_FOUND', str(e), 404)


@api_bp.route('/system/list-standard-fields', methods=['GET'])
@jwt_required
def sys_list_standard_fields():
    """分页查询标准字段列表"""
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))
    service = SystemService(db.session)
    fields = service.list_standard_fields(limit, offset)
    return Result.success([{
        'id': f.id,
        'field_code': f.field_code,
        'field_name': f.field_name,
        'field_type': f.field_type,
        'unit': f.unit,
        'description': f.description,
        'min_value': float(f.min_value) if f.min_value else None,
        'max_value': float(f.max_value) if f.max_value else None,
        'is_critical': f.is_critical,
        'extra': f.extra,
        'created_at': f.created_at.isoformat() if f.created_at else None,
        'updated_at': f.updated_at.isoformat() if f.updated_at else None
    } for f in fields])


# ==================== 标准方法管理 ====================

@api_bp.route('/system/create-standard-methods', methods=['POST'])
@jwt_required
def sys_create_standard_method():
    """创建标准方法"""
    data = request.json
    if not data.get('method_code') or not data.get('method_name'):
        return Result.error('MISSING_FIELDS', 'method_code and method_name are required', 400)

    service = SystemService(db.session)
    try:
        method = service.create_standard_method(**data)
        db.session.commit()
        return Result.success({
            'id': method.id,
            'method_code': method.method_code,
            'method_name': method.method_name,
            'description': method.description,
            'category': method.category,
            'params_schema': method.params_schema,
            'response_schema': method.response_schema,
            'is_active': method.is_active,
            'extra': method.extra,
            'created_at': method.created_at.isoformat() if method.created_at else None,
            'updated_at': method.updated_at.isoformat() if method.updated_at else None
        })
    except DuplicateError as e:
        db.session.rollback()
        return Result.error('DUPLICATE', str(e), 409)
    except Exception as e:
        db.session.rollback()
        return Result.error('INTERNAL_ERROR', str(e), 500)


@api_bp.route('/system/update-standard-methods/<method_id>', methods=['PUT'])
@jwt_required
def sys_update_standard_method(method_id):
    """更新标准方法"""
    data = request.json
    service = SystemService(db.session)
    try:
        method = service.update_standard_method(method_id, **data)
        db.session.commit()
        return Result.success({
            'id': method.id,
            'method_code': method.method_code,
            'method_name': method.method_name,
            'description': method.description,
            'category': method.category,
            'params_schema': method.params_schema,
            'response_schema': method.response_schema,
            'is_active': method.is_active,
            'extra': method.extra,
            'updated_at': method.updated_at.isoformat() if method.updated_at else None
        })
    except NotFoundError as e:
        db.session.rollback()
        return Result.error('NOT_FOUND', str(e), 404)
    except DuplicateError as e:
        db.session.rollback()
        return Result.error('DUPLICATE', str(e), 409)
    except Exception as e:
        db.session.rollback()
        return Result.error('INTERNAL_ERROR', str(e), 500)


@api_bp.route('/system/delete-standard-methods/<method_id>', methods=['DELETE'])
@jwt_required
def sys_delete_standard_method(method_id):
    """删除标准方法"""
    service = SystemService(db.session)
    try:
        service.delete_standard_method(method_id)
        db.session.commit()
        return Result.success(None, 'Deleted')
    except NotFoundError as e:
        db.session.rollback()
        return Result.error('NOT_FOUND', str(e), 404)
    except Exception as e:
        db.session.rollback()
        return Result.error('INTERNAL_ERROR', str(e), 500)


@api_bp.route('/system/getById-standard-methods/<method_id>', methods=['GET'])
@jwt_required
def sys_get_standard_method(method_id):
    """查询单个标准方法"""
    service = SystemService(db.session)
    try:
        method = service.get_standard_method(method_id)
        return Result.success({
            'id': method.id,
            'method_code': method.method_code,
            'method_name': method.method_name,
            'description': method.description,
            'category': method.category,
            'params_schema': method.params_schema,
            'response_schema': method.response_schema,
            'is_active': method.is_active,
            'extra': method.extra,
            'created_at': method.created_at.isoformat() if method.created_at else None,
            'updated_at': method.updated_at.isoformat() if method.updated_at else None
        })
    except NotFoundError as e:
        return Result.error('NOT_FOUND', str(e), 404)


@api_bp.route('/system/list-standard-methods', methods=['GET'])
@jwt_required
def sys_list_standard_methods():
    """分页查询标准方法列表"""
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))
    service = SystemService(db.session)
    methods = service.list_standard_methods(limit, offset)
    return Result.success([{
        'id': m.id,
        'method_code': m.method_code,
        'method_name': m.method_name,
        'description': m.description,
        'category': m.category,
        'params_schema': m.params_schema,
        'response_schema': m.response_schema,
        'is_active': m.is_active,
        'extra': m.extra,
        'created_at': m.created_at.isoformat() if m.created_at else None,
        'updated_at': m.updated_at.isoformat() if m.updated_at else None
    } for m in methods])