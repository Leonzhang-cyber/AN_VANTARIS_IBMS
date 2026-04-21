# src/Iot/services/data_service.py
from typing import Dict, Any, Optional
from datetime import datetime
import json

from src.Iot.dao import FieldMappingDAO
from src.Iot.exceptions import DataParseError


class DataService:
    """设备数据服务 - 接收、解析、存储设备数据"""

    def __init__(self):
        self.data_buffer = []  # 数据缓冲区（可用于批量写入）

    def process_device_data(self, device_did: str, protocol: str,
                            raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理设备上报数据
        1. 解析原始数据
        2. 应用字段映射
        3. 返回结构化数据
        """
        try:
            # 获取字段映射
            mappings = FieldMappingDAO.get_mappings_by_device(device_did, protocol)

            # 提取payload
            payload = raw_data.get('payload', raw_data)

            # 解析数据
            parsed_data = self._parse_with_mappings(payload, mappings)

            # 添加元数据
            parsed_data['_metadata'] = {
                'device_did': device_did,
                'protocol': protocol,
                'received_at': datetime.now().isoformat(),
                'raw_topic': raw_data.get('topic'),
                'raw_qos': raw_data.get('qos')
            }

            # 存储到数据库（可选）
            self._store_device_data(device_did, parsed_data)

            return parsed_data

        except Exception as e:
            raise DataParseError(f"数据解析失败: {str(e)}")

    def _parse_with_mappings(self, payload: Dict, mappings: list) -> Dict:
        """根据映射解析数据"""
        parsed = {}

        for mapping in mappings:
            raw_field = mapping.raw_field
            if raw_field in payload:
                value = payload[raw_field]

                # 应用转换规则
                if mapping.transform:
                    value = self._apply_transform(value, mapping.transform)

                parsed[mapping.standard_field] = value

        # 添加未映射的原始字段
        for key, value in payload.items():
            if key not in [m.raw_field for m in mappings]:
                parsed[f'_raw_{key}'] = value

        return parsed

    def _apply_transform(self, value, transform: str):
        """应用数据转换规则"""
        if not transform:
            return value

        try:
            if transform.startswith('*'):
                # 乘法：*0.1
                factor = float(transform[1:])
                return value * factor
            elif transform.startswith('/'):
                # 除法：/1000
                divisor = float(transform[1:])
                return value / divisor
            elif transform.startswith('+'):
                # 加法：+10
                addend = float(transform[1:])
                return value + addend
            elif transform.startswith('-'):
                # 减法：-5
                subtrahend = float(transform[1:])
                return value - subtrahend
            else:
                return value
        except (ValueError, TypeError):
            return value

    def _store_device_data(self, device_did: str, data: Dict[str, Any]):
        """存储设备数据到数据库"""
        # TODO: 实现数据存储逻辑
        # 可以存储到 imbs_device_data_log 表
        pass

    def is_critical_data(self, data: Dict[str, Any], thresholds: Dict) -> bool:
        """判断是否为关键数据（需要上链）"""
        for field, threshold in thresholds.items():
            if field in data:
                value = data[field]
                if isinstance(value, (int, float)) and value > threshold:
                    return True
        return False