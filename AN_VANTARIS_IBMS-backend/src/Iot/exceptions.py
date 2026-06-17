# src/Iot/exceptions.py

class IOTException(Exception):
    """IoT模块基础异常"""
    pass


class DeviceNotFoundError(IOTException):
    """设备不存在"""
    pass


class DuplicateDeviceError(IOTException):
    """设备重复（设备编号或DID已存在）"""
    pass


class DeviceRegistrationError(IOTException):
    """设备注册失败"""
    pass


class DeviceOfflineError(IOTException):
    """设备离线"""
    pass


class ProtocolNotFoundError(IOTException):
    """协议不支持"""
    pass


class ProtocolError(IOTException):
    """协议通信错误"""
    pass


class FieldMappingNotFoundError(IOTException):
    """字段映射不存在"""
    pass


class MethodMappingNotFoundError(IOTException):
    """方法映射不存在"""
    pass


class CommandSendError(IOTException):
    """命令下发失败"""
    pass


class DataParseError(IOTException):
    """数据解析错误"""
    pass


class InvalidConfigurationError(IOTException):
    """无效的配置参数"""
    pass


class DeviceNotConnectedError(IOTException):
    """设备未连接"""
    pass


class SubscriptionError(IOTException):
    """订阅失败"""
    pass