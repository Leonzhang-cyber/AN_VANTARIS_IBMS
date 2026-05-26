# src/api/system/menu_api.py
from flask import Blueprint, request, jsonify, g
from src.common.core.database import db
from src.system.menu_service import MenuService
from src.common.utils.jwt_util import jwt_required
from src.system.exceptions import NotFoundError, DuplicateError
from src.common.models.response import Result
from src.api import api_bp


# ==================== Test Interface ====================
@api_bp.route('/system/test', methods=['GET'])
def test():
    """Simple test interface"""
    return Result.success({'status': 'ok'})


# ==================== Version Management ====================
@api_bp.route('/system/versions', methods=['GET'])
def list_versions():
    """Get all versions"""
    import traceback
    try:
        from sqlalchemy import text
        result = db.session.execute(text("SELECT * FROM sys_version ORDER BY sort_order"))
        rows = result.fetchall()

        versions = []
        for row in rows:
            versions.append({
                'id': row[0],
                'version_code': row[1],
                'version_name': row[2],
                'description': row[3],
                'icon': row[4],
                'sort_order': row[5],
                'is_active': row[6] == 1,
                'is_default': row[7] == 1,
            })

        return Result.success(versions)
    except Exception as e:
        print("=" * 50)
        print("ERROR in list_versions:")
        traceback.print_exc()
        print("=" * 50)
        return Result.error(code=500, message=str(e))


@api_bp.route('/system/versions/default', methods=['GET'])
def get_default_version():
    """Get default version"""
    try:
        from sqlalchemy import text
        result = db.session.execute(text("SELECT * FROM sys_version WHERE is_default = 1 LIMIT 1"))
        row = result.fetchone()

        if not row:
            return Result.error('NOT_FOUND', 'Default version not found', 404)

        return Result.success({
            'id': row[0],
            'version_code': row[1],
            'version_name': row[2],
            'description': row[3],
            'icon': row[4],
            'sort_order': row[5],
            'is_active': row[6] == 1,
            'is_default': row[7] == 1,
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Result.error(code=500, message=str(e))


@api_bp.route('/system/versions', methods=['POST'])
def create_version():
    """Create version"""
    import traceback
    data = request.json
    required = ['version_code', 'version_name']
    if not all(k in data for k in required):
        return Result.error('MISSING_FIELDS', 'version_code and version_name are required', 400)

    try:
        from sqlalchemy import text

        # Check if exists
        check = db.session.execute(
            text("SELECT id FROM sys_version WHERE version_code = :code"),
            {"code": data['version_code']}
        ).fetchone()

        if check:
            return Result.error('DUPLICATE', f"Version code {data['version_code']} already exists", 409)

        # Insert new version
        db.session.execute(
            text("""
                 INSERT INTO sys_version
                 (version_code, version_name, description, icon, sort_order, is_active, is_default)
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
            'version_code': data['version_code'],
            'version_name': data['version_name'],
            'description': data.get('description'),
            'icon': data.get('icon'),
            'sort_order': data.get('sort_order', 0),
            'is_active': data.get('is_active', True),
            'is_default': data.get('is_default', False)
        })
    except Exception as e:
        db.session.rollback()
        print("=" * 50)
        print("ERROR in create_version:")
        traceback.print_exc()
        print("=" * 50)
        return Result.error(code=500, message=str(e))


@api_bp.route('/system/versions/<version_code>', methods=['PUT'])
def update_version(version_code):
    """Update version"""
    data = request.json
    try:
        from sqlalchemy import text

        # Check if exists
        check = db.session.execute(
            text("SELECT id FROM sys_version WHERE version_code = :code"),
            {"code": version_code}
        ).fetchone()

        if not check:
            return Result.error('NOT_FOUND', f"Version {version_code} not found", 404)

        # Build update statement
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
        import traceback
        traceback.print_exc()
        return Result.error(code=500, message=str(e))


@api_bp.route('/system/versions/<version_code>', methods=['DELETE'])
def delete_version(version_code):
    """Delete version"""
    try:
        from sqlalchemy import text

        # Check if exists
        check = db.session.execute(
            text("SELECT id FROM sys_version WHERE version_code = :code"),
            {"code": version_code}
        ).fetchone()

        if not check:
            return Result.error('NOT_FOUND', f"Version {version_code} not found", 404)

        db.session.execute(
            text("DELETE FROM sys_version WHERE version_code = :code"),
            {"code": version_code}
        )
        db.session.commit()

        return Result.success(None, 'Deleted')
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return Result.error(code=500, message=str(e))


# ==================== Menu Config Interface (Frontend) ====================

@api_bp.route('/system/menu/config/<version_code>', methods=['GET'])
def get_menu_config(version_code):
    """Get menu configuration for a version (for frontend)"""
    try:
        from sqlalchemy import text

        # Check if version exists
        version = db.session.execute(
            text("SELECT version_code FROM sys_version WHERE version_code = :code"),
            {"code": version_code}
        ).fetchone()

        if not version:
            return Result.error('NOT_FOUND', f'Version {version_code} not found', 404)

        # Get visible menus for this version
        menus = db.session.execute(
            text("""
                 SELECT m.id,
                        m.parent_id,
                        m.menu_path,
                        m.menu_title,
                        m.menu_icon,
                        m.menu_type,
                        m.redirect_path,
                        COALESCE(vm.sort_order, m.sort_order) as sort_order
                 FROM sys_menu m
                          JOIN sys_version_menu vm ON m.id = vm.menu_id AND vm.version_code = :version_code
                 WHERE vm.is_visible = 1
                 ORDER BY m.parent_id, sort_order
                 """),
            {"version_code": version_code}
        ).fetchall()

        # Build tree structure
        def build_tree(parent_id=0):
            result = []
            for menu in menus:
                if menu[1] == parent_id:
                    node = {
                        'index': menu[2],
                        'title': menu[3],
                        'icon': menu[4]
                    }
                    children = build_tree(menu[0])
                    if children:
                        node['children'] = children
                    result.append(node)
            return result

        config = build_tree()
        return Result.success(config)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Result.error(code=500, message=str(e))


# ==================== Menu Management Interface (Admin) ====================

@api_bp.route('/system/menus', methods=['GET'])
def get_menu_tree():
    """Get all menu tree (for admin)"""
    try:
        from sqlalchemy import text

        menus = db.session.execute(
            text(
                "SELECT id, parent_id, menu_path, menu_title, menu_icon, menu_type, has_children, redirect_path, sort_order, is_visible FROM sys_menu ORDER BY parent_id, sort_order")
        ).fetchall()

        # Build tree structure
        menu_dict = {}
        for menu in menus:
            menu_dict[menu[0]] = {
                'id': menu[0],
                'parent_id': menu[1],
                'menu_path': menu[2],
                'menu_title': menu[3],
                'menu_icon': menu[4],
                'menu_type': menu[5],
                'has_children': menu[6] == 1,
                'redirect_path': menu[7],
                'sort_order': menu[8],
                'is_visible': menu[9] == 1,
                'children': []
            }

        roots = []
        for menu in menus:
            if menu[1] == 0:
                roots.append(menu_dict[menu[0]])
            else:
                if menu[1] in menu_dict:
                    menu_dict[menu[1]]['children'].append(menu_dict[menu[0]])

        return Result.success(roots)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Result.error(code=500, message=str(e))


@api_bp.route('/system/menus/<int:menu_id>', methods=['GET'])
def get_menu(menu_id):
    """Get menu detail"""
    try:
        from sqlalchemy import text

        menu = db.session.execute(
            text(
                "SELECT id, parent_id, menu_path, menu_title, menu_icon, menu_type, has_children, redirect_path, sort_order, is_visible, created_at, updated_at FROM sys_menu WHERE id = :id"),
            {"id": menu_id}
        ).fetchone()

        if not menu:
            return Result.error('NOT_FOUND', f'Menu {menu_id} not found', 404)

        return Result.success({
            'id': menu[0],
            'parent_id': menu[1],
            'menu_path': menu[2],
            'menu_title': menu[3],
            'menu_icon': menu[4],
            'menu_type': menu[5],
            'has_children': menu[6] == 1,
            'redirect_path': menu[7],
            'sort_order': menu[8],
            'is_visible': menu[9] == 1,
            'created_at': menu[10].isoformat() if menu[10] else None,
            'updated_at': menu[11].isoformat() if menu[11] else None
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Result.error(code=500, message=str(e))


@api_bp.route('/system/menus', methods=['POST'])
def create_menu():
    """Create menu"""
    data = request.json
    required = ['menu_path', 'menu_title']
    if not all(k in data for k in required):
        return Result.error('MISSING_FIELDS', 'menu_path and menu_title are required', 400)

    try:
        from sqlalchemy import text

        # Check if path exists
        existing = db.session.execute(
            text("SELECT id FROM sys_menu WHERE menu_path = :path"),
            {"path": data['menu_path']}
        ).fetchone()

        if existing:
            return Result.error('DUPLICATE', f"Menu path {data['menu_path']} already exists", 409)

        # Insert menu
        result = db.session.execute(
            text("""
                 INSERT INTO sys_menu
                 (parent_id, menu_path, menu_title, menu_icon, menu_type, has_children, redirect_path, sort_order,
                  is_visible)
                 VALUES (:parent_id, :menu_path, :menu_title, :menu_icon, :menu_type, :has_children, :redirect_path,
                         :sort_order, :is_visible)
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

        # Get new menu id
        new_id = db.session.execute(
            text("SELECT id FROM sys_menu WHERE menu_path = :path"),
            {"path": data['menu_path']}
        ).fetchone()[0]

        return Result.success({
            'id': new_id,
            'parent_id': data.get('parent_id', 0),
            'menu_path': data['menu_path'],
            'menu_title': data['menu_title'],
            'menu_icon': data.get('menu_icon'),
            'menu_type': data.get('menu_type', 'menu'),
            'has_children': data.get('has_children', False),
            'redirect_path': data.get('redirect_path'),
            'sort_order': data.get('sort_order', 0),
            'is_visible': data.get('is_visible', True)
        })
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return Result.error(code=500, message=str(e))


@api_bp.route('/system/menus/<int:menu_id>', methods=['PUT'])
def update_menu(menu_id):
    """Update menu"""
    data = request.json
    try:
        from sqlalchemy import text

        # Check if exists
        check = db.session.execute(
            text("SELECT id FROM sys_menu WHERE id = :id"),
            {"id": menu_id}
        ).fetchone()

        if not check:
            return Result.error('NOT_FOUND', f'Menu {menu_id} not found', 404)

        # Build update statement
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
        import traceback
        traceback.print_exc()
        return Result.error(code=500, message=str(e))


@api_bp.route('/system/menus/<int:menu_id>', methods=['DELETE'])
def delete_menu(menu_id):
    """Delete menu"""
    try:
        from sqlalchemy import text

        # Check if exists
        check = db.session.execute(
            text("SELECT id FROM sys_menu WHERE id = :id"),
            {"id": menu_id}
        ).fetchone()

        if not check:
            return Result.error('NOT_FOUND', f'Menu {menu_id} not found', 404)

        # Delete children first
        db.session.execute(
            text("DELETE FROM sys_menu WHERE parent_id = :parent_id"),
            {"parent_id": menu_id}
        )
        # Delete itself
        db.session.execute(
            text("DELETE FROM sys_menu WHERE id = :id"),
            {"id": menu_id}
        )
        db.session.commit()

        return Result.success(None, 'Deleted')
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return Result.error(code=500, message=str(e))


# ==================== Version Menu Config Management ====================

@api_bp.route('/system/version-menus/<version_code>', methods=['GET'])
def get_version_menus(version_code):
    """Get all menu config for a version (for admin)"""
    try:
        from sqlalchemy import text

        # Check if version exists
        version = db.session.execute(
            text(
                "SELECT version_code, version_name, description, icon, sort_order, is_default FROM sys_version WHERE version_code = :code"),
            {"code": version_code}
        ).fetchone()

        if not version:
            return Result.error('NOT_FOUND', f'Version {version_code} not found', 404)

        # Get menu config
        menus = db.session.execute(
            text("""
                 SELECT vm.menu_id, vm.menu_path, vm.is_visible, vm.sort_order
                 FROM sys_version_menu vm
                 WHERE vm.version_code = :version_code
                 ORDER BY COALESCE(vm.sort_order, 0)
                 """),
            {"version_code": version_code}
        ).fetchall()

        return Result.success({
            'version': {
                'code': version[0],
                'name': version[1],
                'description': version[2],
                'icon': version[3],
                'sort_order': version[4],
                'is_default': version[5] == 1
            },
            'menus': [
                {
                    'menu_id': menu[0],
                    'menu_path': menu[1],
                    'is_visible': menu[2] == 1,
                    'sort_order': menu[3]
                }
                for menu in menus
            ]
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Result.error(code=500, message=str(e))


@api_bp.route('/system/version-menus/<version_code>/menus/<int:menu_id>', methods=['PUT'])
def update_version_menu(version_code, menu_id):
    """Update menu config for a version"""
    data = request.json
    is_visible = data.get('is_visible', True)
    sort_order = data.get('sort_order')

    try:
        from sqlalchemy import text

        # Check if version exists
        version = db.session.execute(
            text("SELECT version_code FROM sys_version WHERE version_code = :code"),
            {"code": version_code}
        ).fetchone()

        if not version:
            return Result.error('NOT_FOUND', f'Version {version_code} not found', 404)

        # Check if menu exists
        menu = db.session.execute(
            text("SELECT menu_path FROM sys_menu WHERE id = :id"),
            {"id": menu_id}
        ).fetchone()

        if not menu:
            return Result.error('NOT_FOUND', f'Menu {menu_id} not found', 404)

        # Upsert
        db.session.execute(
            text("""
                 INSERT INTO sys_version_menu (version_code, menu_id, menu_path, is_visible, sort_order)
                 VALUES (:version_code, :menu_id, :menu_path, :is_visible, :sort_order) ON DUPLICATE KEY
                 UPDATE is_visible = :is_visible, sort_order = :sort_order
                 """),
            {
                "version_code": version_code,
                "menu_id": menu_id,
                "menu_path": menu[0],
                "is_visible": 1 if is_visible else 0,
                "sort_order": sort_order
            }
        )
        db.session.commit()

        return Result.success({
            'version_code': version_code,
            'menu_id': menu_id,
            'menu_path': menu[0],
            'is_visible': is_visible,
            'sort_order': sort_order
        })
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return Result.error(code=500, message=str(e))


@api_bp.route('/system/version-menus/<version_code>/batch', methods=['POST'])
def batch_update_version_menus(version_code):
    """Batch update menu config for a version"""
    data = request.json
    menus = data.get('menus', [])

    if not menus:
        return Result.error('INVALID_REQUEST', 'menus is required', 400)

    try:
        from sqlalchemy import text

        # Check if version exists
        version = db.session.execute(
            text("SELECT version_code FROM sys_version WHERE version_code = :code"),
            {"code": version_code}
        ).fetchone()

        if not version:
            return Result.error('NOT_FOUND', f'Version {version_code} not found', 404)

        count = 0
        for menu_config in menus:
            menu_id = menu_config.get('menu_id')
            is_visible = menu_config.get('is_visible', True)
            sort_order = menu_config.get('sort_order')

            # Get menu path
            menu = db.session.execute(
                text("SELECT menu_path FROM sys_menu WHERE id = :id"),
                {"id": menu_id}
            ).fetchone()

            if menu:
                db.session.execute(
                    text("""
                         INSERT INTO sys_version_menu (version_code, menu_id, menu_path, is_visible, sort_order)
                         VALUES (:version_code, :menu_id, :menu_path, :is_visible, :sort_order) ON DUPLICATE KEY
                         UPDATE is_visible = :is_visible, sort_order = :sort_order
                         """),
                    {
                        "version_code": version_code,
                        "menu_id": menu_id,
                        "menu_path": menu[0],
                        "is_visible": 1 if is_visible else 0,
                        "sort_order": sort_order
                    }
                )
                count += 1

        db.session.commit()
        return Result.success({'updated_count': count}, 'Batch update successful')
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return Result.error(code=500, message=str(e))


@api_bp.route('/system/version-menus/<version_code>/init', methods=['POST'])
def init_version_menus(version_code):
    """Initialize menu config for a version"""
    try:
        from sqlalchemy import text

        # Check if version exists
        version = db.session.execute(
            text("SELECT version_code FROM sys_version WHERE version_code = :code"),
            {"code": version_code}
        ).fetchone()

        if not version:
            return Result.error('NOT_FOUND', f'Version {version_code} not found', 404)

        # Get all menus
        all_menus = db.session.execute(
            text("SELECT id, menu_path FROM sys_menu")
        ).fetchall()

        count = 0
        for menu in all_menus:
            db.session.execute(
                text("""
                     INSERT
                     IGNORE INTO sys_version_menu (version_code, menu_id, menu_path, is_visible)
                    VALUES (:version_code, :menu_id, :menu_path, 1)
                     """),
                {
                    "version_code": version_code,
                    "menu_id": menu[0],
                    "menu_path": menu[1]
                }
            )
            count += 1

        db.session.commit()
        return Result.success({'initialized_count': count}, 'Initialization successful')
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return Result.error(code=500, message=str(e))


@api_bp.route('/system/version-menus/copy', methods=['POST'])
def copy_menu_config():
    """Copy menu configuration from one version to another"""
    from_version = request.args.get('from_version')
    to_version = request.args.get('to_version')

    if not from_version or not to_version:
        return Result.error('MISSING_FIELDS', 'from_version and to_version are required', 400)

    try:
        from sqlalchemy import text

        # Check if versions exist
        from_ver = db.session.execute(
            text("SELECT version_code FROM sys_version WHERE version_code = :code"),
            {"code": from_version}
        ).fetchone()

        to_ver = db.session.execute(
            text("SELECT version_code FROM sys_version WHERE version_code = :code"),
            {"code": to_version}
        ).fetchone()

        if not from_ver:
            return Result.error('NOT_FOUND', f'Source version {from_version} not found', 404)
        if not to_ver:
            return Result.error('NOT_FOUND', f'Target version {to_version} not found', 404)

        # Get source menus
        source_menus = db.session.execute(
            text(
                "SELECT menu_id, menu_path, is_visible, sort_order FROM sys_version_menu WHERE version_code = :version_code"),
            {"version_code": from_version}
        ).fetchall()

        count = 0
        for menu in source_menus:
            db.session.execute(
                text("""
                     INSERT INTO sys_version_menu (version_code, menu_id, menu_path, is_visible, sort_order)
                     VALUES (:version_code, :menu_id, :menu_path, :is_visible, :sort_order) ON DUPLICATE KEY
                     UPDATE is_visible = :is_visible, sort_order = :sort_order
                     """),
                {
                    "version_code": to_version,
                    "menu_id": menu[0],
                    "menu_path": menu[1],
                    "is_visible": menu[2],
                    "sort_order": menu[3]
                }
            )
            count += 1

        db.session.commit()
        return Result.success({'copied_count': count}, 'Copy successful')
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return Result.error(code=500, message=str(e))

