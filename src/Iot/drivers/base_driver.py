# src/Iot/drivers/base_driver.py
"""
协议驱动基类 - 所有协议驱动必须继承此类
新增协议时，只需在 drivers/ 目录下创建新文件，继承此类并实现所有抽象方法
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, Optional


class BaseProtocolDriver(ABC):
    """协议驱动基类 - 定义所有协议必须实现的接口"""

    def __init__(self, protocol_name: str):
        self.protocol_name = protocol_name
        self.data_callback = None  # 数据上报回调
        self.status_callback = None  # 设备状态回调

    @abstractmethod
    def connect(self, device_did: str, config: Dict[str, Any]) -> bool:
        """
        连接设备
        :param device_did: 设备DID
        :param config: 连接配置（从数据库 connect_config 读取）
        :return: 是否连接成功
        """
        pass

    @abstractmethod
    def disconnect(self, device_did: str) -> bool:
        """断开设备连接"""
        pass

    @abstractmethod
    def send_command(self, device_did: str, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        下发命令
        :param device_did: 设备DID
        :param command: 命令内容（已转换为设备格式）
        :return: 执行结果
        """
        pass

    @abstractmethod
    def subscribe(self, device_did: str, topics: Optional[list] = None):
        """订阅设备数据"""
        pass

    def register_data_callback(self, callback: Callable):
        """注册数据回调（由 DeviceManager 调用）"""
        self.data_callback = callback

    def register_status_callback(self, callback: Callable):
        """注册状态回调（由 DeviceManager 调用）"""
        self.status_callback = callback

    def _on_data(self, device_did: str, raw_data: Any):
        """收到数据时调用此方法触发回调"""
        if self.data_callback:
            self.data_callback(device_did, raw_data, self.protocol_name)

    def _on_status(self, device_did: str, status: str):
        """状态变化时调用此方法触发回调"""
        if self.status_callback:
            self.status_callback(device_did, status, self.protocol_name)