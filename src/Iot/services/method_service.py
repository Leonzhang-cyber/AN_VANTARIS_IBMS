# src/iot/services/method_service.py
from typing import Dict, List, Optional
from src.Iot.dao import MethodMappingDAO
from src.Iot.exceptions import MethodMappingNotFoundError


class MethodMappingService:
    """方法映射服务"""

    @staticmethod
    def create_mapping(did: str, protocol: str, direction: str,
                       raw_path: str, standard_method: str) -> dict:
        """创建方法映射"""
        mapping_data = {
            'did': did,
            'protocol': protocol,
            'direction': direction,
            'raw_path': raw_path,
            'standard_method': standard_method
        }
        mapping = MethodMappingDAO.create_mapping(mapping_data)
        return {
            'id': mapping.id,
            'did': mapping.did,
            'protocol': mapping.protocol,
            'direction': mapping.direction,
            'raw_path': mapping.raw_path,
            'standard_method': mapping.standard_method
        }

    @staticmethod
    def get_device_mappings(did: str, protocol: Optional[str] = None,
                            direction: Optional[str] = None) -> List[dict]:
        """获取设备的所有方法映射"""
        mappings = MethodMappingDAO.get_mappings_by_device(did, protocol, direction)
        return [
            {
                'id': m.id,
                'did': m.did,
                'protocol': m.protocol,
                'direction': m.direction,
                'raw_path': m.raw_path,
                'standard_method': m.standard_method
            }
            for m in mappings
        ]

    @staticmethod
    def get_method_by_path(did: str, protocol: str, direction: str,
                           raw_path: str) -> Optional[str]:
        """根据原始路径获取标准方法名"""
        mapping = MethodMappingDAO.get_mapping(did, protocol, direction, raw_path)
        return mapping.standard_method if mapping else None

    @staticmethod
    def delete_mapping(mapping_id: str):
        """删除方法映射"""
        MethodMappingDAO.delete_mapping(mapping_id)