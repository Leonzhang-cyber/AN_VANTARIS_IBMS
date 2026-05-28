# src/system/menu_service.py
import logging
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.system.menu_dao import VersionDAO, MenuDAO, VersionMenuDAO
from src.system.menu_models import SysVersion, SysMenu, SysVersionMenu

logger = logging.getLogger(__name__)


class MenuService:
    """菜单业务逻辑层"""

    @staticmethod
    def build_menu_tree(menus: List[SysMenu]) -> List[Dict]:
        def build(parent_id: int = 0) -> List[Dict]:
            result = []
            for menu in menus:
                if menu.parent_id == parent_id:
                    node = {
                        'index': menu.menu_path,
                        'title': menu.menu_title,
                        'icon': menu.menu_icon
                    }
                    children = build(menu.id)
                    if children:
                        node['children'] = children
                    result.append(node)
            return result
        return build()

    @staticmethod
    def build_menu_tree_from_raw(menus: List) -> List[Dict]:
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
        return build_tree()

    @staticmethod
    def get_version_menu_config(session: Session, version_code: str) -> List[Dict]:
        menus = VersionMenuDAO.get_visible_menus(session, version_code)
        return MenuService.build_menu_tree(menus)

    @staticmethod
    def get_version_with_menus(session: Session, version_code: str) -> Optional[Dict]:
        version = VersionDAO.get_by_code(session, version_code)
        if not version:
            return None

        menus = VersionMenuDAO.get_by_version(session, version_code, only_visible=False)

        return {
            'version': {
                'code': version.version_code,
                'name': version.version_name,
                'description': version.description,
                'icon': version.icon,
                'sort_order': version.sort_order,
                'is_default': version.is_default == 1
            },
            'menus': [
                {
                    'menu_id': vm.menu_id,
                    'menu_path': vm.menu_path,
                    'is_visible': vm.is_visible == 1,
                    'sort_order': vm.sort_order
                }
                for vm in menus
            ]
        }

    @staticmethod
    def copy_menu_config(session: Session, from_version: str, to_version: str) -> int:
        source_menus = VersionMenuDAO.get_by_version(session, from_version, only_visible=False)
        count = 0
        for vm in source_menus:
            VersionMenuDAO.set_visible(session, to_version, vm.menu_id, vm.is_visible == 1, vm.sort_order)
            count += 1
        session.flush()
        return count

    @staticmethod
    def get_menu_tree(session: Session) -> List[Dict]:
        menus = MenuDAO.get_all(session)

        menu_dict = {}
        for menu in menus:
            menu_dict[menu.id] = {
                'id': menu.id,
                'parent_id': menu.parent_id,
                'menu_path': menu.menu_path,
                'menu_title': menu.menu_title,
                'menu_icon': menu.menu_icon,
                'menu_type': menu.menu_type,
                'has_children': menu.has_children == 1,
                'redirect_path': menu.redirect_path,
                'sort_order': menu.sort_order,
                'is_visible': menu.is_visible == 1,
                'children': []
            }

        roots = []
        for menu in menus:
            if menu.parent_id == 0:
                roots.append(menu_dict[menu.id])
            else:
                if menu.parent_id in menu_dict:
                    menu_dict[menu.parent_id]['children'].append(menu_dict[menu.id])
        return roots

    @staticmethod
    def get_active_version_menu_config(session: Session) -> Optional[Dict]:
        result = session.execute(
            text("SELECT version_code FROM sys_version WHERE is_default = 1 LIMIT 1")
        ).fetchone()

        if not result:
            return None

        version_code = result[0]

        menus = session.execute(
            text("""
                 SELECT m.id, m.parent_id, m.menu_path, m.menu_title, m.menu_icon,
                        m.menu_type, m.redirect_path, COALESCE(vm.sort_order, m.sort_order) as sort_order
                 FROM sys_menu m
                 JOIN sys_version_menu vm ON m.id = vm.menu_id AND vm.version_code = :version_code
                 WHERE vm.is_visible = 1
                 ORDER BY m.parent_id, sort_order
                 """),
            {"version_code": version_code}
        ).fetchall()

        config = MenuService.build_menu_tree_from_raw(menus)

        return {
            'version_code': version_code,
            'menu_config': config
        }

    @staticmethod
    def switch_active_version(session: Session, version_code: str) -> Optional[Dict]:
        target = session.execute(
            text("SELECT version_code FROM sys_version WHERE version_code = :code"),
            {"code": version_code}
        ).fetchone()

        if not target:
            return None

        session.execute(text("UPDATE sys_version SET is_default = 0"))
        session.execute(
            text("UPDATE sys_version SET is_default = 1 WHERE version_code = :code"),
            {"code": version_code}
        )
        session.flush()

        menus = session.execute(
            text("""
                 SELECT m.id, m.parent_id, m.menu_path, m.menu_title, m.menu_icon,
                        m.menu_type, m.redirect_path, COALESCE(vm.sort_order, m.sort_order) as sort_order
                 FROM sys_menu m
                 JOIN sys_version_menu vm ON m.id = vm.menu_id AND vm.version_code = :version_code
                 WHERE vm.is_visible = 1
                 ORDER BY m.parent_id, sort_order
                 """),
            {"version_code": version_code}
        ).fetchall()

        config = MenuService.build_menu_tree_from_raw(menus)

        version_info = session.execute(
            text("SELECT version_code, version_name, description, icon FROM sys_version WHERE version_code = :code"),
            {"code": version_code}
        ).fetchone()

        return {
            'version_code': version_code,
            'version_name': version_info[1],
            'description': version_info[2],
            'icon': version_info[3],
            'menu_config': config
        }