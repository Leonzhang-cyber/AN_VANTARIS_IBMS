from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

# 导入所有子模块
from .hello import hello_api
from .did import did_api