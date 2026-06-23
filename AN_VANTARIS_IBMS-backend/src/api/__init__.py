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
from .umms import umms_api
from .uedge import uedge_api
from .airport_ga_readonly import airport_ga_readonly_api
from .prod_ga import foundation_packages_api
from .uhmi import uhmi_api
from .customer_delivery import customer_delivery_api
from .engineer_installer import engineer_installer_api
from .foundation_diagnostics import foundation_diagnostics_api
from .asset_context import asset_context_api
from .code_policy import code_policy_api
from .nexus_ai import nexus_ai_api
from .server_precheck import server_precheck_api
from .iot.sse_api import *
