# src/api/iot/iot_api.py
"""
IoT 模块 API 接口
提供设备注册功能
"""

from flask import request

from src.api import api_bp
from src.common.models.response import Result
from src.common.utils.jwt_util import jwt_required
from src.common.utils.permission_util import require_permission, require_any_permission
from src.common.utils.audit_trace import log_sensitive_api
from src.Iot.services.device_service import DeviceService
from src.Iot.exceptions import DeviceRegistrationError, DeviceNotFoundError


# ==================== 初始化服务 ====================

def get_device_service() -> DeviceService:
    """获取设备服务实例"""
    return DeviceService()


# ==================== 1. 设备注册接口====================

@api_bp.route('/iot/device/register', methods=['POST'])
@jwt_required
@require_permission('device:manage')
def register_device():
    """
    设备注册接口（保存设备信息到数据库）
    注意：设备主体需提前通过DID模块的 /api/did/entity 接口注册

    请求体 JSON:
    {
        "device_name": "温度传感器001",
        "device_code": "TEMP_001",
        "did": "did:imbs:device:xxx",
        "public_key": "0x...",
        "private_key": "0x...",
        "vc_json": {},
        "parent_did": "did:imbs:property:xxx",
        "protocol": "mqtt",
        "connect_config": {},
        "field_mappings": [],
        "method_mappings": [],
        "extra": {}
    }
    """
    log_sensitive_api("iot.device.register", category="iot")
    data = request.get_json()

    if not data:
        return Result.error(message="请求体不能为空", code=400)

    try:
        service = get_device_service()
        result = service.register_device(data)
        return Result.success(data=result, message="设备注册成功")
    except DeviceRegistrationError as e:
        return Result.error(message=str(e), code=400)
    except Exception as e:
        return Result.error(message=f"设备注册失败: {str(e)}", code=500)


# ==================== 2. 根据父DID查询设备列表 ====================

@api_bp.route('/iot/device/parent/<string:parent_did>', methods=['GET'])
def get_devices_by_parent(parent_did: str):
    """
    根据父DID查询该区域下所有设备

    请求参数:
        parent_did: 父实体DID（路径参数）
        page: 页码（默认1）
        per_page: 每页数量（默认20）
        status: 状态过滤（可选，0离线/1在线/2异常）
        protocol: 协议过滤（可选）

    返回:
        {
            "code": 200,
            "data": {
                "items": [
                    {
                        "id": "uuid",
                        "did": "...",
                        "device_code": "...",
                        "device_name": "...",
                        "protocol": "mqtt",
                        "status": 0,
                        "parent_did": "...",
                        "created_at": "...",
                        "updated_at": "..."
                    }
                ],
                "total": 10,
                "page": 1,
                "per_page": 20,
                "pages": 1
            }
        }
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status', type=int)
        protocol = request.args.get('protocol')

        service = get_device_service()
        result = service.get_devices_by_parent(
            parent_did=parent_did,
            page=page,
            per_page=per_page,
            status=status,
            protocol=protocol
        )
        return Result.success(data=result)
    except Exception as e:
        return Result.error(message=f"查询失败: {str(e)}", code=500)


# ==================== 3. 根据DID查询设备详细信息 ====================

@api_bp.route('/iot/device/did/<string:device_did>', methods=['GET'])
def get_device_by_did(device_did: str):
    """
    根据设备DID查询设备详细信息（包含字段映射和方法映射）

    请求参数:
        device_did: 设备DID（路径参数）

    返回:
        {
            "code": 200,
            "data": {
                "id": "uuid",
                "did": "...",
                "device_code": "...",
                "device_name": "...",
                "public_key": "0x...",
                "vc_json": {},
                "parent_did": "...",
                "protocol": "mqtt",
                "connect_config": {},
                "status": 0,
                "extra": {},
                "field_mappings": [
                    {
                        "id": "uuid",
                        "raw_field": "power_kw",
                        "standard_field": "power",
                        "transform": null
                    }
                ],
                "method_mappings": [
                    {
                        "id": "uuid",
                        "direction": "downlink",
                        "raw_path": "building/hvac/command",
                        "standard_method": "set_temperature"
                    }
                ],
                "created_at": "...",
                "updated_at": "..."
            }
        }
    """
    try:
        service = get_device_service()
        result = service.get_device_detail(device_did)
        return Result.success(data=result)
    except DeviceNotFoundError as e:
        return Result.error(message=str(e), code=404)
    except Exception as e:
        return Result.error(message=f"查询失败: {str(e)}", code=500)


# ==================== 4. 根据设备编号查询设备信息 ====================

@api_bp.route('/iot/device/code/<string:device_code>', methods=['GET'])
def get_device_by_code(device_code: str):
    """
    根据设备编号查询设备基本信息

    请求参数:
        device_code: 设备编号（路径参数）

    返回:
        {
            "code": 200,
            "data": {
                "id": "uuid",
                "did": "...",
                "device_code": "...",
                "device_name": "...",
                "protocol": "mqtt",
                "status": 0,
                "parent_did": "...",
                "created_at": "...",
                "updated_at": "..."
            }
        }
    """
    try:
        service = get_device_service()
        result = service.get_device_by_code(device_code)
        return Result.success(data=result)
    except DeviceNotFoundError as e:
        return Result.error(message=str(e), code=404)
    except Exception as e:
        return Result.error(message=f"查询失败: {str(e)}", code=500)


# ==================== 5. 更新设备信息 ====================

@api_bp.route('/iot/device/did/<string:device_did>', methods=['PUT'])
@jwt_required
@require_permission('device:manage')
def update_device(device_did: str):
    """
    更新设备信息（只更新设备主表，不更新映射关系）

    请求体 JSON:
    {
        "device_name": "新设备名称",        // 可选
        "connect_config": {},              // 可选
        "extra": {},                       // 可选
        "status": 1                        // 可选 (0离线/1在线/2异常)
    }
    """
    log_sensitive_api("iot.device.update", device_did=device_did, category="iot")
    data = request.get_json()

    if not data:
        return Result.error(message="请求体不能为空", code=400)

    try:
        service = get_device_service()
        result = service.update_device(device_did, data)
        return Result.success(data=result, message="设备更新成功")
    except DeviceNotFoundError as e:
        return Result.error(message=str(e), code=404)
    except DeviceRegistrationError as e:
        return Result.error(message=str(e), code=400)
    except Exception as e:
        return Result.error(message=f"更新失败: {str(e)}", code=500)


# ==================== 6. 部分更新设备信息 ====================

@api_bp.route('/iot/device/did/<string:device_did>', methods=['PATCH'])
@jwt_required
@require_permission('device:manage')
def patch_device(device_did: str):
    """
    部分更新设备信息（PATCH方式，只更新传入的字段）

    请求体 JSON:
    {
        "device_name": "新设备名称",        // 可选
        "status": 1                        // 可选
    }
    """
    log_sensitive_api("iot.device.patch", device_did=device_did, category="iot")
    data = request.get_json()

    if not data:
        return Result.error(message="请求体不能为空", code=400)

    try:
        service = get_device_service()
        result = service.patch_device(device_did, data)
        return Result.success(data=result, message="设备更新成功")
    except DeviceNotFoundError as e:
        return Result.error(message=str(e), code=404)
    except DeviceRegistrationError as e:
        return Result.error(message=str(e), code=400)
    except Exception as e:
        return Result.error(message=f"更新失败: {str(e)}", code=500)


# ==================== 7. 删除设备 ====================

@api_bp.route('/iot/device/did/<string:device_did>', methods=['DELETE'])
@jwt_required
@require_permission('device:manage')
def delete_device(device_did: str):
    """
    删除设备（同时删除关联的字段映射和方法映射）
    """
    log_sensitive_api("iot.device.delete", device_did=device_did, category="iot")
    try:
        service = get_device_service()
        service.delete_device(device_did)
        return Result.success(message="设备删除成功")
    except DeviceNotFoundError as e:
        return Result.error(message=str(e), code=404)
    except Exception as e:
        return Result.error(message=f"删除失败: {str(e)}", code=500)


# ==================== 8. 更新设备状态 ====================

@api_bp.route('/iot/device/did/<string:device_did>/status', methods=['PUT'])
@jwt_required
@require_permission('device:manage')
def update_device_status(device_did: str):
    """
    更新设备状态

    请求体 JSON:
    {
        "status": 1    // 0离线/1在线/2异常
    }
    """
    data = request.get_json()

    if not data or 'status' not in data:
        return Result.error(message="缺少 status 参数", code=400)

    status = data.get('status')
    if status not in [0, 1, 2]:
        return Result.error(message="status 必须是 0(离线)、1(在线) 或 2(异常)", code=400)

    try:
        service = get_device_service()
        result = service.update_device_status(device_did, status)
        return Result.success(data=result, message="设备状态更新成功")
    except DeviceNotFoundError as e:
        return Result.error(message=str(e), code=404)
    except Exception as e:
        return Result.error(message=f"更新失败: {str(e)}", code=500)


# ==================== 9. 更新设备的字段映射 ====================

@api_bp.route('/iot/device/did/<string:device_did>/field-mappings', methods=['PUT'])
@jwt_required
@require_permission('device:manage')
def update_device_field_mappings(device_did: str):
    """
    更新设备的字段映射（先删除旧的，再创建新的）

    请求体 JSON:
    {
        "field_mappings": [
            {
                "raw_field": "power_kw",
                "standard_field": "power",
                "transform": null
            }
        ]
    }
    """
    data = request.get_json()

    if not data or 'field_mappings' not in data:
        return Result.error(message="缺少 field_mappings 参数", code=400)

    try:
        service = get_device_service()
        result = service.update_device_field_mappings(device_did, data['field_mappings'])
        return Result.success(data=result, message="字段映射更新成功")
    except DeviceNotFoundError as e:
        return Result.error(message=str(e), code=404)
    except Exception as e:
        return Result.error(message=f"更新失败: {str(e)}", code=500)


# ==================== 10. 更新设备的方法映射 ====================

@api_bp.route('/iot/device/did/<string:device_did>/method-mappings', methods=['PUT'])
@jwt_required
@require_permission('device:manage')
def update_device_method_mappings(device_did: str):
    """
    更新设备的方法映射（先删除旧的，再创建新的）

    请求体 JSON:
    {
        "method_mappings": [
            {
                "direction": "downlink",
                "raw_path": "building/hvac/command",
                "standard_method": "set_temperature",
                "extra": {"param": "setpoint_c"}
            }
        ]
    }
    """
    data = request.get_json()

    if not data or 'method_mappings' not in data:
        return Result.error(message="缺少 method_mappings 参数", code=400)

    try:
        service = get_device_service()
        result = service.update_device_method_mappings(device_did, data['method_mappings'])
        return Result.success(data=result, message="方法映射更新成功")
    except DeviceNotFoundError as e:
        return Result.error(message=str(e), code=404)
    except Exception as e:
        return Result.error(message=f"更新失败: {str(e)}", code=500)


# ==================== 11. 添加 SSE 连接地址接口 ====================
@api_bp.route('/iot/device/<string:device_code>/sse-url', methods=['GET'])
def get_device_sse_url(device_code: str):
    """
    获取设备的 SSE 连接地址

    返回:
    {
        "code": 200,
        "data": {
            "url": "http://localhost:5000/api/iot/device/HVAC_SIM_001/stream",
            "device_code": "HVAC_SIM_001",
            "protocol": "http"
        }
    }
    """
    from flask import request

    host = request.host
    protocol = "https" if request.is_secure else "http"

    sse_url = f"{protocol}://{host}/api/iot/device/{device_code}/stream"

    return Result.success(data={
        'url': sse_url,
        'device_code': device_code,
        'protocol': protocol,
        'method': 'GET',
        'content_type': 'text/event-stream'
    })


# ==================== 12. 获取标准字典（全局） ====================

@api_bp.route('/iot/standard-methods', methods=['GET'])
def get_standard_methods():
    """
    获取标准方法字典（所有可用的标准方法定义）

    请求参数:
        category: 可选，按分类过滤(control/query/config)

    返回:
        {
            "code": 200,
            "data": {
                "methods": [
                    {
                        "method_code": "set_temperature",
                        "method_name": "设置温度",
                        "description": "设置设备的目标温度",
                        "category": "control",
                        "params_schema": {...},
                        "response_schema": {...}
                    }
                ]
            }
        }
    """
    from src.Iot.dao import StandardMethodDAO

    category = request.args.get('category')
    methods = StandardMethodDAO.get_all(category)

    result = []
    for m in methods:
        result.append({
            'method_code': m.method_code,
            'method_name': m.method_name,
            'description': m.description,
            'category': m.category,
            'params_schema': m.params_schema,
            'response_schema': m.response_schema
        })

    return Result.success(data={'methods': result})


@api_bp.route('/iot/standard-methods/<string:method_code>', methods=['GET'])
def get_standard_method_detail(method_code: str):
    """
    获取单个标准方法的详细定义
    """
    from src.Iot.dao import StandardMethodDAO

    method = StandardMethodDAO.get_by_code(method_code)
    if not method:
        return Result.error(message=f"方法不存在: {method_code}", code=404)

    return Result.success(data={
        'method_code': method.method_code,
        'method_name': method.method_name,
        'description': method.description,
        'category': method.category,
        'params_schema': method.params_schema,
        'response_schema': method.response_schema
    })


@api_bp.route('/iot/standard-fields', methods=['GET'])
def get_standard_fields():
    """
    获取标准字段字典（所有可用的标准字段定义）

    请求参数:
        is_critical: 可选，是否关键字段 (true/false)
        field_type: 可选，字段类型过滤 (float/int/string/bool/json)

    返回:
        {
            "code": 200,
            "data": {
                "fields": [
                    {
                        "field_code": "temperature",
                        "field_name": "温度",
                        "field_type": "float",
                        "unit": "℃",
                        "description": "环境温度",
                        "min_value": -40,
                        "max_value": 100,
                        "is_critical": true
                    }
                ]
            }
        }
    """
    from src.Iot.dao import StandardFieldDAO

    is_critical = request.args.get('is_critical')
    if is_critical is not None:
        is_critical = is_critical.lower() == 'true'

    field_type = request.args.get('field_type')

    result = StandardFieldDAO.get_all_fields(
        page=1,
        per_page=1000,
        is_critical=is_critical,
        field_type=field_type
    )

    fields = []
    for f in result['items']:
        fields.append({
            'field_code': f.field_code,
            'field_name': f.field_name,
            'field_type': f.field_type,
            'unit': f.unit,
            'description': f.description,
            'min_value': float(f.min_value) if f.min_value is not None else None,
            'max_value': float(f.max_value) if f.max_value is not None else None,
            'is_critical': f.is_critical,
            'extra': f.extra
        })

    return Result.success(data={'fields': fields, 'total': result['total']})


@api_bp.route('/iot/standard-fields/<string:field_code>', methods=['GET'])
def get_standard_field_detail(field_code: str):
    """
    获取单个标准字段的详细定义
    """
    from src.Iot.dao import StandardFieldDAO

    field = StandardFieldDAO.get_field_by_code(field_code)
    if not field:
        return Result.error(message=f"标准字段不存在: {field_code}", code=404)

    return Result.success(data={
        'field_code': field.field_code,
        'field_name': field.field_name,
        'field_type': field.field_type,
        'unit': field.unit,
        'description': field.description,
        'min_value': float(field.min_value) if field.min_value is not None else None,
        'max_value': float(field.max_value) if field.max_value is not None else None,
        'is_critical': field.is_critical,
        'extra': field.extra,
        'created_at': field.created_at.isoformat() if field.created_at else None
    })


# ==================== 13. 下发命令接口 ====================

@api_bp.route('/iot/device/<string:device_did>/command', methods=['POST'])
@jwt_required
@require_any_permission(['iot:command', 'device:control'])
def send_device_command(device_did: str):
    """
    向设备下发命令

    请求体:
    {
        "method": "set_temperature",
        "params": {"value": 24}
    }
    """
    log_sensitive_api("iot.device.command", device_did=device_did, category="iot")
    data = request.get_json()

    if not data or 'method' not in data:
        return Result.error(message="缺少 method 参数", code=400)

    try:
        from src.Iot.device_manager import get_device_manager

        device_manager = get_device_manager()
        result = device_manager.send_command(device_did, data)

        if result.get('success'):
            return Result.success(data=result, message="命令下发成功")
        else:
            return Result.error(message=result.get('error', '命令下发失败'), code=400)

    except Exception as e:
        return Result.error(message=f"命令下发失败: {str(e)}", code=500)


@api_bp.route('/iot/device/code/<string:device_code>/command', methods=['POST'])
@jwt_required
@require_any_permission(['iot:command', 'device:control'])
def send_command_by_code(device_code: str):
    """根据设备编号下发命令"""
    log_sensitive_api("iot.device.command", device_code=device_code, category="iot")
    from src.Iot.dao import DeviceDAO

    data = request.get_json()

    if not data or 'method' not in data:
        return Result.error(message="缺少 method 参数", code=400)

    try:
        device = DeviceDAO.get_device_by_code(device_code)

        from src.Iot.device_manager import get_device_manager
        device_manager = get_device_manager()
        result = device_manager.send_command(device.did, data)

        if result.get('success'):
            return Result.success(data=result, message="命令下发成功")
        else:
            return Result.error(message=result.get('error', '命令下发失败'), code=400)

    except DeviceNotFoundError as e:
        return Result.error(message=str(e), code=404)
    except Exception as e:
        return Result.error(message=f"命令下发失败: {str(e)}", code=500)


# ==================== 14. 获取设备的字段映射 ====================

@api_bp.route('/iot/<string:device_did>/field-mappings-info', methods=['GET'])
def get_device_field_mappings(device_did: str):
    """
    获取设备的字段映射列表

    返回:
    {
        "code": 200,
        "data": {
            "field_mappings": [
                {
                    "id": "uuid",
                    "raw_field": "power_kw",
                    "standard_field": "power",
                    "transform": null,
                    "protocol": "mqtt",
                    "created_at": "..."
                }
            ]
        }
    }
    """
    from src.Iot.dao import FieldMappingDAO
    from src.Iot.dao import DeviceDAO
    from src.Iot.exceptions import DeviceNotFoundError

    try:
        device = DeviceDAO.get_device_by_did(device_did)
        mappings = FieldMappingDAO.get_mappings_by_device(device_did, device.protocol)

        result = []
        for m in mappings:
            result.append({
                'id': m.id,
                'raw_field': m.raw_field,
                'standard_field': m.standard_field,
                'transform': m.transform,
                'protocol': m.protocol,
                'created_at': m.created_at.isoformat() if m.created_at else None
            })

        return Result.success(data={'field_mappings': result})
    except DeviceNotFoundError as e:
        return Result.error(message=str(e), code=404)
    except Exception as e:
        return Result.error(message=str(e), code=500)


# ==================== 15. 获取设备的方法映射 ====================

@api_bp.route('/iot/<string:device_did>/method-mappings-info', methods=['GET'])
def get_device_method_mappings(device_did: str):
    """
    获取设备的方法映射列表
    返回:
    {
        "code": 200,
        "data": {
            "method_mappings": [
                {
                    "id": "uuid",
                    "direction": "downlink",
                    "raw_path": "building/hvac/command",
                    "standard_method": "set_temperature",
                    "extra": {"param": "setpoint_c"},
                    "protocol": "mqtt",
                    "created_at": "..."
                }
            ]
        }
    }
    """
    from src.Iot.dao import MethodMappingDAO
    from src.Iot.dao import DeviceDAO
    from src.Iot.exceptions import DeviceNotFoundError

    try:
        device = DeviceDAO.get_device_by_did(device_did)
        mappings = MethodMappingDAO.get_mappings_by_device(device_did, device.protocol)

        result = []
        for m in mappings:
            result.append({
                'id': m.id,
                'direction': m.direction,
                'raw_path': m.raw_path,
                'standard_method': m.standard_method,
                'extra': m.extra,
                'protocol': m.protocol,
                'created_at': m.created_at.isoformat() if m.created_at else None
            })

        return Result.success(data={'method_mappings': result})
    except DeviceNotFoundError as e:
        return Result.error(message=str(e), code=404)
    except Exception as e:
        return Result.error(message=str(e), code=500)


# ==================== 16. 标准字段管理 ====================

@api_bp.route('/iot/standard-fields', methods=['POST'])
@jwt_required
@require_permission('iot:write')
def create_standard_field():
    """
    创建标准字段

    请求体:
    {
        "field_code": "pm25",
        "field_name": "PM2.5",
        "field_type": "float",
        "unit": "μg/m³",
        "description": "细颗粒物浓度",
        "min_value": 0,
        "max_value": 500,
        "is_critical": true,
        "extra": {"threshold": 75, "alert_level": "warning"}
    }
    """
    log_sensitive_api("iot.standard_field.create", category="iot")
    from src.Iot.dao import StandardFieldDAO
    from src.Iot.models import IMSStandardField

    data = request.get_json()

    if not data or 'field_code' not in data or 'field_name' not in data or 'field_type' not in data:
        return Result.error(message="缺少必填字段: field_code, field_name, field_type", code=400)

    # 检查是否已存在
    existing = StandardFieldDAO.get_field_by_code(data['field_code'])
    if existing:
        return Result.error(message=f"标准字段已存在: {data['field_code']}", code=400)

    try:
        field = StandardFieldDAO.create_field(data)
        return Result.success(data={
            'id': field.id,
            'field_code': field.field_code,
            'field_name': field.field_name,
            'field_type': field.field_type,
            'unit': field.unit,
            'description': field.description,
            'min_value': float(field.min_value) if field.min_value else None,
            'max_value': float(field.max_value) if field.max_value else None,
            'is_critical': field.is_critical,
            'created_at': field.created_at.isoformat() if field.created_at else None
        }, message="标准字段创建成功")
    except Exception as e:
        return Result.error(message=str(e), code=500)


@api_bp.route('/iot/standard-fields/<string:field_code>', methods=['PUT'])
@jwt_required
@require_permission('iot:write')
def update_standard_field(field_code: str):
    """
    更新标准字段

    请求体:
    {
        "field_name": "PM2.5浓度",
        "field_type": "float",
        "unit": "μg/m³",
        "description": "细颗粒物浓度",
        "min_value": 0,
        "max_value": 500,
        "is_critical": true,
        "extra": {"threshold": 75, "alert_level": "warning"}
    }
    """
    log_sensitive_api("iot.standard_field.update", category="iot")
    from src.Iot.dao import StandardFieldDAO

    data = request.get_json()

    if not data:
        return Result.error(message="请求体不能为空", code=400)

    try:
        field = StandardFieldDAO.get_field_by_code(field_code)
        if not field:
            return Result.error(message=f"标准字段不存在: {field_code}", code=404)

        # 允许更新的字段
        allowed_fields = ['field_name', 'field_type', 'unit', 'description',
                          'min_value', 'max_value', 'is_critical', 'extra']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}

        updated_field = StandardFieldDAO.update_field(field.id, update_data)

        return Result.success(data={
            'field_code': updated_field.field_code,
            'field_name': updated_field.field_name,
            'field_type': updated_field.field_type,
            'unit': updated_field.unit,
            'description': updated_field.description,
            'min_value': float(updated_field.min_value) if updated_field.min_value else None,
            'max_value': float(updated_field.max_value) if updated_field.max_value else None,
            'is_critical': updated_field.is_critical,
            'updated_at': updated_field.updated_at.isoformat() if updated_field.updated_at else None
        }, message="标准字段更新成功")
    except Exception as e:
        return Result.error(message=str(e), code=500)


@api_bp.route('/iot/standard-fields/<string:field_code>', methods=['DELETE'])
@jwt_required
@require_permission('iot:write')
def delete_standard_field(field_code: str):
    """
    删除标准字段
    """
    log_sensitive_api("iot.standard_field.delete", category="iot")
    from src.Iot.dao import StandardFieldDAO

    try:
        field = StandardFieldDAO.get_field_by_code(field_code)
        if not field:
            return Result.error(message=f"标准字段不存在: {field_code}", code=404)

        StandardFieldDAO.delete_field(field.id)
        return Result.success(message=f"标准字段删除成功: {field_code}")
    except ValueError as e:
        return Result.error(message=str(e), code=400)
    except Exception as e:
        return Result.error(message=str(e), code=500)



# ====================16.标准方法管理 ====================

@api_bp.route('/iot/standard-methods', methods=['POST'])
@jwt_required
@require_permission('iot:write')
def create_standard_method():
    """
    创建标准方法

    请求体:
    {
        "method_code": "set_humidity",
        "method_name": "设置湿度",
        "description": "设置设备的目标湿度",
        "category": "control",
        "params_schema": {
            "type": "object",
            "required": ["value"],
            "properties": {
                "value": {"type": "number", "description": "目标湿度(%)", "minimum": 30, "maximum": 80}
            }
        },
        "response_schema": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "current_humidity": {"type": "number"}
            }
        }
    }
    """
    log_sensitive_api("iot.standard_method.create", category="iot")
    from src.Iot.models import IMSStandardMethod
    from src.common.core.database import db
    from src.Iot.dao import StandardMethodDAO

    data = request.get_json()

    if not data or 'method_code' not in data or 'method_name' not in data:
        return Result.error(message="缺少必填字段: method_code, method_name", code=400)

    # 检查是否已存在
    existing = StandardMethodDAO.get_by_code(data['method_code'])
    if existing:
        return Result.error(message=f"标准方法已存在: {data['method_code']}", code=400)

    try:
        method = IMSStandardMethod(
            method_code=data['method_code'],
            method_name=data['method_name'],
            description=data.get('description'),
            category=data.get('category'),
            params_schema=data.get('params_schema'),
            response_schema=data.get('response_schema'),
            is_active=data.get('is_active', True),
            extra=data.get('extra')
        )
        db.session.add(method)
        db.session.commit()

        return Result.success(data={
            'method_code': method.method_code,
            'method_name': method.method_name,
            'description': method.description,
            'category': method.category,
            'params_schema': method.params_schema,
            'response_schema': method.response_schema,
            'created_at': method.created_at.isoformat() if method.created_at else None
        }, message="标准方法创建成功")
    except Exception as e:
        db.session.rollback()
        return Result.error(message=str(e), code=500)


@api_bp.route('/iot/standard-methods/<string:method_code>', methods=['PUT'])
@jwt_required
@require_permission('iot:write')
def update_standard_method(method_code: str):
    """
    更新标准方法

    请求体:
    {
        "method_name": "设置湿度",
        "description": "设置设备的目标湿度",
        "category": "control",
        "params_schema": {...},
        "response_schema": {...},
        "is_active": true
    }
    """
    log_sensitive_api("iot.standard_method.update", category="iot")
    from src.Iot.dao import StandardMethodDAO

    data = request.get_json()

    if not data:
        return Result.error(message="请求体不能为空", code=400)

    try:
        method = StandardMethodDAO.get_by_code(method_code)
        if not method:
            return Result.error(message=f"标准方法不存在: {method_code}", code=404)

        # 允许更新的字段
        allowed_fields = ['method_name', 'description', 'category',
                          'params_schema', 'response_schema', 'is_active', 'extra']
        for field in allowed_fields:
            if field in data:
                setattr(method, field, data[field])

        from src.common.core.database import db
        db.session.commit()

        return Result.success(data={
            'method_code': method.method_code,
            'method_name': method.method_name,
            'description': method.description,
            'category': method.category,
            'params_schema': method.params_schema,
            'response_schema': method.response_schema,
            'is_active': method.is_active,
            'updated_at': method.updated_at.isoformat() if method.updated_at else None
        }, message="标准方法更新成功")
    except Exception as e:
        return Result.error(message=str(e), code=500)


@api_bp.route('/iot/standard-methods/<string:method_code>', methods=['DELETE'])
@jwt_required
@require_permission('iot:write')
def delete_standard_method(method_code: str):
    """
    删除标准方法
    """
    log_sensitive_api("iot.standard_method.delete", category="iot")
    from src.Iot.dao import StandardMethodDAO
    from src.common.core.database import db

    try:
        method = StandardMethodDAO.get_by_code(method_code)
        if not method:
            return Result.error(message=f"标准方法不存在: {method_code}", code=404)

        # 检查是否被设备方法映射引用
        from src.Iot.models import IMSMethodMapping
        ref_count = IMSMethodMapping.query.filter_by(standard_method=method_code).count()
        if ref_count > 0:
            return Result.error(message=f"标准方法已被 {ref_count} 个设备方法映射引用，无法删除", code=400)

        db.session.delete(method)
        db.session.commit()
        return Result.success(message=f"标准方法删除成功: {method_code}")
    except Exception as e:
        db.session.rollback()
        return Result.error(message=str(e), code=500)

@api_bp.route('/iot/ingest/http', methods=['POST'])
@jwt_required
@require_permission('iot:ingest')
def http_data_ingest():
    """
    HTTP 设备主动上报数据接口
    设备通过 POST 请求发送数据到此端点
    """
    log_sensitive_api("iot.ingest.http", category="iot")
    from src.Iot.device_manager import get_device_manager
    from src.Iot.dao import DeviceDAO
    from src.Iot.drivers import DriverRegistry
    from src.common.models.response import Result
    from datetime import datetime
    from flask import request

    try:
        data = request.json
        if not data:
            return Result.error(message="请求体为空")

        device_code = data.get('device_code')
        if not device_code:
            return Result.error(message="缺少 device_code")

        # 查找设备
        device = DeviceDAO.get_device_by_code(device_code)

        if not device:
            print(f"[HTTP Ingest] 拒绝: 设备未注册 - {device_code}")
            return Result.error(message=f"设备未注册: {device_code}")

        if device.protocol != 'http':
            return Result.error(message=f"设备协议不匹配，期望 http，实际 {device.protocol}")

        payload = data.get('data', {})
        if not payload:
            return Result.error(message="缺少 data 字段")

        if 'timestamp' not in payload:
            payload['timestamp'] = datetime.now().isoformat()

        # 🆕 通过 HTTP 驱动处理数据（统一使用驱动的回调机制）
        try:
            driver = DriverRegistry.get_driver('http')
            driver.ingest_data(device.did, payload)
        except Exception as e:
            print(f"[HTTP Ingest] 驱动处理失败: {e}")
            # 降级：直接调用 DeviceManager
            from src.Iot.device_manager import get_device_manager
            dm = get_device_manager()
            dm._on_device_data(device.did, payload, 'http')

        print(f"[HTTP Ingest] ✅ 设备 {device_code} 数据已接收")

        return Result.success(message="数据已接收", data={
            'device_code': device_code,
            'received_at': datetime.now().isoformat()
        })

    except Exception as e:
        print(f"[HTTP Ingest] ❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return Result.error(message=str(e))


@api_bp.route('/iot/device/<string:device_code>/reconnect', methods=['POST'])
@jwt_required
@require_permission('device:control')
def reconnect_device(device_code: str):
    """手动重连设备"""
    from src.Iot.device_manager import get_device_manager
    from src.Iot.dao import DeviceDAO

    device = DeviceDAO.get_device_by_code(device_code)
    if not device:
        return Result.error(message="设备不存在", code=404)

    dm = get_device_manager()

    # 断开现有连接
    if device.did in dm.drivers:
        driver = dm.drivers[device.did]
        driver.disconnect(device.did)
        del dm.drivers[device.did]

    # 重新连接
    dm._connect_device({
        'did': device.did,
        'device_name': device.device_name,
        'device_code': device.device_code,
        'protocol': device.protocol,
        'connect_config': device.connect_config
    })

    return Result.success(message="重连指令已发送")