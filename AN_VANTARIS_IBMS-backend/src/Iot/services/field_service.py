# src/iot/services/field_service.py
from typing import Dict, List, Optional
from src.Iot.dao import FieldMappingDAO
from src.Iot.exceptions import FieldMappingNotFoundError


class FieldMappingService:
    """字段映射服务"""

    @staticmethod
    def create_mapping(did: str, protocol: str, raw_field: str,
                       standard_field: str, transform: Optional[str] = None) -> dict:
        """创建字段映射"""
        mapping_data = {
            'did': did,
            'protocol': protocol,
            'raw_field': raw_field,
            'standard_field': standard_field,
            'transform': transform
        }
        mapping = FieldMappingDAO.create_mapping(mapping_data)
        return {
            'id': mapping.id,
            'did': mapping.did,
            'protocol': mapping.protocol,
            'raw_field': mapping.raw_field,
            'standard_field': mapping.standard_field,
            'transform': mapping.transform
        }

    @staticmethod
    def get_device_mappings(did: str, protocol: Optional[str] = None) -> List[dict]:
        """获取设备的所有字段映射"""
        mappings = FieldMappingDAO.get_mappings_by_device(did, protocol)
        return [
            {
                'id': m.id,
                'did': m.did,
                'protocol': m.protocol,
                'raw_field': m.raw_field,
                'standard_field': m.standard_field,
                'transform': m.transform
            }
            for m in mappings
        ]

    @staticmethod
    def delete_mapping(mapping_id: str):
        """删除字段映射"""
        FieldMappingDAO.delete_mapping(mapping_id)

    @staticmethod
    def batch_create_mappings(did: str, mappings: List[dict]) -> List[dict]:
        """批量创建字段映射"""
        mapping_list = []
        for mapping in mappings:
            mapping['did'] = did
            mapping_list.append(mapping)

        created = FieldMappingDAO.batch_create(mapping_list)
        return [
            {
                'id': m.id,
                'raw_field': m.raw_field,
                'standard_field': m.standard_field
            }
            for m in created
        ]