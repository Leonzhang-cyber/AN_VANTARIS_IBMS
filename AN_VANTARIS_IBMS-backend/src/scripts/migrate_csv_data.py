"""
文件路径: scripts/migrate_csv_data.py
将历史 CSV 数据追加到 data/csv/HVAC_SIM_001.csv
"""

import csv
import os
import sys

# 当前脚本所在目录: .../imbs-sysytem-backend/src/scripts
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# 项目根目录: .../imbs-sysytem-backend（去掉 src/scripts）
BASE_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))

# 源文件路径: src/testMQTT/hvac_2025_prediction_data.csv
SOURCE_CSV = os.path.join(BASE_DIR, 'src', 'testMQTT', 'hvac_2025_prediction_data.csv')

# 目标文件路径: data/csv/HVAC_SIM_001.csv
TARGET_CSV = os.path.join(BASE_DIR, 'data', 'csv', 'HVAC_SIM_001.csv')

print(f"BASE_DIR = {BASE_DIR}")  # 调试：查看根目录是否正确
print(f"SOURCE_CSV = {SOURCE_CSV}")
print(f"TARGET_CSV = {TARGET_CSV}")


# 固定值
DEVICE_CODE = 'HVAC_SIM_001'
DEVICE_DID = 'did:imbs:system:root:bim_region:dbfece48:device:hvac:dcbc7318d31b'


def migrate_data():
    """迁移数据（追加模式）"""

    # 检查源文件是否存在
    if not os.path.exists(SOURCE_CSV):
        print(f"❌ 源文件不存在: {SOURCE_CSV}")
        return False

    # 确保目标目录存在
    target_dir = os.path.dirname(TARGET_CSV)
    os.makedirs(target_dir, exist_ok=True)

    print(f"📂 源文件: {SOURCE_CSV}")
    print(f"📂 目标文件: {TARGET_CSV}")
    print()

    # 读取源数据
    source_data = []
    with open(SOURCE_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            source_data.append(row)

    print(f"源文件数据条数: {len(source_data)}")

    # 读取已存在的 seq 最大值（如果目标文件存在）
    existing_seq_max = 0
    if os.path.exists(TARGET_CSV):
        with open(TARGET_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                seq = int(row.get('seq', 0))
                if seq > existing_seq_max:
                    existing_seq_max = seq
        print(f"目标文件已有数据条数: {existing_seq_max}")

    # 准备目标数据
    target_data_list = []
    seq = existing_seq_max + 1

    for row in source_data:
        # 字段映射
        target_row = {
            'temperature': row.get('zone_1_temp', ''),
            'power': row.get('chiller_A_power_kW', ''),
            'dew_point': row.get('dew_point_temp', ''),
            'holiday_flag': row.get('is_holiday', ''),
            'set_temperature': row.get('chilled_water_temp_setpoint', ''),
            'outdoor_temperature': row.get('outdoor_air_temp', ''),
            'damper_position': row.get('ahu_1_damper_pos', ''),
            'occupancy': row.get('occupancy_schedule', ''),
            'chiller_state': row.get('chiller_A_status', ''),
            'solar_radiation': row.get('solar_radiation_w_m2', ''),
            'device_code': DEVICE_CODE,
            'device_did': DEVICE_DID,
            'timestamp': row.get('timestamp', ''),
            'seq': seq
        }
        target_data_list.append(target_row)
        seq += 1

    # 追加或覆盖写入
    if os.path.exists(TARGET_CSV):
        # 追加模式
        with open(TARGET_CSV, 'a', newline='', encoding='utf-8') as f:
            fieldnames = ['temperature', 'power', 'dew_point', 'holiday_flag', 'set_temperature',
                         'outdoor_temperature', 'damper_position', 'occupancy', 'chiller_state',
                         'solar_radiation', 'device_code', 'device_did', 'timestamp', 'seq']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writerows(target_data_list)
        print(f"\n✅ 追加完成！共追加 {len(target_data_list)} 条数据")
    else:
        # 新文件，写入表头和数据
        with open(TARGET_CSV, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['temperature', 'power', 'dew_point', 'holiday_flag', 'set_temperature',
                         'outdoor_temperature', 'damper_position', 'occupancy', 'chiller_state',
                         'solar_radiation', 'device_code', 'device_did', 'timestamp', 'seq']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(target_data_list)
        print(f"\n✅ 写入完成！共写入 {len(target_data_list)} 条数据")

    # 统计最终数据条数
    with open(TARGET_CSV, 'r', encoding='utf-8') as f:
        line_count = sum(1 for _ in f) - 1
    print(f"目标文件总数据条数: {line_count}")

    return True


def preview_data():
    """预览迁移后的数据"""
    if not os.path.exists(TARGET_CSV):
        print(f"❌ 目标文件不存在: {TARGET_CSV}")
        return

    print("\n📊 迁移后的数据预览（最后5条）:")
    print("-" * 80)

    lines = []
    with open(TARGET_CSV, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 打印最后5条数据
    for line in lines[-5:]:
        print(line.strip())

    print(f"\n📈 总数据条数: {len(lines) - 1}")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--preview', action='store_true', help='预览迁移后的数据')
    args = parser.parse_args()

    if args.preview:
        preview_data()
    else:
        migrate_data()