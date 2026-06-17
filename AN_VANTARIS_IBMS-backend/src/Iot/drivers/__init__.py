# src/Iot/drivers/__init__.py
"""
协议驱动注册中心 - 自动发现并注册所有驱动
新增协议时，只需在 drivers/ 目录下创建新的驱动文件，无需修改此文件
"""

import os
import importlib
from typing import Dict, Type, Optional

from src.Iot.drivers.base_driver import BaseProtocolDriver
from src.Iot.exceptions import ProtocolNotFoundError
from .http_driver import HTTPDriver
from .modbus_driver import ModbusDriver
from .mqtt_driver import MQTTDriver


class DriverRegistry:
    """协议驱动注册中心 - 自动发现并管理所有驱动"""

    _drivers: Dict[str, Type[BaseProtocolDriver]] = {}
    _instances: Dict[str, BaseProtocolDriver] = {}

    @classmethod
    def register(cls, protocol_name: str, driver_class: Type[BaseProtocolDriver]):
        """注册驱动"""
        cls._drivers[protocol_name.lower()] = driver_class
        print(f"[DriverRegistry] Registered driver: {protocol_name}")

    @classmethod
    def get_driver(cls, protocol_name: str) -> BaseProtocolDriver:
        """获取驱动实例（单例）"""
        protocol_name = protocol_name.lower()

        if protocol_name not in cls._instances:
            driver_class = cls._drivers.get(protocol_name)
            if not driver_class:
                raise ProtocolNotFoundError(
                    f"不支持的协议: {protocol_name}，已注册协议: {list(cls._drivers.keys())}"
                )
            cls._instances[protocol_name] = driver_class()

        return cls._instances[protocol_name]

    @classmethod
    def list_drivers(cls) -> list:
        """列出所有已注册的驱动"""
        return list(cls._drivers.keys())

    @classmethod
    def is_supported(cls, protocol_name: str) -> bool:
        """检查协议是否支持"""
        return protocol_name.lower() in cls._drivers

    @classmethod
    def auto_discover(cls):
        """
        自动发现 drivers 目录下的所有驱动
        扫描当前目录，自动导入所有以 _driver.py 结尾或定义了驱动类的模块
        """
        current_dir = os.path.dirname(__file__)

        for filename in os.listdir(current_dir):
            # 跳过基类文件和初始化文件
            if filename in ['base_driver.py', '__init__.py']:
                continue

            if filename.endswith('.py'):
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(f'src.Iot.drivers.{module_name}')

                    # 查找模块中继承 BaseProtocolDriver 的类
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and
                                issubclass(attr, BaseProtocolDriver) and
                                attr is not BaseProtocolDriver):
                            # 实例化获取协议名称
                            temp_instance = attr()
                            protocol_name = temp_instance.protocol_name
                            cls.register(protocol_name, attr)

                            # 🆕 如果是 ISUP 驱动，自动启动服务端
                            if protocol_name == 'isup':
                                try:
                                    # 获取已注册的驱动实例
                                    driver_instance = cls.get_driver(protocol_name)
                                    if hasattr(driver_instance, 'start_server'):
                                        driver_instance.start_server(7660)
                                        print(f"[ISUP] 服务端已启动，监听端口: 7660")
                                except Exception as e:
                                    print(f"[ISUP] 启动服务端失败: {e}")

                            # 🆕 如果是 RTSP 驱动，打印 RTP 接收端口
                            if protocol_name == 'rtsp':
                                try:
                                    driver_instance = cls.get_driver(protocol_name)
                                    if hasattr(driver_instance, 'rtp_port'):
                                        print(f"[RTSP] RTP 数据接收端口: {driver_instance.rtp_port}")
                                except Exception as e:
                                    print(f"[RTSP] 获取端口信息失败: {e}")

                except Exception as e:
                    print(f"[DriverRegistry] Failed to load {module_name}: {e}")


# 自动发现并注册所有驱动
DriverRegistry.auto_discover()

# 导出
__all__ = [
    'DriverRegistry',
    'BaseProtocolDriver'
]