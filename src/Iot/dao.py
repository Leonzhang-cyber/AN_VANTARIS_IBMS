# src/Iot/dao.py
from sqlalchemy import and_, or_
from sqlalchemy.sql import func
from src.common.core.database import db
from src.Iot.models import IMSDevice, IMSFieldMapping, IMSMethodMapping, IMSStandardField
from src.Iot.exceptions import DeviceNotFoundError, DuplicateDeviceError


class DeviceDAO:
    """设备数据访问层"""

    @staticmethod
    def create_device(device_data: dict) -> IMSDevice:
        """创建设备"""
        # 检查设备编号是否重复
        existing = IMSDevice.query.filter_by(device_code=device_data['device_code']).first()
        if existing:
            raise DuplicateDeviceError(f"设备编号已存在: {device_data['device_code']}")

        # 检查DID是否重复
        existing = IMSDevice.query.filter_by(did=device_data['did']).first()
        if existing:
            raise DuplicateDeviceError(f"设备DID已存在: {device_data['did']}")

        device = IMSDevice(**device_data)
        db.session.add(device)
        db.session.commit()
        return device

    @staticmethod
    def get_device_by_did(did: str) -> IMSDevice:
        """根据DID查询设备"""
        device = IMSDevice.query.filter_by(did=did).first()
        if not device:
            raise DeviceNotFoundError(f"设备不存在: {did}")
        return device

    @staticmethod
    def get_device_by_code(device_code: str) -> IMSDevice:
        """根据设备编号查询"""
        device = IMSDevice.query.filter_by(device_code=device_code).first()
        if not device:
            raise DeviceNotFoundError(f"设备不存在: {device_code}")
        return device

    @staticmethod
    def get_devices_by_protocol(protocol: str, status: int = None) -> list:
        """根据协议查询设备"""
        query = IMSDevice.query.filter_by(protocol=protocol)
        if status is not None:
            query = query.filter_by(status=status)
        return query.all()

    @staticmethod
    def update_device_status(did: str, status: int) -> IMSDevice:
        """更新设备状态"""
        device = DeviceDAO.get_device_by_did(did)
        device.status = status
        db.session.commit()
        return device

    @staticmethod
    def update_device(did: str, update_data: dict) -> IMSDevice:
        """更新设备信息"""
        device = DeviceDAO.get_device_by_did(did)
        for key, value in update_data.items():
            if hasattr(device, key):
                setattr(device, key, value)
        db.session.commit()
        return device

    @staticmethod
    def delete_device(did: str):
        """删除设备（软删除或硬删除）"""
        device = DeviceDAO.get_device_by_did(did)
        db.session.delete(device)
        db.session.commit()

    @staticmethod
    def list_devices(page: int = 1, per_page: int = 20, filters: dict = None) -> dict:
        """分页查询设备列表"""
        query = IMSDevice.query
        if filters:
            if filters.get('protocol'):
                query = query.filter_by(protocol=filters['protocol'])
            if filters.get('status') is not None:
                query = query.filter_by(status=filters['status'])
            if filters.get('parent_did'):
                query = query.filter_by(parent_did=filters['parent_did'])
            if filters.get('device_name'):
                query = query.filter(IMSDevice.device_name.like(f"%{filters['device_name']}%"))

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return {
            'items': pagination.items,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }

    @staticmethod
    def count_by_protocol() -> dict:
        """按协议统计设备数量"""
        results = db.session.query(
            IMSDevice.protocol,
            func.count(IMSDevice.id).label('count')
        ).group_by(IMSDevice.protocol).all()
        return {r[0]: r[1] for r in results}

    @staticmethod
    def count_by_status() -> dict:
        """按状态统计设备数量"""
        results = db.session.query(
            IMSDevice.status,
            func.count(IMSDevice.id).label('count')
        ).group_by(IMSDevice.status).all()
        status_map = {0: '离线', 1: '在线', 2: '异常'}
        return {status_map.get(r[0], str(r[0])): r[1] for r in results}


class StandardFieldDAO:
    """标准字段数据访问层"""

    @staticmethod
    def create_field(field_data: dict) -> IMSStandardField:
        """创建标准字段"""
        field = IMSStandardField(**field_data)
        db.session.add(field)
        db.session.commit()
        return field

    @staticmethod
    def get_field_by_id(field_id: str) -> IMSStandardField:
        """根据ID查询标准字段"""
        field = IMSStandardField.query.get(field_id)
        if not field:
            raise ValueError(f"标准字段不存在: {field_id}")
        return field

    @staticmethod
    def get_field_by_code(field_code: str) -> IMSStandardField:
        """根据字段编码查询"""
        return IMSStandardField.query.filter_by(field_code=field_code).first()

    @staticmethod
    def get_all_fields(page: int = 1, per_page: int = 50,
                       is_critical: bool = None, field_type: str = None) -> dict:
        """分页查询所有标准字段"""
        query = IMSStandardField.query

        if is_critical is not None:
            query = query.filter_by(is_critical=is_critical)
        if field_type:
            query = query.filter_by(field_type=field_type)

        query = query.order_by(IMSStandardField.field_code)
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            'items': pagination.items,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }

    @staticmethod
    def get_critical_fields() -> list:
        """获取所有关键数据字段"""
        return IMSStandardField.query.filter_by(is_critical=True).all()

    @staticmethod
    def update_field(field_id: str, update_data: dict) -> IMSStandardField:
        """更新标准字段"""
        field = StandardFieldDAO.get_field_by_id(field_id)
        for key, value in update_data.items():
            if hasattr(field, key) and key not in ['id', 'created_at']:
                setattr(field, key, value)
        db.session.commit()
        return field

    @staticmethod
    def delete_field(field_id: str) -> bool:
        """删除标准字段（检查是否被映射引用）"""
        field = StandardFieldDAO.get_field_by_id(field_id)

        # 检查是否被字段映射引用
        ref_count = IMSFieldMapping.query.filter_by(standard_field_id=field_id).count()
        if ref_count > 0:
            raise ValueError(f"标准字段已被 {ref_count} 个映射引用，无法删除")

        db.session.delete(field)
        db.session.commit()
        return True

    @staticmethod
    def batch_create_fields(fields_data: list) -> list:
        """批量创建标准字段"""
        created = []
        for field_data in fields_data:
            existing = StandardFieldDAO.get_field_by_code(field_data['field_code'])
            if existing:
                created.append(existing)
            else:
                created.append(StandardFieldDAO.create_field(field_data))
        return created

    @staticmethod
    def batch_update_fields(updates: list) -> list:
        """批量更新标准字段"""
        updated = []
        for update_data in updates:
            field_id = update_data.pop('id')
            field = StandardFieldDAO.update_field(field_id, update_data)
            updated.append(field)
        return updated

    @staticmethod
    def search_fields(keyword: str) -> list:
        """搜索标准字段（按编码、名称、描述）"""
        return IMSStandardField.query.filter(
            or_(
                IMSStandardField.field_code.like(f"%{keyword}%"),
                IMSStandardField.field_name.like(f"%{keyword}%"),
                IMSStandardField.description.like(f"%{keyword}%")
            )
        ).all()

    @staticmethod
    def get_fields_by_type(field_type: str) -> list:
        """根据字段类型获取标准字段"""
        return IMSStandardField.query.filter_by(field_type=field_type).all()

    @staticmethod
    def validate_field_value(field_code: str, value) -> dict:
        """
        验证字段值是否在有效范围内
        返回: {'valid': bool, 'message': str, 'is_critical': bool}
        """
        field = StandardFieldDAO.get_field_by_code(field_code)
        if not field:
            return {'valid': False, 'message': f'未知的标准字段: {field_code}', 'is_critical': False}

        # 类型检查
        if field.field_type in ['float', 'int']:
            try:
                num_value = float(value)

                # 范围检查
                if field.min_value is not None and num_value < float(field.min_value):
                    return {
                        'valid': False,
                        'message': f'{field.field_name} 值 {value} 低于最小值 {field.min_value}',
                        'is_critical': field.is_critical
                    }
                if field.max_value is not None and num_value > float(field.max_value):
                    # 超过阈值可能是告警
                    threshold = field.extra.get('threshold') if field.extra else None
                    if threshold and num_value > threshold:
                        return {
                            'valid': True,
                            'message': f'{field.field_name} 值 {value} 超过告警阈值 {threshold}',
                            'is_critical': field.is_critical,
                            'is_alert': True
                        }
                    return {
                        'valid': False,
                        'message': f'{field.field_name} 值 {value} 超过最大值 {field.max_value}',
                        'is_critical': field.is_critical
                    }
            except (ValueError, TypeError):
                return {
                    'valid': False,
                    'message': f'{field.field_name} 值类型错误，期望 {field.field_type}',
                    'is_critical': field.is_critical
                }

        return {'valid': True, 'message': '验证通过', 'is_critical': field.is_critical, 'is_alert': False}

    @staticmethod
    def get_field_with_mappings(field_code: str) -> dict:
        """获取标准字段及其关联的映射关系"""
        field = StandardFieldDAO.get_field_by_code(field_code)
        if not field:
            return None

        mappings = IMSFieldMapping.query.filter_by(standard_field_id=field.id).all()

        return {
            'field': field,
            'mappings': mappings,
            'mapping_count': len(mappings)
        }

    @staticmethod
    def get_statistics() -> dict:
        """获取标准字段统计信息"""
        total = IMSStandardField.query.count()
        critical = IMSStandardField.query.filter_by(is_critical=True).count()

        type_stats = db.session.query(
            IMSStandardField.field_type,
            func.count(IMSStandardField.id).label('count')
        ).group_by(IMSStandardField.field_type).all()

        return {
            'total_fields': total,
            'critical_fields': critical,
            'normal_fields': total - critical,
            'type_distribution': {r[0]: r[1] for r in type_stats}
        }


class FieldMappingDAO:
    """字段映射数据访问层"""

    @staticmethod
    @staticmethod
    def create_mapping(mapping_data: dict) -> IMSFieldMapping:
        """创建字段映射"""
        mapping_data.pop('standard_field_id', None)

        mapping = IMSFieldMapping(**mapping_data)
        db.session.add(mapping)
        db.session.commit()
        return mapping

    @staticmethod
    def get_mappings_by_device(did: str, protocol: str = None) -> list:
        """获取设备的字段映射（包含标准字段信息）"""
        query = IMSFieldMapping.query.filter(
            or_(
                IMSFieldMapping.did == did,
                IMSFieldMapping.did == '*'  # 全局映射
            )
        )
        if protocol:
            query = query.filter_by(protocol=protocol)

        mappings = query.all()

        # 为每个映射附加标准字段信息
        for mapping in mappings:
            if mapping.standard_field_id:
                mapping.standard_field_info = StandardFieldDAO.get_field_by_id(mapping.standard_field_id)

        return mappings

    @staticmethod
    def get_mapping(did: str, protocol: str, raw_field: str) -> IMSFieldMapping:
        """获取特定字段映射"""
        # 优先设备级，其次全局
        mapping = IMSFieldMapping.query.filter_by(
            did=did, protocol=protocol, raw_field=raw_field
        ).first()
        if not mapping:
            mapping = IMSFieldMapping.query.filter_by(
                did='*', protocol=protocol, raw_field=raw_field
            ).first()

        # 附加标准字段信息
        if mapping and mapping.standard_field_id:
            mapping.standard_field_info = StandardFieldDAO.get_field_by_id(mapping.standard_field_id)

        return mapping

    @staticmethod
    def delete_mapping(mapping_id: str):
        """删除映射"""
        mapping = IMSFieldMapping.query.get(mapping_id)
        if mapping:
            db.session.delete(mapping)
            db.session.commit()

    @staticmethod
    def batch_create(mappings: list) -> list:
        """批量创建映射"""
        created = []
        for mapping_data in mappings:
            created.append(FieldMappingDAO.create_mapping(mapping_data))
        return created

    @staticmethod
    def delete_by_device(did: str, protocol: str = None) -> int:
        """删除设备的所有映射"""
        query = IMSFieldMapping.query.filter_by(did=did)
        if protocol:
            query = query.filter_by(protocol=protocol)
        count = query.delete()
        db.session.commit()
        return count

    @staticmethod
    def get_global_mappings(protocol: str = None) -> list:
        """获取全局字段映射"""
        query = IMSFieldMapping.query.filter_by(did='*')
        if protocol:
            query = query.filter_by(protocol=protocol)
        return query.all()


class MethodMappingDAO:
    """方法映射数据访问层"""

    @staticmethod
    def create_mapping(mapping_data: dict) -> IMSMethodMapping:
        """创建方法映射"""
        mapping = IMSMethodMapping(**mapping_data)
        db.session.add(mapping)
        db.session.commit()
        return mapping

    @staticmethod
    def get_mappings_by_device(did: str, protocol: str = None, direction: str = None) -> list:
        """获取设备的方法映射"""
        query = IMSMethodMapping.query.filter(
            or_(
                IMSMethodMapping.did == did,
                IMSMethodMapping.did == '*'
            )
        )
        if protocol:
            query = query.filter_by(protocol=protocol)
        if direction:
            query = query.filter_by(direction=direction)
        return query.all()

    @staticmethod
    def get_mapping(did: str, protocol: str, direction: str, raw_path: str) -> IMSMethodMapping:
        """获取特定方法映射"""
        mapping = IMSMethodMapping.query.filter_by(
            did=did, protocol=protocol, direction=direction, raw_path=raw_path
        ).first()
        if not mapping:
            mapping = IMSMethodMapping.query.filter_by(
                did='*', protocol=protocol, direction=direction, raw_path=raw_path
            ).first()
        return mapping

    @staticmethod
    def get_mapping_by_standard(did: str, protocol: str, direction: str, standard_method: str) -> IMSMethodMapping:
        """根据标准方法名获取映射"""
        mapping = IMSMethodMapping.query.filter_by(
            did=did, protocol=protocol, direction=direction, standard_method=standard_method
        ).first()
        if not mapping:
            mapping = IMSMethodMapping.query.filter_by(
                did='*', protocol=protocol, direction=direction, standard_method=standard_method
            ).first()
        return mapping

    @staticmethod
    def delete_mapping(mapping_id: str):
        """删除方法映射"""
        mapping = IMSMethodMapping.query.get(mapping_id)
        if mapping:
            db.session.delete(mapping)
            db.session.commit()

    @staticmethod
    def delete_by_device(did: str, protocol: str = None) -> int:
        """删除设备的所有方法映射"""
        query = IMSMethodMapping.query.filter_by(did=did)
        if protocol:
            query = query.filter_by(protocol=protocol)
        count = query.delete()
        db.session.commit()
        return count

    @staticmethod
    def batch_create(mappings: list) -> list:
        """批量创建方法映射"""
        created = []
        for mapping_data in mappings:
            created.append(MethodMappingDAO.create_mapping(mapping_data))
        return created


# src/Iot/dao.py - 在文件末尾添加

class StandardMethodDAO:
    """标准方法数据访问层"""

    @staticmethod
    def get_by_code(method_code: str):
        """根据方法编码查询"""
        from src.Iot.models import IMSStandardMethod
        return IMSStandardMethod.query.filter_by(method_code=method_code, is_active=True).first()

    @staticmethod
    def get_all(category: str = None) -> list:
        """获取所有标准方法"""
        from src.Iot.models import IMSStandardMethod
        query = IMSStandardMethod.query.filter_by(is_active=True)
        if category:
            query = query.filter_by(category=category)
        return query.all()

    @staticmethod
    def get_methods_with_mappings(device_did: str, protocol: str) -> list:
        """获取设备支持的方法列表（带映射信息）"""
        from src.Iot.models import IMSStandardMethod, IMSMethodMapping

        results = []
        standard_methods = StandardMethodDAO.get_all()

        for method in standard_methods:
            mapping = IMSMethodMapping.query.filter_by(
                did=device_did,
                protocol=protocol,
                standard_method=method.method_code,
                direction='downlink'
            ).first()

            results.append({
                'method_code': method.method_code,
                'method_name': method.method_name,
                'description': method.description,
                'category': method.category,
                'params_schema': method.params_schema,
                'is_supported': mapping is not None,
                'mapping_id': mapping.id if mapping else None,
                'raw_path': mapping.raw_path if mapping else None,
                'extra': mapping.extra if mapping else None
            })

        return results