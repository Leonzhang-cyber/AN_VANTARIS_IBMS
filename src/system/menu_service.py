# src/system/menu_service.py
import logging
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from src.system.menu_dao import VersionDAO, MenuDAO, VersionMenuDAO
from src.system.menu_models import SysVersion, SysMenu, SysVersionMenu

logger = logging.getLogger(__name__)


class MenuService:
    """菜单业务逻辑层"""

    @staticmethod
    def build_menu_tree(menus: List[SysMenu]) -> List[Dict]:
        """构建前端菜单树"""
        # 先构建 id 到菜单的映射
        menu_map = {m.id: m for m in menus}

        # 构建树
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
    def get_version_menu_config(session: Session, version_code: str) -> List[Dict]:
        """获取版本的菜单配置（前端可直接使用）"""
        menus = VersionMenuDAO.get_visible_menus(session, version_code)
        return MenuService.build_menu_tree(menus)

    @staticmethod
    def get_version_with_menus(session: Session, version_code: str) -> Optional[Dict]:
        """获取版本及其菜单配置"""
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
                'is_default': version.is_default
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
        """复制菜单配置从一个版本到另一个版本"""
        source_menus = VersionMenuDAO.get_by_version(session, from_version, only_visible=False)

        count = 0
        for vm in source_menus:
            existing = VersionMenuDAO.set_visible(
                session, to_version, vm.menu_id,
                vm.is_visible == 1, vm.sort_order
            )
            count += 1
        session.flush()
        return count

    @staticmethod
    def get_menu_tree(session: Session) -> List[Dict]:
        """获取所有菜单树（管理用）- 不使用 ORM 自关联"""
        menus = MenuDAO.get_all(session)

        # 手动构建树结构
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

        # 构建树
        roots = []
        for menu in menus:
            if menu.parent_id == 0:
                roots.append(menu_dict[menu.id])
            else:
                if menu.parent_id in menu_dict:
                    menu_dict[menu.parent_id]['children'].append(menu_dict[menu.id])

        return roots