"""
文件路径: src/data_modeling/predictors/template_predictor.py
预测器模板 - 新设备预测器请复制此文件并重命名
命名规则: {device_code}_predictor.py (例如: hvac_sim_001_predictor.py)

方法签名必须保持一致，否则 service 层无法正确调用
"""

from typing import Dict, Any, List
import pandas as pd


# ==================== 必须实现的方法 ====================

def train(df: pd.DataFrame, models_dir: str, **kwargs) -> dict:
    """
    训练模型（必须实现）

    参数:
        df: 设备 CSV 数据 (DataFrame)，包含 timestamp 和所有字段
        models_dir: 模型保存目录
        **kwargs: 其他参数（由 API 透传）

    返回:
        dict: {
            "message": "训练完成",
            "model_path": "模型文件路径",
            "metrics": {
                "r2": 0.99,
                "mae": 0.5,
                ...
            }
        }
    """
    pass


def predict_future(device_code: str, days: int, models_dir: str, **kwargs) -> Dict[str, Any]:
    """
    未来多天预测（必须实现）

    参数:
        device_code: 设备号（用于读取 CSV 最新时间）
        days: 预测天数
        models_dir: 模型保存目录
        **kwargs: 其他参数，通常包括:
            - city: 城市名称（用于天气API）
            - electricity_price: 电价
            - enable_saving: 是否启用节能模拟

    返回:
        dict: {
            "status": "success",
            "prediction_stats": {
                "total_energy_kWh": 100.5,
                "avg_power_kW": 4.2,
                "peak_power_kW": 8.5,
                "min_power_kW": 0.0,
                "avg_outdoor_temp": 22.5,
                "estimated_cost_yuan": 150,
                "start_date": "2026-01-01",
                "end_date": "2026-01-07"
            },
            "daily_data": [...],
            "raw_hourly_data": [...],
            "saving_simulation": {...}  # 可选
        }
    """
    pass


def predict(features: Dict[str, float], models_dir: str, **kwargs) -> float:
    """
    单点预测（可选实现，用于兼容）

    参数:
        features: 特征值字典，如 {"temperature": 22.5, "humidity": 60}
        models_dir: 模型保存目录
        **kwargs: 其他参数

    返回:
        float: 预测值
    """
    pass


def get_model_info(models_dir: str) -> dict:
    """
    获取模型信息（可选实现）

    参数:
        models_dir: 模型保存目录

    返回:
        dict: {
            "exists": True,
            "metrics": {...},
            "trained_at": "2026-01-01T00:00:00"
        }
    """
    pass


# ==================== 辅助函数（可选，按需实现） ====================

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    数据预处理（可选）
    根据设备特点处理数据
    """
    pass


def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """
    特征工程（可选）
    根据设备特点创建特征
    """
    pass


def get_weather_data(start_time, days, city, **kwargs) -> pd.DataFrame:
    """
    天气数据获取（可选）
    如果设备需要天气数据，实现此方法
    """
    pass