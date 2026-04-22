"""
文件路径: src/data_modeling/service.py
核心业务逻辑 - 动态加载预测器
"""

import importlib
import os
from typing import Dict, Any, List

from src.data_modeling.config import DEVICE_PREDICTOR_MAP, MODEL_CONFIG, CSV_CONFIG
from src.data_modeling.csv_storage import csv_storage
from src.data_modeling.exceptions import PredictorNotFoundError, DataInsufficientError


class ModelingService:
    """数据建模服务 - 动态加载设备预测器"""

    def _get_predictor_module(self, device_code: str):
        """根据设备号动态加载对应的预测器模块"""
        module_name = DEVICE_PREDICTOR_MAP.get(device_code)
        if not module_name:
            raise PredictorNotFoundError(
                f"设备 {device_code} 未配置预测器，请在 config.py 的 DEVICE_PREDICTOR_MAP 中添加"
            )

        try:
            module = importlib.import_module(f"src.data_modeling.predictors.{module_name}")
            return module
        except ImportError as e:
            raise PredictorNotFoundError(f"预测器模块 {module_name} 不存在: {e}")

    def train(self, device_code: str, **kwargs) -> Dict[str, Any]:
        """
        训练模型 - 所有参数透传给预测器
        预测器函数签名: train(df, models_dir, **kwargs)
        """
        predictor = self._get_predictor_module(device_code)

        if not hasattr(predictor, 'train'):
            raise AttributeError(f"预测器 {predictor.__name__} 必须实现 train() 函数")

        # 获取设备数据
        df = csv_storage.read_dataframe(device_code)
        if df.empty:
            raise DataInsufficientError(f"设备 {device_code} 无数据，请先上报数据")

        # 调用预测器的 train 函数（不传 device_code）
        result = predictor.train(
            df=df,
            models_dir=MODEL_CONFIG['models_dir'],
            **kwargs
        )

        return {
            "status": "success",
            "device_code": device_code,
            "result": result
        }

    def predict_future(self, device_code: str, **kwargs) -> Dict[str, Any]:
        """
        未来多天预测 - 所有参数透传给预测器
        """
        predictor = self._get_predictor_module(device_code)

        if not hasattr(predictor, 'predict_future'):
            raise AttributeError(f"预测器 {predictor.__name__} 必须实现 predict_future() 函数")

        # 🆕 调用时传入 device_code
        result = predictor.predict_future(
            device_code=device_code,
            models_dir=MODEL_CONFIG['models_dir'],
            **kwargs
        )

        return {
            "status": "success",
            "device_code": device_code,
            "result": result
        }

    def predict(self, device_code: str, **kwargs) -> Dict[str, Any]:
        """
        单点预测 - 所有参数透传给预测器
        预测器函数签名: predict(features, models_dir, **kwargs)
        """
        predictor = self._get_predictor_module(device_code)

        if not hasattr(predictor, 'predict'):
            raise AttributeError(f"预测器 {predictor.__name__} 必须实现 predict() 函数")

        # 如果没有传入 features，自动获取最新数据
        if 'features' not in kwargs:
            features = csv_storage.get_latest_data(device_code)
            if not features:
                raise DataInsufficientError(f"设备 {device_code} 无历史数据")
            kwargs['features'] = features

        # 调用预测器的 predict 函数（不传 device_code）
        result = predictor.predict(
            models_dir=MODEL_CONFIG['models_dir'],
            **kwargs
        )

        return {
            "device_code": device_code,
            "result": result
        }

    def get_model_info(self, device_code: str) -> Dict[str, Any]:
        """
        获取模型信息
        预测器函数签名: get_model_info(models_dir)
        """
        predictor = self._get_predictor_module(device_code)

        if hasattr(predictor, 'get_model_info'):
            result = predictor.get_model_info(models_dir=MODEL_CONFIG['models_dir'])
        else:
            result = {"message": "该预测器未实现 get_model_info 方法"}

        return {
            "device_code": device_code,
            "result": result
        }

    def call(self, device_code: str, method: str, **kwargs) -> Dict[str, Any]:
        """
        通用调用方法 - 调用预测器中的任意方法
        """
        predictor = self._get_predictor_module(device_code)

        if not hasattr(predictor, method):
            raise AttributeError(f"预测器 {predictor.__name__} 没有实现 {method}() 方法")

        # 自动添加 models_dir
        if 'models_dir' not in kwargs:
            kwargs['models_dir'] = MODEL_CONFIG['models_dir']

        result = getattr(predictor, method)(**kwargs)

        return {
            "device_code": device_code,
            "method": method,
            "result": result
        }

    # ========== CSV 文件管理接口 ==========

    def list_csv_files(self) -> Dict[str, Any]:
        """获取所有 CSV 文件列表"""
        csv_dir = CSV_CONFIG['data_dir']

        if not os.path.exists(csv_dir):
            return {
                "total": 0,
                "devices": []
            }

        csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]

        devices = []
        for csv_file in csv_files:
            device_code = csv_file.replace('.csv', '')
            file_path = os.path.join(csv_dir, csv_file)
            file_size = os.path.getsize(file_path)

            df = csv_storage.read_dataframe(device_code)
            row_count = len(df) if not df.empty else 0

            devices.append({
                "device_code": device_code,
                "file_name": csv_file,
                "file_size_bytes": file_size,
                "file_size_kb": round(file_size / 1024, 2),
                "row_count": row_count,
                "has_predictor": device_code in DEVICE_PREDICTOR_MAP
            })

        devices.sort(key=lambda x: x['device_code'])

        return {
            "total": len(devices),
            "devices": devices
        }

    def get_device_csv_info(self, device_code: str) -> Dict[str, Any]:
        """获取指定设备 CSV 的最新一条数据和统计信息"""
        df = csv_storage.read_dataframe(device_code)
        if df.empty:
            raise DataInsufficientError(f"设备 {device_code} 的 CSV 文件不存在或无数据")

        latest_data = csv_storage.get_latest_data(device_code)

        stats = {
            "total_count": len(df),
            "fields": [col for col in df.columns if col != 'timestamp'],
            "date_range": {
                "start": df['timestamp'].min(),
                "end": df['timestamp'].max()
            } if 'timestamp' in df.columns else None
        }

        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        numeric_stats = {}
        for col in numeric_cols:
            numeric_stats[col] = {
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "mean": float(df[col].mean()),
                "std": float(df[col].std())
            }

        return {
            "device_code": device_code,
            "latest_data": latest_data,
            "statistics": stats,
            "numeric_stats": numeric_stats,
            "has_predictor": device_code in DEVICE_PREDICTOR_MAP
        }


service = ModelingService()