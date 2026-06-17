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

    def _apply_field_mapping(self, device_did: str, device_code: str, protocol: str, payload: Dict) -> Dict:
        """应用标准字段映射"""
        from src.Iot.dao import FieldMappingDAO

        mapped_result = {}

        if self.app:
            with self.app.app_context():
                mappings = FieldMappingDAO.get_mappings_by_device(device_did, protocol)

                for mapping in mappings:
                    raw_field = mapping.raw_field
                    if raw_field in payload:
                        value = payload[raw_field]

                        if mapping.transform:
                            value = self._apply_transform(value, mapping.transform)

                        mapped_result[mapping.standard_field] = value

        # 添加设备信息
        mapped_result['device_code'] = device_code
        mapped_result['device_did'] = device_did
        if 'timestamp' in payload:
            mapped_result['timestamp'] = payload['timestamp']
        else:
            mapped_result['timestamp'] = datetime.now().isoformat()

        if 'seq' in payload:
            mapped_result['seq'] = payload['seq']

        return mapped_result

    def _save_to_csv_for_analysis(self, device_did: str, mapped_data: Dict):
        """将数据保存到CSV用于数据分析"""
        try:
            if not self.app:
                return

            with self.app.app_context():
                # 1. 获取设备信息
                device = DeviceDAO.get_device_by_did(device_did)
                if not device:
                    return

                # 2. 获取 device_code（必须存在）
                if hasattr(device, 'device_code') and device.device_code:
                    device_code = device.device_code
                else:
                    print(f"[CSV] 错误: 设备 {device_did} 没有 device_code，无法创建CSV文件")
                    return

                # 2. 检查 extra 中的数据分析标识
                extra = device.extra or {}
                enable_data_analysis = extra.get('enable_data_analysis', False)

                if not enable_data_analysis:
                    print(device_did + ":不采用数据存储模式")
                    return

                # 采用数据存储模式
                print(device_did + ":采用数据存储模式")
                print(f"数据: {mapped_data}")

                # 3. 直接存储所有映射后的数据（排除系统内部字段）
                # 需要存储的字段：所有不以 _ 开头的字段
                filtered_data = {}
                for key, value in mapped_data.items():
                    # 不存储系统内部字段（以 _ 开头）
                    if not key.startswith('_'):
                        filtered_data[key] = value

                if filtered_data:
                    csv_storage.append_data(device_code, filtered_data)
                    print(f"[CSV] {device_did} 已加入队列，字段: {list(filtered_data.keys())}")

        except Exception as e:
            print(f"[CSV] 异常: {e}")

    def _on_device_data(self, device_did: str, raw_data: Any, protocol: str):
        """设备数据回调 - 先做字段映射，再通过 SSE 推送到前端"""
        device_info = self.devices.get(device_did, {})
        device_code = device_info.get('device_code', 'unknown')

        # ===== 🆕 视频帧直接透传（不做字段映射） =====
        if isinstance(raw_data, dict) and raw_data.get('type') == 'video_frame':
            print(f"[DeviceManager] 📹 收到视频帧: {device_code}, frame_count={raw_data.get('frame_count')}")
            try:
                push_to_device(device_code, raw_data)
                print(f"[DeviceManager] ✅ 视频帧已推送到 SSE")
            except Exception as e:
                print(f"[DeviceManager] ❌ SSE 推送失败: {e}")
            return

        if isinstance(raw_data, dict):
            payload = raw_data.get('payload', raw_data)
        else:
            payload = raw_data

        # 🆕 打印映射前原始数据
        print("=" * 20)
        print(f"\n[映射前] device_did: {device_did}")
        print(f"[映射前] protocol: {protocol}")
        print(f"[映射前] payload: {payload}")

        # 1. 标准字段映射
        mapped_data = self._apply_field_mapping(device_did, device_code, protocol, payload)

        # 🆕 1.5 保存到CSV用于数据分析
        self._save_to_csv_for_analysis(device_did, mapped_data)

        print("=" * 20)

        # 2. 构建 SSE 推送数据
        push_data = {
            'type': 'device_data',
            'device_code': device_code,
            'device_did': device_did,
            'timestamp': datetime.now().isoformat(),
            'data': mapped_data
        }

        # 3. SSE 推送
        try:
            push_to_device(device_code, push_data)
        except Exception as e:
            print(f"[SSE] 推送失败: {e}")

    def _on_device_status(self, device_did: str, status: str, protocol: str):
        """设备状态回调"""
        device_info = self.devices.get(device_did, {})
        device_name = device_info.get('device_name', device_did[:20])
        device_code = device_info.get('device_code', 'unknown')

        # print(f"[{device_code}] {device_name} -> {status.upper()}")

        # 推送状态变化到 SSE
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

        # 更新数据库状态
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
            # print(f"\n📋 发现 {len(all_devices)} 台设备")

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

            # print("🔌 连接设备...")
            for device_dict in device_dicts:
                self._connect_device(device_dict)
        except Exception as e:
            print(f"❌ 加载失败: {e}")

    def _connect_device(self, device: Dict) -> bool:
        device_did = device.get('did')
        device_name = device.get('device_name', '未知')
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
                # print(f"   ✅ {device_code} ({device_name})")
                return True
            else:
                print(f"   ❌ {device_code} ({device_name})")
                return False
        except Exception as e:
            # print(f"   ❌ {device_code} 连接错误: {e}")
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