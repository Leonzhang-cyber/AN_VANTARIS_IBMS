"""
文件路径: src/data_modeling/exceptions.py
自定义异常类
"""


class DataModelingError(Exception):
    """数据建模模块基础异常"""
    pass


class DataInsufficientError(DataModelingError):
    """数据不足异常"""
    pass


class ModelNotFoundError(DataModelingError):
    """模型不存在异常"""
    pass


class TrainingError(DataModelingError):
    """训练失败异常"""
    pass


class PredictorNotFoundError(DataModelingError):
    """预测器不存在异常"""
    pass


class CSVReadError(DataModelingError):
    """CSV读取异常"""
    pass


class CSVWriteError(DataModelingError):
    """CSV写入异常"""
    pass