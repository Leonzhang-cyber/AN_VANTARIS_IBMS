# src/Iot/services/device_service.py
"""
IoT 设备注册服务
负责保存前端传入的设备信息到数据库
"""

from typing import Dict, Any

from src.Iot.dao import DeviceDAO, FieldMappingDAO, MethodMappingDAO
from src.Iot.exceptions import DeviceRegistrationError


class DeviceService:
    """
    设备注册服务 - 保存设备信息到数据库
    注意：设备主体注册由前端调用DID模块完成，本服务只负责存储设备扩展信息
    """

    def __init__(self):
        pass

    def register_device(self, device_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        注册设备：保存设备信息到数据库

        :param device_info: 设备信息，包含：
            - device_name: 设备名称（必填）
            - device_code: 设备编号（必填，唯一）
            - did: 设备DID（必填，由DID模块生成）
            - public_key: 设备公钥（必填，由DID模块生成）
            - private_key: 设备私钥（必填，由DID模块生成）
            - vc_json: 设备VC（必填，由DID模块签发）
            - parent_did: 父实体DID（必填）
            - protocol: 通讯协议（必填）
            - connect_config: 连接配置（可选）
            - field_mappings: 字段映射（可选）
            - method_mappings: 方法映射（可选）
            - extra: 扩展信息（可选）

        :return: 保存的设备信息
        """
        try:
            # 验证必填字段
            required_fields = ['device_name', 'device_code', 'did', 'public_key',
                               'private_key', 'vc_json', 'parent_did', 'protocol']
            for field in required_fields:
                if field not in device_info:
                    raise DeviceRegistrationError(f"缺少必填字段: {field}")

            # ========== 步骤1: 准备设备表数据 ==========
            device_data = {
                'device_name': device_info['device_name'],
                'device_code': device_info['device_code'],
                'did': device_info['did'],
                'public_key': device_info['public_key'],
                'private_key': device_info['private_key'],
                'vc_json': device_info['vc_json'],
                'parent_did': device_info['parent_did'],
                'protocol': device_info['protocol'],
                'connect_config': device_info.get('connect_config', {}),
                'status': 0,  # 初始状态：离线
                'extra': device_info.get('extra', {})
            }

            # ========== 步骤2: 保存设备主表 ==========
            device = DeviceDAO.create_device(device_data)

            # ========== 步骤3: 保存字段映射（如果有） ==========
            if device_info.get('field_mappings'):
                for mapping in device_info['field_mappings']:
                    mapping_data = {
                        'did': device_info['did'],
                        'protocol': device_info['protocol'],
                        'raw_field': mapping['raw_field'],
                        'standard_field': mapping['standard_field'],
                        'transform': mapping.get('transform'),
                        'extra': mapping.get('extra')
                    }
                    FieldMappingDAO.create_mapping(mapping_data)

            # ========== 步骤4: 保存方法映射（如果有） ==========
            if device_info.get('method_mappings'):
                for mapping in device_info['method_mappings']:
                    mapping_data = {
                        'did': device_info['did'],
                        'protocol': device_info['protocol'],
                        'direction': mapping['direction'],
                        'raw_path': mapping['raw_path'],
                        'standard_method': mapping['standard_method'],
                        'extra': mapping.get('extra')
                    }
                    MethodMappingDAO.create_mapping(mapping_data)

            # ========== 步骤5: 返回保存结果 ==========
            return {
                'device': {
                    'id': device.id,
                    'did': device.did,
                    'device_code': device.device_code,
                    'device_name': device.device_name,
                    'protocol': device.protocol,
                    'status': device.status,
                    'parent_did': device.parent_did,
                    'created_at': device.created_at.isoformat() if device.created_at else None
                }
            }

        except Exception as e:
            raise DeviceRegistrationError(f"设备注册失败: {str(e)}")

    def get_devices_by_parent(
            self,
            parent_did: str,
            page: int = 1,
            per_page: int = 20,
            status: int = None,
            protocol: str = None
    ) -> Dict[str, Any]:
        """
        根据父DID查询设备列表

        :param parent_did: 父实体DID
        :param page: 页码
        :param per_page: 每页数量
        :param status: 状态过滤
        :param protocol: 协议过滤
        :return: 分页结果
        """
        filters = {
            'parent_did': parent_did
        }
        if status is not None:
            filters['status'] = status
        if protocol:
            filters['protocol'] = protocol

        result = DeviceDAO.list_devices(page, per_page, filters)

        return {
            'items': [
                {
                    'id': d.id,
                    'did': d.did,
                    'device_code': d.device_code,
                    'device_name': d.device_name,
                    'protocol': d.protocol,
                    'status': d.status,
                    'parent_did': d.parent_did,
                    'created_at': d.created_at.isoformat() if d.created_at else None,
                    'updated_at': d.updated_at.isoformat() if d.updated_at else None
                }
                for d in result['items']
            ],
            'total': result['total'],
            'page': result['page'],
            'per_page': result['per_page'],
            'pages': result['pages']
        }

    def get_device_detail(self, device_did: str) -> Dict[str, Any]:
        """
        获取设备详细信息（包含字段映射和方法映射）

        :param device_did: 设备DID
        :return: 设备详细信息
        """
        device = DeviceDAO.get_device_by_did(device_did)

        # 获取字段映射
        field_mappings = FieldMappingDAO.get_mappings_by_device(device_did)

        # 获取方法映射
        method_mappings = MethodMappingDAO.get_mappings_by_device(device_did)

        return {
            'id': device.id,
            'did': device.did,
            'device_code': device.device_code,
            'device_name': device.device_name,
            'public_key': device.public_key,
            'vc_json': device.vc_json,
            'parent_did': device.parent_did,
            'protocol': device.protocol,
            'connect_config': device.connect_config,
            'status': device.status,
            'extra': device.extra,
            'field_mappings': [
                {
                    'id': m.id,
                    'raw_field': m.raw_field,
                    'standard_field': m.standard_field,
                    'transform': m.transform
                }
                for m in field_mappings if m.did == device_did
            ],
            'method_mappings': [
                {
                    'id': m.id,
                    'direction': m.direction,
                    'raw_path': m.raw_path,
                    'standard_method': m.standard_method
                }
                for m in method_mappings if m.did == device_did
            ],
            'created_at': device.created_at.isoformat() if device.created_at else None,
            'updated_at': device.updated_at.isoformat() if device.updated_at else None
        }

    def get_device_by_code(self, device_code: str) -> Dict[str, Any]:
        """
        根据设备编号获取设备基本信息

        :param device_code: 设备编号
        :return: 设备基本信息
        """
        device = DeviceDAO.get_device_by_code(device_code)

        return {
            'id': device.id,
            'did': device.did,
            'device_code': device.device_code,
            'device_name': device.device_name,
            'protocol': device.protocol,
            'status': device.status,
            'parent_did': device.parent_did,
            'created_at': device.created_at.isoformat() if device.created_at else None,
            'updated_at': device.updated_at.isoformat() if device.updated_at else None
        }

    def update_device(self, device_did: str, update_data: dict) -> Dict[str, Any]:
        """
        更新设备信息

        :param device_did: 设备DID
        :param update_data: 要更新的数据
        :return: 更新后的设备信息
        """
        # 允许更新的字段
        allowed_fields = ['device_name', 'connect_config', 'extra', 'status']
        filtered_data = {k: v for k, v in update_data.items() if k in allowed_fields}

        if not filtered_data:
            raise DeviceRegistrationError("没有可更新的字段")

        device = DeviceDAO.update_device(device_did, filtered_data)

        return {
            'did': device.did,
            'device_name': device.device_name,
            'protocol': device.protocol,
            'status': device.status,
            'updated_at': device.updated_at.isoformat() if device.updated_at else None
        }

    def patch_device(self, device_did: str, patch_data: dict) -> Dict[str, Any]:
        """
        部分更新设备信息（同 update_device，保留作为别名）
        """
        return self.update_device(device_did, patch_data)

    def update_device_field_mappings(self, device_did: str, field_mappings: list) -> Dict[str, Any]:
        """
        更新设备的字段映射（先删除旧的，再创建新的）

        :param device_did: 设备DID
        :param field_mappings: 新的字段映射列表
        :return: 更新后的映射信息
        """
        # 检查设备是否存在
        device = DeviceDAO.get_device_by_did(device_did)

        # 删除旧的字段映射
        FieldMappingDAO.delete_by_device(device_did, device.protocol)

        # 创建新的字段映射
        new_mappings = []
        for mapping in field_mappings:
            mapping_data = {
                'did': device_did,
                'protocol': device.protocol,
                'raw_field': mapping['raw_field'],
                'standard_field': mapping['standard_field'],
                'transform': mapping.get('transform'),
                'extra': mapping.get('extra')
            }
            new_mapping = FieldMappingDAO.create_mapping(mapping_data)
            new_mappings.append({
                'id': new_mapping.id,
                'raw_field': new_mapping.raw_field,
                'standard_field': new_mapping.standard_field,
                'transform': new_mapping.transform
            })

        return {
            'did': device_did,
            'field_mappings': new_mappings,
            'count': len(new_mappings)
        }

    def update_device_method_mappings(self, device_did: str, method_mappings: list) -> Dict[str, Any]:
        """
        更新设备的方法映射（先删除旧的，再创建新的）

        :param device_did: 设备DID
        :param method_mappings: 新的方法映射列表
        :return: 更新后的映射信息
        """
        # 检查设备是否存在
        device = DeviceDAO.get_device_by_did(device_did)

        # 删除旧的方法映射
        MethodMappingDAO.delete_by_device(device_did, device.protocol)

        # 创建新的方法映射
        new_mappings = []
        for mapping in method_mappings:
            mapping_data = {
                'did': device_did,
                'protocol': device.protocol,
                'direction': mapping['direction'],
                'raw_path': mapping['raw_path'],
                'standard_method': mapping['standard_method'],
                'extra': mapping.get('extra')
            }
            new_mapping = MethodMappingDAO.create_mapping(mapping_data)
            new_mappings.append({
                'id': new_mapping.id,
                'direction': new_mapping.direction,
                'raw_path': new_mapping.raw_path,
                'standard_method': new_mapping.standard_method
            })

        return {
            'did': device_did,
            'method_mappings': new_mappings,
            'count': len(new_mappings)
        }

    def delete_device(self, device_did: str) -> bool:
        """
        删除设备（同时删除关联的字段映射和方法映射）
        """
        # 先删除字段映射
        FieldMappingDAO.delete_by_device(device_did)

        # 再删除方法映射
        MethodMappingDAO.delete_by_device(device_did)

        # 最后删除设备
        DeviceDAO.delete_device(device_did)

        return True

    def update_device_status(self, device_did: str, status: int) -> Dict[str, Any]:
        """
        更新设备状态

        :param device_did: 设备DID
        :param status: 状态值（0离线/1在线/2异常）
        :return: 更新后的状态信息
        """
        try:
            device = DeviceDAO.update_device_status(device_did, status)
            return {
                'did': device.did,
                'status': device.status,
                'updated_at': device.updated_at.isoformat() if device.updated_at else None
            }
        except DeviceNotFoundError:
            raise
        except Exception as e:
            raise DeviceRegistrationError(f"更新设备状态失败: {str(e)}")