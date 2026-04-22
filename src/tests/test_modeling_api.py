"""
文件路径: tests/test_modeling_api.py
API测试
"""

import unittest
import json


class TestModelingAPI(unittest.TestCase):
    """API测试"""

    def setUp(self):
        # 这里需要创建测试用的Flask应用
        # 请根据你的项目配置修改
        from flask import Flask
        from src.api.data_modeling.modeling_api import modeling_bp

        self.app = Flask(__name__)
        self.app.register_blueprint(modeling_bp)
        self.client = self.app.test_client()

    def test_get_config(self):
        """测试获取配置"""
        response = self.client.get('/api/ai/device/test_did/config')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['device_did'], 'test_did')

    def test_update_config(self):
        """测试更新配置"""
        response = self.client.put('/api/ai/device/test_did/config', json={
            'enabled': True,
            'target_field': 'temperature'
        })
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['target_field'], 'temperature')

    def test_get_fields(self):
        """测试获取字段"""
        response = self.client.get('/api/ai/device/test_did/fields')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()