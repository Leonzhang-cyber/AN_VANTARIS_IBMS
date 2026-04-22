"""
文件路径: tests/test_data_modeling.py
单元测试
"""

import unittest
import tempfile
import os
import pandas as pd
import numpy as np


class TestCSVStorage(unittest.TestCase):
    """CSV存储测试"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        from src.data_modeling.csv_storage import CSVStorage
        self.storage = CSVStorage(data_dir=self.temp_dir)
        self.device_did = 'test_device_001'

    def test_append_and_read(self):
        """测试写入和读取"""
        data = {'temperature': 22.5, 'humidity': 60}
        self.storage.append_data(self.device_did, data)

        # 等待异步写入完成
        import time
        time.sleep(0.5)

        df = self.storage.read_dataframe(self.device_did)
        self.assertFalse(df.empty)
        self.assertEqual(df.iloc[-1]['temperature'], 22.5)

    def test_get_available_fields(self):
        """测试获取字段"""
        data = {'temperature': 22.5, 'humidity': 60, 'pressure': 1013}
        self.storage.append_data(self.device_did, data)

        import time
        time.sleep(0.5)

        fields = self.storage.get_available_fields(self.device_did)
        self.assertIn('temperature', fields)
        self.assertIn('humidity', fields)


class TestTrainer(unittest.TestCase):
    """训练器测试"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        from src.data_modeling.trainer import ModelTrainer
        self.trainer = ModelTrainer(models_dir=self.temp_dir)

        # 创建测试数据
        dates = pd.date_range('2024-01-01', periods=200, freq='H')
        self.df = pd.DataFrame({
            'timestamp': dates,
            'temperature': 20 + np.sin(np.arange(200) * 0.1) + np.random.randn(200) * 0.5,
            'humidity': 50 + np.cos(np.arange(200) * 0.05) + np.random.randn(200) * 2,
            'pressure': 1013 + np.random.randn(200) * 2
        })

    def test_train_linear(self):
        """测试线性回归训练"""
        metrics = self.trainer.train(
            device_did='test_device',
            df=self.df,
            target_field='temperature',
            algorithm='linear'
        )

        self.assertIn('mse', metrics)
        self.assertIn('r2', metrics)
        self.assertGreater(metrics['train_samples'], 0)

    def test_train_insufficient_data(self):
        """测试数据不足的情况"""
        small_df = self.df.head(10)

        with self.assertRaises(Exception):
            self.trainer.train(
                device_did='test_device',
                df=small_df,
                target_field='temperature'
            )


if __name__ == '__main__':
    unittest.main()