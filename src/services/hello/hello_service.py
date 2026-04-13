# src/imbs/services/hello/hello_service.py

from src.dao.hello_dao import HelloDAO

class HelloService:
    @staticmethod
    def get_hello_message() -> str:
        # 这里可以写复杂业务逻辑，比如从数据库读取配置、调用外部API等
        return "Hello, IMBS from Service Layer!"

    @staticmethod
    def get_personalized_message(name: str) -> dict:
        record = HelloDAO.find_by_name(name.strip())
        if record:
            return {"message": f"Hello, {record.email}! Welcome back."}
        else:
            return {"message": f"Hello, {name}! You're new here."}