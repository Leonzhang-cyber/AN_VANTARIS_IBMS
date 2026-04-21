# src/api/__init__.py
from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

# 导入其他模块
from .did import did_api
from .iot import iot_api
from .iot.sse_api import *