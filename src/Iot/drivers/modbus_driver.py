# src/Iot/drivers/modbus_driver.py
from src.Iot.drivers.base_driver import BaseProtocolDriver


class ModbusDriver(BaseProtocolDriver):
    def __init__(self):
        super().__init__("modbus")  # 协议名称

    def connect(self, device_did: str, config: dict) -> bool:
        # 实现 Modbus 连接逻辑
        pass

    def disconnect(self, device_did: str) -> bool:
        # 实现断开逻辑
        pass

    def send_command(self, device_did: str, command: dict) -> dict:
        # 实现命令下发
        pass

    def subscribe(self, device_did: str, topics: list = None):
        # 实现数据订阅
        pass