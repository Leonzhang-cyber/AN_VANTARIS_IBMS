# src/system/menu_dao.py
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional, Dict, Any
from src.system.menu_models import SysVersion, SysMenu, SysVersionMenu


class VersionDAO:
    """版本数据访问层"""

    @staticmethod
    def create(session: Session, **kwargs) -> SysVersion:
        version = SysVersion(**kwargs)
        session.add(version)
        session.flush()
        return version

    @staticmethod
    def update(session: Session, version: SysVersion, **kwargs) -> SysVersion:
        for key, value in kwargs.items():
            if hasattr(version, key) and value is not None:
                setattr(version, key, value)
        session.flush()
        return version

    @staticmethod
    def delete(session: Session, version: SysVersion):
        session.delete(version)
        session.flush()

    @staticmethod
    def get_by_code(session: Session, version_code: str) -> Optional[SysVersion]:
        return session.query(SysVersion).filter(SysVersion.version_code == version_code).first()

    @staticmethod
    def get_by_id(session: Session, version_id: int) -> Optional[SysVersion]:
        return session.query(SysVersion).filter(SysVersion.id == version_id).first()

    @staticmethod
    def get_all(session: Session, is_active: bool = None) -> List[SysVersion]:
        query = session.query(SysVersion).order_by(SysVersion.sort_order)
        if is_active is not None:
            query = query.filter(SysVersion.is_active == (1 if is_active else 0))
        return query.all()

    @staticmethod
    def get_default(session: Session) -> Optional[SysVersion]:
        return session.query(SysVersion).filter(SysVersion.is_default == 1).first()


class MenuDAO:
    """菜单数据访问层"""

    @staticmethod
    def create(session: Session, **kwargs) -> SysMenu:
        menu = SysMenu(**kwargs)
        session.add(menu)
        session.flush()
        return menu

    @staticmethod
    def update(session: Session, menu: SysMenu, **kwargs) -> SysMenu:
        for key, value in kwargs.items():
            if hasattr(menu, key) and value is not None:
                setattr(menu, key, value)
        session.flush()
        return menu

    @staticmethod
    def delete(session: Session, menu: SysMenu):
        session.delete(menu)
        session.flush()

    @staticmethod
    def get_by_id(session: Session, menu_id: int) -> Optional[SysMenu]:
        return session.query(SysMenu).filter(SysMenu.id == menu_id).first()

    @staticmethod
    def get_by_path(session: Session, menu_path: str) -> Optional[SysMenu]:
        return session.query(SysMenu).filter(SysMenu.menu_path == menu_path).first()

    @staticmethod
    def get_all(session: Session) -> List[SysMenu]:
        return session.query(SysMenu).order_by(SysMenu.parent_id, SysMenu.sort_order).all()

    @staticmethod
    def get_by_parent(session: Session, parent_id: int = 0) -> List[SysMenu]:
        return session.query(SysMenu).filter(SysMenu.parent_id == parent_id).order_by(SysMenu.sort_order).all()


class VersionMenuDAO:
    """版本菜单关联数据访问层"""

    @staticmethod
    def set_visible(session: Session, version_code: str, menu_id: int, is_visible: bool,
                    sort_order: int = None) -> SysVersionMenu:
        existing = session.query(SysVersionMenu).filter(
            and_(SysVersionMenu.version_code == version_code, SysVersionMenu.menu_id == menu_id)
        ).first()

        if existing:
            existing.is_visible = 1 if is_visible else 0
            if sort_order is not None:
                existing.sort_order = sort_order
            session.flush()
            return existing

        menu = session.query(SysMenu).filter(SysMenu.id == menu_id).first()
        if not menu:
            raise ValueError(f"Menu {menu_id} not found")

        vm = SysVersionMenu(
            version_code=version_code,
            menu_id=menu_id,
            menu_path=menu.menu_path,
            is_visible=1 if is_visible else 0,
            sort_order=sort_order
        )
        session.add(vm)
        session.flush()
        return vm

    @staticmethod
    def get_by_version(session: Session, version_code: str, only_visible: bool = True) -> List[SysVersionMenu]:
        query = session.query(SysVersionMenu).filter(SysVersionMenu.version_code == version_code)
        if only_visible:
            query = query.filter(SysVersionMenu.is_visible == 1)
        return query.all()

    @staticmethod
    def get_visible_menus(session: Session, version_code: str) -> List[SysMenu]:
        return session.query(SysMenu).join(
            SysVersionMenu,
            and_(
                SysMenu.id == SysVersionMenu.menu_id,
                SysVersionMenu.version_code == version_code,
                SysVersionMenu.is_visible == 1
            )
        ).order_by(SysMenu.parent_id, SysVersionMenu.sort_order).all()

    @staticmethod
    def init_version_menus(session: Session, version_code: str) -> int:
        all_menus = session.query(SysMenu).all()
        count = 0
        for menu in all_menus:
            existing = session.query(SysVersionMenu).filter(
                and_(SysVersionMenu.version_code == version_code, SysVersionMenu.menu_id == menu.id)
            ).first()
            if not existing:
                vm = SysVersionMenu(
                    version_code=version_code,
                    menu_id=menu.id,
                    menu_path=menu.menu_path,
                    is_visible=1
                )
                session.add(vm)
                count += 1
        session.flush()
        return count

    @staticmethod
    def batch_update(session: Session, version_code: str, menus: List[Dict]) -> int:
        count = 0
        for menu_config in menus:
            menu_id = menu_config.get('menu_id')
            is_visible = menu_config.get('is_visible', True)
            sort_order = menu_config.get('sort_order')

            existing = session.query(SysVersionMenu).filter(
                and_(SysVersionMenu.version_code == version_code, SysVersionMenu.menu_id == menu_id)
            ).first()

            if existing:
                existing.is_visible = 1 if is_visible else 0
                if sort_order is not None:
                    existing.sort_order = sort_order
            else:
                menu = session.query(SysMenu).filter(SysMenu.id == menu_id).first()
                if menu:
                    vm = SysVersionMenu(
                        version_code=version_code,
                        menu_id=menu_id,
                        menu_path=menu.menu_path,
                        is_visible=1 if is_visible else 0,
                        sort_order=sort_order
                    )
                    session.add(vm)
            count += 1
        session.flush()
        return count

    @staticmethod
    def delete_by_version(session: Session, version_code: str) -> int:
        deleted = session.query(SysVersionMenu).filter(SysVersionMenu.version_code == version_code).delete()
        session.flush()
        return deleted