"""
文件路径: src/api/data_modeling/modeling_api.py
API接口
"""

from flask import request, jsonify
from src.api import api_bp
from src.data_modeling.service import service


# ========== CSV 文件管理接口 ==========

@api_bp.route('/modeling/csv/list', methods=['GET'])
def list_csv_files():
    """
    获取所有 CSV 文件列表
    返回每个设备的设备号和文件信息
    """
    try:
        result = service.list_csv_files()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/modeling/csv/<device_code>', methods=['GET'])
def get_device_csv_info(device_code):
    """
    获取指定设备 CSV 的最新一条数据和统计信息
    """
    try:
        result = service.get_device_csv_info(device_code)
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========== 预测接口 ==========

@api_bp.route('/modeling/<device_code>/train', methods=['POST'])
def train(device_code):
    """训练模型"""
    try:
        result = service.train(device_code, **request.json)
        return jsonify(result), 202
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@api_bp.route('/modeling/<device_code>/predict', methods=['POST'])
def predict(device_code):
    """单点预测"""
    try:
        result = service.predict(device_code, **request.json)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@api_bp.route('/modeling/<device_code>/predict_future', methods=['POST'])
def predict_future(device_code):
    """
    未来多天预测
    Body示例:
    {
        "days": 7,
        "city": "Hong Kong",
        "electricity_price": 1.44,
        "enable_saving": true
    }
    """
    try:
        result = service.predict_future(device_code, **request.json)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@api_bp.route('/modeling/<device_code>/model_info', methods=['GET'])
def get_model_info(device_code):
    """获取模型信息"""
    try:
        result = service.get_model_info(device_code)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@api_bp.route('/modeling/<device_code>/<method>', methods=['POST', 'GET'])
def call_method(device_code, method):
    """
    通用调用（调用预测器中的任意方法）
    注意：predict_future 和 model_info 已有专用接口，建议使用专用接口
    """
    try:
        if request.method == 'GET':
            result = service.call(device_code, method, **request.args)
        else:
            result = service.call(device_code, method, **request.json)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400