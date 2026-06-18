# src/api/__init__.py
from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

# 导入其他模块
from .did import did_api
from .iot import iot_api
from .system import system_api, menu_api
from .data_modeling import modeling_api
from .reports import reports_api
from .console import console_api
from .ucde import ucde_api
from .assets import assets_api
from .uesg import uesg_api
from .iot.sse_api import *