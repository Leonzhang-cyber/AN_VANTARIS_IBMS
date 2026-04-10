# src/imbs/api/hello_api.py
from . import api_bp
from src.imbs.services.hello_service import HelloService   # 绝对导入

@api_bp.route('/hello')
def hello():
    # 调用服务层获取消息
    message = HelloService.get_hello_message()
    return {"message": message}

@api_bp.route('/hello/<name>')
def hello_name(name):
    message = HelloService.get_personalized_message(name)
    return {"message": message}