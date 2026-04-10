# src/imbs/api/__init__.py
from flask import Blueprint

# 创建蓝图对象，url_prefix 可以给所有 API 路由加前缀，例如 /api
api_bp = Blueprint('api', __name__, url_prefix='/api')

# 导入各个路由模块，让蓝图知道这些路由
from . import hello_api