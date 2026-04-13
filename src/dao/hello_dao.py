# src/dao/hello_dao.py
from typing import Optional, List
from src.models.Hello import Hello
from src.core.database import db

class HelloDAO:
    @staticmethod
    def find_by_name(name: str) -> Optional[Hello]:
        """根据姓名精确查询记录"""
        return Hello.query.filter_by(name=name).first()

    @staticmethod
    def find_all() -> List[Hello]:
        """查询所有记录"""
        return Hello.query.all()

    @staticmethod
    def create(name: str, age: int = None, email: str = None) -> Hello:
        """创建新记录"""
        record = Hello(name=name, age=age, email=email)
        db.session.add(record)
        db.session.commit()
        return record

    @staticmethod
    def delete_by_id(id: int) -> bool:
        """根据 ID 删除记录"""
        record = Hello.query.get(id)
        if record:
            db.session.delete(record)
            db.session.commit()
            return True
        return False