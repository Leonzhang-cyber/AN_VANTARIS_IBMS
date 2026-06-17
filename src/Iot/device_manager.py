# src/Iot/device_manager.py

import threading
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from src.Iot import DeviceDAO, ProtocolNotFoundError
from src.Iot.drivers import DriverRegistry
from src.Iot.drivers.base_driver import BaseProtocolDriver
from src.Iot.exceptions import DeviceNotFoundError
from src.api.iot.sse_api import push_to_device

# 🆕 导入数据建模模块
from src.data_modeling.csv_storage import csv_storage
from src.data_modeling.config import DATA_MODELING_CONFIG


class DeviceManager:
    """设备管理器 - 单例模式"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self.devices: Dict[str, Dict] = {}
        self.drivers: Dict[str, Any] = {}
        self.running = False
        self.app = None

    def set_app(self, app):
        self.app = app

    def _apply_transform(self, value, transform: str):
        """应用转换规则"""
        if not transform:
            return value
        try:
            if transform.startswith('*'):
                return float(value) * float(transform[1:])
            elif transform.startswith('/'):
                return float(value) / float(transform[1:])
            elif transform.startswith('+'):
                return float(value) + float(transform[1:])
            elif transform.startswith('-'):
                return float(value) - float(transform[1:])
            else:
                return value
        except:
            return value

    def _apply_field_mapping(self, device_did: str, protocol: str, payload: Dict) -> Dict:
        """
        应用标准字段映射 - 只负责字段名转换，不添加元数据

        输入: {'temperature_c': 23.1, 'humidity_percent': 47.5, 'status_code': 0}
        输出: {'temperature': 23.1, 'humidity': 47.5, 'error_code': 0}
        """
        from src.Iot.dao import FieldMappingDAO

        if not self.app:
            return payload.copy()

        with self.app.app_context():
            mappings = FieldMappingDAO.get_mappings_by_device(device_did, protocol)

            # 没有配置映射，直接透传
            if not mappings:
                print(f"[Mapping] ⚠️ 设备 {device_did} 没有配置字段映射，直接透传")
                return payload.copy()

            # 应用映射
            mapped_result = {}
            for mapping in mappings:
                raw_field = mapping.raw_field
                if raw_field in payload:
                    value = payload[raw_field]
                    if mapping.transform:
                        value = self._apply_transform(value, mapping.transform)
                    mapped_result[mapping.standard_field] = value

            return mapped_result

    def _save_to_csv_for_analysis(self, device_did: str, mapped_data: Dict):
        """将数据保存到CSV用于数据分析"""
        try:
            if not self.app:
                return

            with self.app.app_context():
                device = DeviceDAO.get_device_by_did(device_did)
                if not device:
                    return

                if hasattr(device, 'device_code') and device.device_code:
                    device_code = device.device_code
                else:
                    return

                extra = device.extra or {}
                enable_data_analysis = extra.get('enable_data_analysis', False)

                if not enable_data_analysis:
                    return

                filtered_data = {}
                for key, value in mapped_data.items():
                    if not key.startswith('_'):
                        filtered_data[key] = value

                if filtered_data:
                    csv_storage.append_data(device_code, filtered_data)

        except Exception as e:
            print(f"[CSV] 异常: {e}")

    def _on_device_data(self, device_did: str, raw_data: Any, protocol: str):
        """
        设备数据回调 - 先做字段映射，再通过 SSE 推送到前端
        """
        device_info = self.devices.get(device_did, {})
        device_code = device_info.get('device_code', 'unknown')

        # ===== 视频帧直接透传 =====
        if isinstance(raw_data, dict) and raw_data.get('type') == 'video_frame':
            try:
                push_to_device(device_code, raw_data)
            except Exception as e:
                print(f"[DeviceManager] ❌ SSE 推送失败: {e}")
            return

        # ===== 提取实际数据 payload =====
        if isinstance(raw_data, dict):
            if 'payload' in raw_data and isinstance(raw_data['payload'], dict):
                payload = raw_data['payload']
            elif 'data' in raw_data and isinstance(raw_data['data'], dict):
                payload = raw_data['data']
            else:
                payload = raw_data
        else:
            payload = raw_data

        print("=" * 60)
        print(f"[映射前] device_did: {device_did}")
        print(f"[映射前] protocol: {protocol}")
        print(f"[映射前] payload: {payload}")

        # 1. 字段映射（只返回业务数据，不添加元数据）
        mapped_data = self._apply_field_mapping(device_did, protocol, payload)

        print(f"[映射后] mapped_data: {mapped_data}")
        print("=" * 60)

        # 2. 保存到CSV（如果需要）
        self._save_to_csv_for_analysis(device_did, mapped_data)

        # 3. 构建 SSE 推送数据（元数据在外层，data 只包含业务数据）
        push_data = {
            'type': 'device_data',
            'device_code': device_code,
            'device_did': device_did,
            'timestamp': datetime.now().isoformat(),
            'data': mapped_data  # ✅ 只有业务数据，没有重复
        }

        # 4. SSE 推送
        try:
            push_to_device(device_code, push_data)
            print(f"[SSE] ✅ 已推送: {device_code}")
        except Exception as e:
            print(f"[SSE] ❌ 推送失败: {e}")

    def _on_device_status(self, device_did: str, status: str, protocol: str):
        """设备状态回调"""
        device_info = self.devices.get(device_did, {})
        device_code = device_info.get('device_code', 'unknown')

        status_data = {
            'type': 'device_status',
            'device_code': device_code,
            'device_did': device_did,
            'status': status,
            'timestamp': datetime.now().isoformat()
        }
        try:
            push_to_device(device_code, status_data)
        except Exception as e:
            pass

        try:
            if self.app:
                with self.app.app_context():
                    if status == 'online':
                        DeviceDAO.update_device_status(device_did, 1)
                    elif status == 'offline':
                        DeviceDAO.update_device_status(device_did, 0)
                    elif status == 'error':
                        DeviceDAO.update_device_status(device_did, 2)
        except Exception as e:
            pass

    def start(self):
        print("\n" + "=" * 60)
        print("🚀 IoT 设备管理器启动")
        print("=" * 60)

        available_drivers = DriverRegistry.list_drivers()
        print(f"📦 驱动: {available_drivers}")

        self.running = True
        self._load_and_connect_devices()
        self._print_startup_summary()
        print("\n✅ 设备管理器已启动\n")

    def _load_and_connect_devices(self):
        try:
            result = DeviceDAO.list_devices(page=1, per_page=1000)
            all_devices = result['items']

            device_dicts = []
            for device in all_devices:
                device_dict = {
                    'did': device.did,
                    'device_name': device.device_name,
                    'device_code': device.device_code,
                    'protocol': device.protocol,
                    'connect_config': device.connect_config,
                    'status': device.status,
                }
                device_dicts.append(device_dict)

            for device_dict in device_dicts:
                self._connect_device(device_dict)
        except Exception as e:
            print(f"❌ 加载失败: {e}")

    def _connect_device(self, device: Dict) -> bool:
        device_did = device.get('did')
        device_code = device.get('device_code', '未知')
        protocol = device.get('protocol', '')
        connect_config = device.get('connect_config', {})
        connect_config['device_code'] = device_code

        try:
            driver = DriverRegistry.get_driver(protocol)
            driver.register_data_callback(self._on_device_data)
            driver.register_status_callback(self._on_device_status)

            success = driver.connect(device_did, connect_config)

            if success:
                self.devices[device_did] = device
                self.drivers[device_did] = driver
                print(f"   ✅ {device_code}")
                return True
            else:
                print(f"   ❌ {device_code}")
                return False
        except Exception as e:
            return False

    def _print_startup_summary(self):
        print("\n" + "=" * 60)
        print(f"📊 已注册设备: {len(self.devices)} 台")
        for did, info in self.devices.items():
            print(f"   ✅ {info.get('device_code')} | {info.get('protocol')}")
        print("=" * 60)

    def send_command(self, device_did: str, command: Dict) -> Dict:
        """下发命令到设备"""
        if device_did not in self.drivers:
            return {'success': False, 'error': '设备未连接'}
        try:
            driver = self.drivers[device_did]
            return driver.send_command(device_did, command)
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def list_connected_devices(self) -> List[Dict]:
        return [
            {
                'did': did,
                'device_code': info.get('device_code'),
                'device_name': info.get('device_name'),
                'protocol': info.get('protocol')
            }
            for did, info in self.devices.items()
        ]


_device_manager = None


def get_device_manager() -> DeviceManager:
    global _device_manager
    if _device_manager is None:
        _device_manager = DeviceManager()
    return _device_manager