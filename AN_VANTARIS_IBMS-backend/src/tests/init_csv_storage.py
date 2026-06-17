"""
文件路径: scripts/init_csv_storage.py
初始化CSV存储目录
"""

import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_modeling.config import CSV_CONFIG


def init_csv_storage():
    """初始化CSV存储目录"""

    # 创建CSV数据目录
    csv_dir = CSV_CONFIG['data_dir']
    os.makedirs(csv_dir, exist_ok=True)
    print(f"✅ CSV目录创建成功: {csv_dir}")

    # 创建models目录
    from src.data_modeling.config import MODEL_CONFIG
    models_dir = MODEL_CONFIG['models_dir']
    os.makedirs(models_dir, exist_ok=True)
    print(f"✅ 模型目录创建成功: {models_dir}")

    # 创建cache目录
    from src.data_modeling.config import DATA_DIR
    cache_dir = os.path.join(DATA_DIR, 'cache')
    os.makedirs(cache_dir, exist_ok=True)
    print(f"✅ 缓存目录创建成功: {cache_dir}")

    # 统计已有CSV文件（仅显示，不创建）
    csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]

    if csv_files:
        print(f"\n📊 已有CSV文件: {len(csv_files)} 个")
        for f in csv_files[:10]:
            filepath = os.path.join(csv_dir, f)
            file_size = os.path.getsize(filepath)
            print(f"  - {f} ({file_size} bytes)")
        if len(csv_files) > 10:
            print(f"  ... 还有 {len(csv_files) - 10} 个文件")
    else:
        print(f"\n📊 暂无CSV文件，设备上报数据后会自动创建")


if __name__ == '__main__':
    init_csv_storage()