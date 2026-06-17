"""
文件路径: src/data_modeling/config.py
模块配置
"""

import os

# 项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# CSV 存储路径
CSV_CONFIG = {
    'data_dir': os.path.join(BASE_DIR, 'data', 'csv'),
}

# 模型保存路径
MODEL_CONFIG = {
    'models_dir': os.path.join(BASE_DIR, 'data', 'models'),
}

DATA_MODELING_CONFIG = {
    'csv': CSV_CONFIG,
    'model': MODEL_CONFIG,
}

# 设备号 → 预测器模块名映射
# 用户在这里配置每个设备对应的预测器文件
DEVICE_PREDICTOR_MAP = {
    'HVAC_SIM_001': 'hvac_sim_001',      # 对应 predictors/hvac_sim_001.py
    # 添加新设备：
    # 'CHILLER_002': 'chiller_002',
}