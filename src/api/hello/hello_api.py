from src.api import api_bp
from src.services.hello.hello_service import HelloService
from src.models.response import Result   # 导入统一响应格式

@api_bp.route('/hello')
def hello():
    message = HelloService.get_hello_message()
    # 保持原有数据结构，包装在 Result 中
    return Result.success(data={"message": message})

@api_bp.route('/hello/<name>')
def hello_name(name):
    print(name+"收到请求")
    message = HelloService.get_personalized_message(name)
    return Result.success(data={"message": message})