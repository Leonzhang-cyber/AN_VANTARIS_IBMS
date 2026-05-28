# src/api/system/menu_api.py

from flask import Blueprint, request
from src.common.core.database import db
from src.system.menu_service import MenuService
from src.common.models.response import Result
from src.api import api_bp


@api_bp.route('/system/test', methods=['GET'])
def test():
    return Result.success({'status': 'ok'})


# ==================== Version Management ====================
@api_bp.route('/system/versions', methods=['GET'])
def list_versions():
    try:
        from sqlalchemy import text
        result = db.session.execute(text("SELECT * FROM sys_version ORDER BY sort_order"))
        rows = result.fetchall()
        versions = [{
            'id': row[0], 'version_code': row[1], 'version_name': row[2],
            'description': row[3], 'icon': row[4], 'sort_order': row[5],
            'is_active': row[6] == 1, 'is_default': row[7] == 1
        } for row in rows]
        return Result.success(versions)
    except Exception as e:
        return Result.error(code=500, message=str(e))


@api_bp.route('/system/versions/default', methods=['GET'])
def get_default_version():
    try:
        from sqlalchemy import text
        row = db.session.execute(text("SELECT * FROM sys_version WHERE is_default = 1 LIMIT 1")).fetchone()
        if not row:
            return Result.error('NOT_FOUND', 'Default version not found', 404)
        return Result.success({
            'id': row[0], 'version_code': row[1], 'version_name': row[2],
            'description': row[3], 'icon': row[4], 'sort_order': row[5],
            'is_active': row[6] == 1, 'is_default': row[7] == 1
        })
    except Exception as e:
        return Result.error(code=500, message=str(e))


@api_bp.route('/system/versions', methods=['POST'])
def create_version():
    data = request.json
    if not data.get('version_code') or not data.get('version_name'):
        return Result.error('MISSING_FIELDS', 'version_code and version_name are required', 400)
    try:
        from sqlalchemy import text
        check = db.session.execute(
            text("SELECT id FROM sys_version WHERE version_code = :code"),
            {"code": data['version_code']}
        ).fetchone()
        if check:
            return Result.error('DUPLICATE', f"Version code {data['version_code']} already exists", 409)
        db.session.execute(
            text("""
                INSERT INTO sys_version (version_code, version_name, description, icon, sort_order, is_active, is_default)
                VALUES (:version_code, :version_name, :description, :icon, :sort_order, :is_active, :is_default)
            """),
            {
                "version_code": data['version_code'],
                "version_name": data['version_name'],
                "description": data.get('description'),
                "icon": data.get('icon'),
                "sort_order": data.get('sort_order', 0),
                "is_active": 1 if data.get('is_active', True) else 0,
                "is_default": 1 if data.get('is_default', False) else 0
            }
        )
        db.session.commit()
        return Result.success({
            'version_code': data['version_code'], 'version_name': data['version_name'],
            'description': data.get('description'), 'icon': data.get('icon'),
            'sort_order': data.get('sort_order', 0),
            'is_active': data.get('is_active', True), 'is_default': data.get('is_default', False)
        })
    except Exception as e:
        db.session.rollback()
        return Result.error(code=500, message=str(e))


@api_bp.route('/system/versions/<version_code>', methods=['PUT'])
def update_version(version_code):
    data = request.json
    try:
        from sqlalchemy import text
        check = db.session.execute(
            text("SELECT id FROM sys_version WHERE version_code = :code"),
            {"code": version_code}
        ).fetchone()
        if not check:
            return Result.error('NOT_FOUND', f"Version {version_code} not found", 404)
        update_fields = []
        params = {"version_code": version_code}
        if 'version_name' in data:
            update_fields.append("version_name = :version_name")
            params["version_name"] = data['version_name']
        if 'description' in data:
            update_fields.append("description = :description")
            params["description"] = data['description']
        if 'icon' in data:
            update_fields.append("icon = :icon")
            params["icon"] = data['icon']
        if 'sort_order' in data:
            update_fields.append("sort_order = :sort_order")
            params["sort_order"] = data['sort_order']
        if 'is_active' in data:
            update_fields.append("is_active = :is_active")
            params["is_active"] = 1 if data['is_active'] else 0
        if 'is_default' in data:
            update_fields.append("is_default = :is_default")
            params["is_default"] = 1 if data['is_default'] else 0
        if update_fields:
            query = f"UPDATE sys_version SET {', '.join(update_fields)} WHERE version_code = :version_code"
            db.session.execute(text(query), params)
            db.session.commit()
        return Result.success(message="Update successful")
    except Exception as e:
        db.session.rollback()
        return Result.error(code=500, message=str(e))


@api_bp.route('/system/versions/<version_code>', methods=['DELETE'])
def delete_version(version_code):
    try:
        from sqlalchemy import text
        check = db.session.execute(
            text("SELECT id FROM sys_version WHERE version_code = :code"),
            {"code": version_code}
        ).fetchone()
        if not check:
            return Result.error('NOT_FOUND', f"Version {version_code} not found", 404)
        db.session.execute(text("DELETE FROM sys_version WHERE version_code = :code"), {"code": version_code})
        db.session.commit()
        return Result.success(None, 'Deleted')
    except Exception as e:
        db.session.rollback()
        return Result.error(code=500, message=str(e))


# ==================== Menu Config Interface ====================
@api_bp.route('/system/menu/config/<version_code>', methods=['GET'])
def get_menu_config(version_code):
    try:
        service = MenuService()
        result = service.get_version_menu_config(db.session, version_code)
        return Result.success(result)
    except Exception as e:
        return Result.error(code=500, message=str(e))


@api_bp.route('/system/menu/active', methods=['GET'])
def get_active_version_menu_config():
    try:
        service = MenuService()
        result = service.get_active_version_menu_config(db.session)
        if not result:
            return Result.error('NOT_FOUND', 'No active version found', 404)
        return Result.success(result)
    except Exception as e:
        return Result.error(code=500, message=str(e))


@api_bp.route('/system/versions/switch/<version_code>', methods=['PUT'])
def switch_active_version(version_code):
    try:
        service = MenuService()
        result = service.switch_active_version(db.session, version_code)
        if not result:
            return Result.error('NOT_FOUND', f'Version {version_code} not found', 404)
        db.session.commit()
        return Result.success(result)
    except Exception as e:
        db.session.rollback()
        return Result.error(code=500, message=str(e))


# ==================== Menu Management ====================
@api_bp.route('/system/menus', methods=['GET'])
def get_menu_tree():
    try:
        service = MenuService()
        tree = service.get_menu_tree(db.session)
        return Result.success(tree)
    except Exception as e:
        return Result.error(code=500, message=str(e))


@api_bp.route('/system/menus-add', methods=['POST'])
def create_menu():
    data = request.json
    if not data.get('menu_path') or not data.get('menu_title'):
        return Result.error('MISSING_FIELDS', 'menu_path and menu_title are required', 400)
    try:
        from sqlalchemy import text
        existing = db.session.execute(
            text("SELECT id FROM sys_menu WHERE menu_path = :path"),
            {"path": data['menu_path']}
        ).fetchone()
        if existing:
            return Result.error('DUPLICATE', f"Menu path {data['menu_path']} already exists", 409)
        db.session.execute(
            text("""
                INSERT INTO sys_menu (parent_id, menu_path, menu_title, menu_icon, menu_type, has_children, redirect_path, sort_order, is_visible)
                VALUES (:parent_id, :menu_path, :menu_title, :menu_icon, :menu_type, :has_children, :redirect_path, :sort_order, :is_visible)
            """),
            {
                "parent_id": data.get('parent_id', 0),
                "menu_path": data['menu_path'],
                "menu_title": data['menu_title'],
                "menu_icon": data.get('menu_icon'),
                "menu_type": data.get('menu_type', 'menu'),
                "has_children": 1 if data.get('has_children', False) else 0,
                "redirect_path": data.get('redirect_path'),
                "sort_order": data.get('sort_order', 0),
                "is_visible": 1 if data.get('is_visible', True) else 0
            }
        )
        db.session.commit()
        new_id = db.session.execute(
            text("SELECT id FROM sys_menu WHERE menu_path = :path"),
            {"path": data['menu_path']}
        ).fetchone()[0]
        return Result.success({'id': new_id, **data})
    except Exception as e:
        db.session.rollback()
        return Result.error(code=500, message=str(e))


@api_bp.route('/system/menus-update/<int:menu_id>', methods=['PUT'])
def update_menu(menu_id):
    data = request.json
    try:
        from sqlalchemy import text
        check = db.session.execute(
            text("SELECT id FROM sys_menu WHERE id = :id"),
            {"id": menu_id}
        ).fetchone()
        if not check:
            return Result.error('NOT_FOUND', f'Menu {menu_id} not found', 404)
        update_fields = []
        params = {"id": menu_id}
        if 'parent_id' in data:
            update_fields.append("parent_id = :parent_id")
            params["parent_id"] = data['parent_id']
        if 'menu_title' in data:
            update_fields.append("menu_title = :menu_title")
            params["menu_title"] = data['menu_title']
        if 'menu_icon' in data:
            update_fields.append("menu_icon = :menu_icon")
            params["menu_icon"] = data['menu_icon']
        if 'menu_type' in data:
            update_fields.append("menu_type = :menu_type")
            params["menu_type"] = data['menu_type']
        if 'has_children' in data:
            update_fields.append("has_children = :has_children")
            params["has_children"] = 1 if data['has_children'] else 0
        if 'redirect_path' in data:
            update_fields.append("redirect_path = :redirect_path")
            params["redirect_path"] = data['redirect_path']
        if 'sort_order' in data:
            update_fields.append("sort_order = :sort_order")
            params["sort_order"] = data['sort_order']
        if 'is_visible' in data:
            update_fields.append("is_visible = :is_visible")
            params["is_visible"] = 1 if data['is_visible'] else 0
        if update_fields:
            query = f"UPDATE sys_menu SET {', '.join(update_fields)} WHERE id = :id"
            db.session.execute(text(query), params)
            db.session.commit()
        return Result.success(message="Update successful")
    except Exception as e:
        db.session.rollback()
        return Result.error(code=500, message=str(e))


@api_bp.route('/system/menus-delete/<int:menu_id>', methods=['DELETE'])
def delete_menu(menu_id):
    try:
        from sqlalchemy import text
        check = db.session.execute(
            text("SELECT id FROM sys_menu WHERE id = :id"),
            {"id": menu_id}
        ).fetchone()
        if not check:
            return Result.error('NOT_FOUND', f'Menu {menu_id} not found', 404)
        db.session.execute(text("DELETE FROM sys_menu WHERE parent_id = :parent_id"), {"parent_id": menu_id})
        db.session.execute(text("DELETE FROM sys_menu WHERE id = :id"), {"id": menu_id})
        db.session.commit()
        return Result.success(None, 'Deleted')
    except Exception as e:
        db.session.rollback()
        return Result.error(code=500, message=str(e))


# ==================== Menu Sort ====================
# ==================== Menu Sort ====================
@api_bp.route('/system/menus/batch-sort', methods=['POST'])
def batch_update_menu_sort():
    data = request.json
    menus = data.get('menus', [])

    print(data)

    print(f"收到排序数据: {menus}")
    if not menus:
        return Result.error('INVALID_REQUEST', 'menus is required', 400)
    try:
        from sqlalchemy import text
        updated_count = 0
        for menu in menus:
            # 支持两种格式：menu_id 或 menu_path
            menu_id = menu.get('id')
            menu_path = menu.get('menu_path')
            sort_order = menu.get('sort_order')

            # 如果没有提供 id，通过 menu_path 查询
            if menu_id is None and menu_path is not None:
                result = db.session.execute(
                    text("SELECT id FROM sys_menu WHERE menu_path = :path"),
                    {"path": menu_path}
                ).fetchone()
                if result:
                    menu_id = result[0]
                    print(f"通过路径 {menu_path} 找到菜单 ID: {menu_id}")

            if menu_id is not None and sort_order is not None:
                db.session.execute(
                    text("UPDATE sys_menu SET sort_order = :sort_order WHERE id = :id"),
                    {"id": menu_id, "sort_order": sort_order}
                )
                updated_count += 1
                print(f"更新菜单 {menu_id} 排序为 {sort_order}")
        db.session.commit()
        return Result.success({'updated_count': updated_count}, 'Sort order updated successfully')
    except Exception as e:
        db.session.rollback()
        return Result.error(code=500, message=str(e))


# ==================== Version Menu Config ====================
@api_bp.route('/system/version-menus/<version_code>', methods=['GET'])
def get_version_menus(version_code):
    try:
        service = MenuService()
        result = service.get_version_with_menus(db.session, version_code)
        if not result:
            return Result.error('NOT_FOUND', f'Version {version_code} not found', 404)
        return Result.success(result)
    except Exception as e:
        return Result.error(code=500, message=str(e))


@api_bp.route('/system/version-menus/<version_code>/batch', methods=['POST'])
def batch_update_version_menus(version_code):
    data = request.json
    menus = data.get('menus', [])
    if not menus:
        return Result.error('INVALID_REQUEST', 'menus is required', 400)
    try:
        from sqlalchemy import text
        version = db.session.execute(
            text("SELECT version_code FROM sys_version WHERE version_code = :code"),
            {"code": version_code}
        ).fetchone()
        if not version:
            return Result.error('NOT_FOUND', f'Version {version_code} not found', 404)
        count = 0
        for menu_config in menus:
            menu_path = menu_config.get('menu_path')
            is_visible = menu_config.get('is_visible', True)
            sort_order = menu_config.get('sort_order')
            if menu_path:
                menu = db.session.execute(
                    text("SELECT id FROM sys_menu WHERE menu_path = :path"),
                    {"path": menu_path}
                ).fetchone()
                if menu:
                    db.session.execute(
                        text("""
                            INSERT INTO sys_version_menu (version_code, menu_id, menu_path, is_visible, sort_order)
                            VALUES (:version_code, :menu_id, :menu_path, :is_visible, :sort_order)
                            ON DUPLICATE KEY UPDATE is_visible = :is_visible, sort_order = :sort_order
                        """),
                        {
                            "version_code": version_code,
                            "menu_id": menu[0],
                            "menu_path": menu_path,
                            "is_visible": 1 if is_visible else 0,
                            "sort_order": sort_order
                        }
                    )
                    count += 1
        db.session.commit()
        return Result.success({'updated_count': count}, 'Batch update successful')
    except Exception as e:
        db.session.rollback()
        return Result.error(code=500, message=str(e))


# ==================== Incremental Update Version Menu ====================

@api_bp.route('/system/version-menus/<version_code>/incremental',methods=['POST'])
def incremental_update_version_menus(version_code):
    """
    增量更新版本菜单配置（只更新变化的菜单）
    请求体格式: {
        "add": ["/menu/path/1", "/menu/path/2"],      # 新增勾选的菜单
        "remove": ["/menu/path/3", "/menu/path/4"]    # 取消勾选的菜单
    }
    """
    data = request.json
    add_list = data.get('add', [])
    remove_list = data.get('remove', [])

    if not add_list and not remove_list:
        return Result.error('INVALID_REQUEST', 'add or remove list is required', 400)

    try:
        from sqlalchemy import text

        # 检查版本是否存在
        version = db.session.execute(
            text("SELECT version_code FROM sys_version WHERE version_code = :code"),
            {"code": version_code}
        ).fetchone()

        if not version:
            return Result.error('NOT_FOUND', f'Version {version_code} not found', 404)

        added_count = 0
        removed_count = 0

        # 处理新增勾选的菜单
        for menu_path in add_list:
            menu = db.session.execute(
                text("SELECT id, menu_path FROM sys_menu WHERE menu_path = :path"),
                {"path": menu_path}
            ).fetchone()

            if menu:
                db.session.execute(
                    text("""
                         INSERT INTO sys_version_menu (version_code, menu_id, menu_path, is_visible)
                         VALUES (:version_code, :menu_id, :menu_path, 1) ON DUPLICATE KEY
                         UPDATE is_visible = 1
                         """),
                    {
                        "version_code": version_code,
                        "menu_id": menu[0],
                        "menu_path": menu[1]
                    }
                )
                added_count += 1

        # 处理取消勾选的菜单
        for menu_path in remove_list:
            menu = db.session.execute(
                text("SELECT id, menu_path FROM sys_menu WHERE menu_path = :path"),
                {"path": menu_path}
            ).fetchone()

            if menu:
                db.session.execute(
                    text("""
                         UPDATE sys_version_menu
                         SET is_visible = 0
                         WHERE version_code = :version_code
                           AND menu_id = :menu_id
                         """),
                    {
                        "version_code": version_code,
                        "menu_id": menu[0]
                    }
                )
                removed_count += 1

        db.session.commit()

        return Result.success({
            'added': added_count,
            'removed': removed_count,
            'message': f'Updated {added_count} menus added, {removed_count} menus removed'
        }, 'Incremental update successful')

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return Result.error(code=500, message=str(e))


@api_bp.route('/system/version-menus/<version_code>/diff', methods=['POST'])
def diff_update_version_menus(version_code):
    """
    差异更新版本菜单配置（只提交变化前后的差异）
    请求体格式: {
        "changes": [
            {"menu_path": "/home/system-overview", "is_visible": true},
            {"menu_path": "/home/kpi-dashboard", "is_visible": false}
        ]
    }
    """
    data = request.json
    changes = data.get('changes', [])

    if not changes:
        return Result.error('INVALID_REQUEST', 'changes list is required', 400)

    try:
        from sqlalchemy import text

        version = db.session.execute(
            text("SELECT version_code FROM sys_version WHERE version_code = :code"),
            {"code": version_code}
        ).fetchone()

        if not version:
            return Result.error('NOT_FOUND', f'Version {version_code} not found', 404)

        updated_count = 0
        for change in changes:
            menu_path = change.get('menu_path')
            is_visible = change.get('is_visible', True)

            if not menu_path:
                continue

            menu = db.session.execute(
                text("SELECT id, menu_path FROM sys_menu WHERE menu_path = :path"),
                {"path": menu_path}
            ).fetchone()

            if menu:
                db.session.execute(
                    text("""
                         INSERT INTO sys_version_menu (version_code, menu_id, menu_path, is_visible)
                         VALUES (:version_code, :menu_id, :menu_path, :is_visible) ON DUPLICATE KEY
                         UPDATE is_visible = :is_visible
                         """),
                    {
                        "version_code": version_code,
                        "menu_id": menu[0],
                        "menu_path": menu[1],
                        "is_visible": 1 if is_visible else 0
                    }
                )
                updated_count += 1

        db.session.commit()
        return Result.success({'updated_count': updated_count}, 'Diff update successful')

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return Result.error(code=500, message=str(e))