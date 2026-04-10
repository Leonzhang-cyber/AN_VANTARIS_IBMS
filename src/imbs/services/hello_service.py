# src/imbs/services/hello_service.py

class HelloService:
    @staticmethod
    def get_hello_message() -> str:
        # 这里可以写复杂业务逻辑，比如从数据库读取配置、调用外部API等
        return "Hello, IMBS from Service Layer!"

    @staticmethod
    def get_personalized_message(name: str) -> str:
        return f"Hello, {name}! Welcome to IMBS."