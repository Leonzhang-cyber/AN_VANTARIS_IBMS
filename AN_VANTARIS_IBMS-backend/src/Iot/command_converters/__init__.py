# src/Iot/command_converters/__init__.py
"""
命令转换器 - 将标准方法转换为不同协议的设备命令
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import json


class CommandConverter(ABC):
    """命令转换器基类"""

    @abstractmethod
    def convert(self, device_config: Dict, method: str, params: Dict) -> Dict:
        """将标准命令转换为设备特定命令"""
        pass


class MQTTCommandConverter(CommandConverter):
    """MQTT 命令转换器"""

    def convert(self, device_config: Dict, method: str, params: Dict) -> Dict:
        """转换为 MQTT 命令"""
        from src.Iot.dao import MethodMappingDAO

        method_mapping = MethodMappingDAO.get_mapping_by_standard(
            device_config.get('did'), 'mqtt', 'downlink', method
        )

        if not method_mapping:
            raise ValueError(f"未找到方法映射: {method}")

        extra = method_mapping.extra or {}
        param_name = extra.get('param', method)

        # 获取设备编号
        device_code = device_config.get('device_code', '')

        # 构建 topic（包含设备号）
        raw_path = method_mapping.raw_path
        command_topic = raw_path.replace('{device_id}', device_config.get('did', ''))
        command_topic = command_topic.replace('{device_code}', device_code)

        # 如果没有占位符，自动添加设备号
        if '{device_id}' not in raw_path and '{device_code}' not in raw_path:
            if command_topic.endswith('/command'):
                base_path = command_topic.replace('/command', '')
                command_topic = f"{base_path}/{device_code}/command"
            else:
                command_topic = f"{command_topic}/{device_code}"

        # 构建 payload
        if method == 'set_temperature':
            payload = {'command': 'set_setpoint', 'value': params.get('value')}
        elif method == 'set_damper':
            payload = {'command': 'set_damper', 'value': params.get('value')}
        elif method == 'get_status':
            payload = {'command': 'get_status'}
        else:
            payload = {param_name: params.get('value', params)}

        return {
            'topic': command_topic,
            'payload': payload,
            'qos': 1
        }


class HTTPCommandConverter(CommandConverter):
    """HTTP 命令转换器"""

    def convert(self, device_config: Dict, method: str, params: Dict) -> Dict:
        """转换为 HTTP 命令"""
        from src.Iot.dao import MethodMappingDAO

        method_mapping = MethodMappingDAO.get_mapping_by_standard(
            device_config.get('did'), 'http', 'downlink', method
        )

        if not method_mapping:
            raise ValueError(f"未找到方法映射: {method}")

        extra = method_mapping.extra or {}

        # 从 extra 中获取 HTTP 配置
        http_config = extra.get('http_config', {})

        return {
            'endpoint': http_config.get('endpoint', f'/api/{method}'),
            'http_method': http_config.get('method', 'POST'),
            'headers': http_config.get('headers', {'Content-Type': 'application/json'}),
            'params': params
        }


class ModbusCommandConverter(CommandConverter):
    """Modbus 命令转换器 - 待实现"""

    def convert(self, device_config: Dict, method: str, params: Dict) -> Dict:
        """转换为 Modbus 命令（待实现）"""
        # TODO: 实现 Modbus 命令转换
        raise NotImplementedError("Modbus 命令转换器待实现")


# 转换器注册
CONVERTERS = {
    'mqtt': MQTTCommandConverter(),
    'http': HTTPCommandConverter(),
    'modbus': ModbusCommandConverter(),
}


def get_command_converter(protocol: str) -> CommandConverter:
    """获取协议对应的命令转换器"""
    return CONVERTERS.get(protocol.lower()) if protocol else None


def register_converter(protocol: str, converter: CommandConverter):
    """注册新的协议转换器"""
    CONVERTERS[protocol.lower()] = converter


__all__ = [
    'CommandConverter',
    'MQTTCommandConverter',
    'HTTPCommandConverter',
    'ModbusCommandConverter',
    'get_command_converter',
    'register_converter'
]