#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTTP 设备模拟器 - 纯主动上报模式
设备只需要无脑上传数据，不需要注册
"""

import requests
import json
import time
import random
import math
import signal
import sys
from datetime import datetime

# ========== 配置信息 ==========
IMBS_HOST = "http://localhost:5000"  # IoT 模块地址
INGEST_URL = f"{IMBS_HOST}/api/iot/ingest/http"

DEVICE_CODE = "HTTP_SENSOR_001"

SEND_INTERVAL = 5  # 发送间隔（秒）

# 统计
running = True
sent_count = 0
success_count = 0
fail_count = 0


def generate_sensor_data():
    """生成模拟传感器数据"""
    hour = datetime.now().hour

    # 温度模拟 (15-35°C，中午高，晚上低)
    temp_base = 20 + 12 * math.sin((hour - 14) * math.pi / 12)
    temperature = round(temp_base + random.uniform(-1.5, 1.5), 1)

    # 湿度模拟 (40-80%，与温度相反)
    humidity_base = 60 - 20 * math.sin((hour - 14) * math.pi / 12)
    humidity = round(humidity_base + random.uniform(-8, 8), 1)
    humidity = max(20, min(95, humidity))

    # 电池电量模拟 (缓慢下降)
    if not hasattr(generate_sensor_data, 'battery'):
        generate_sensor_data.battery = 95.0
    generate_sensor_data.battery -= random.uniform(0, 0.1)
    if generate_sensor_data.battery < 10:
        generate_sensor_data.battery = 95.0
    battery = round(generate_sensor_data.battery, 1)

    # 设备状态 (0=正常, 1=警告, 2=故障)
    status_code = 0
    if temperature > 38 or battery < 15:
        status_code = 1
    elif temperature > 40 or battery < 10:
        status_code = 2

    return {
        "device_code": DEVICE_CODE,
        "timestamp": datetime.now().isoformat(),
        "data": {
            "temperature_c": temperature,
            "humidity_percent": humidity,
            "battery_percent": battery,
            "status_code": status_code
        }
    }


def send_data():
    """发送数据到 IoT 模块"""
    global sent_count, success_count, fail_count

    data = generate_sensor_data()
    sent_count += 1

    try:
        response = requests.post(
            INGEST_URL,
            json=data,
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code == 200:
            success_count += 1

            # 打印数据
            temp = data['data']['temperature_c']
            humidity = data['data']['humidity_percent']
            battery = data['data']['battery_percent']
            status = data['data']['status_code']

            # 状态图标
            if status == 0:
                status_icon = "✅"
            elif status == 1:
                status_icon = "⚠️"
            else:
                status_icon = "❌"

            print(f"\n📤 [{sent_count}] 上报成功")
            print(f"   🌡️ {temp}°C  💧 {humidity}%  🔋 {battery}%  {status_icon}")

        else:
            fail_count += 1
            print(f"\n❌ [{sent_count}] 上报失败: HTTP {response.status_code}")

    except requests.ConnectionError:
        fail_count += 1
        print(f"\n❌ [{sent_count}] 连接失败: 后端未启动")
    except Exception as e:
        fail_count += 1
        print(f"\n❌ [{sent_count}] 错误: {e}")


def send_loop():
    """数据发送循环"""
    print(f"\n🚀 开始发送数据 (间隔: {SEND_INTERVAL}秒)")
    print("=" * 60)
    print(f"设备代码: {DEVICE_CODE}")
    print(f"上报接口: {INGEST_URL}")
    print("=" * 60)

    while running:
        send_data()
        time.sleep(SEND_INTERVAL)


def signal_handler(sig, frame):
    global running
    print("\n\n🛑 正在关闭模拟器...")
    running = False

    print("\n📊 统计信息:")
    print(f"   总发送: {sent_count} 条")
    print(f"   成功: {success_count} 条")
    print(f"   失败: {fail_count} 条")
    if sent_count > 0:
        print(f"   成功率: {success_count / sent_count * 100:.1f}%")
    print("\n✅ 模拟器已关闭")
    sys.exit(0)


def main():
    print("=" * 70)
    print("   🌐 HTTP 设备模拟器 (纯上报模式)")
    print("=" * 70)
    print(f"后端地址: {IMBS_HOST}")
    print(f"上报接口: {INGEST_URL}")
    print(f"设备代码: {DEVICE_CODE}")
    print(f"发送间隔: {SEND_INTERVAL} 秒")
    print("=" * 70)

    print("\n⚠️  注意: 请确保设备已在系统中注册")
    print(f"   设备代码: {DEVICE_CODE}")
    print("   如果未注册，请先通过 API 注册设备")
    print("=" * 70)

    # 设置信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    input("\n按 Enter 开始发送数据...")

    # 选择发送模式
    print("\n📝 选择发送模式:")
    print("  1. 无限循环发送 (按 Ctrl+C 停止)")
    print("  2. 发送指定条数后停止")

    choice = input("请选择 (1/2): ").strip()

    if choice == '2':
        try:
            count = int(input("请输入发送条数: ").strip())
            print(f"\n🔢 将发送 {count} 条数据...")

            for i in range(count):
                if not running:
                    break
                send_data()
                if i < count - 1:
                    time.sleep(SEND_INTERVAL)

            print(f"\n✅ 已完成 {count} 条数据发送")

        except ValueError:
            print("❌ 无效输入，切换到无限循环模式")
            send_loop()
    else:
        send_loop()


if __name__ == "__main__":
    import os
    import sys

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from _runtime_guard import require_simulator_enabled

    require_simulator_enabled("http_device_simulator")
    main()