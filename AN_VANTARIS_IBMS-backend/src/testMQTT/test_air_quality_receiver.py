#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
空气检测设备 MQTT 接收测试脚本
用于测试 AIR_QUALITY_001 设备的数据接收和字段映射
"""

import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime
import os
import sys

# ========== 配置信息 ==========
MQTT_BROKER = os.getenv("IBMS_MQTT_HOST", "127.0.0.1").strip() or "127.0.0.1"
MQTT_PORT = int(os.getenv("IBMS_MQTT_PORT", "1883").strip() or "1883")
MQTT_USERNAME = os.getenv("IBMS_MQTT_USERNAME", "replace-with-mqtt-user").strip() or "replace-with-mqtt-user"
MQTT_PASSWORD = os.getenv("IBMS_MQTT_PASSWORD", "replace-with-mqtt-password").strip() or "replace-with-mqtt-password"

DEVICE_ID = "AIR_QUALITY_001"

TOPIC_DATA = f"building/air/{DEVICE_ID}/data"
TOPIC_COMMAND = f"building/air/{DEVICE_ID}/command"
TOPIC_STATUS = f"building/air/{DEVICE_ID}/status"

# 接收到的数据统计
data_count = 0
last_data = None


def on_connect(client, userdata, flags, rc, properties=None):
    """MQTT 连接回调"""
    if rc == 0:
        print(f"\n✅ MQTT 连接成功!")
        print(f"  Broker: {MQTT_BROKER}:{MQTT_PORT}")

        # 订阅所有相关主题
        client.subscribe(TOPIC_DATA)
        client.subscribe(TOPIC_STATUS)
        client.subscribe(TOPIC_COMMAND)

        print(f"📡 已订阅主题:")
        print(f"   - {TOPIC_DATA} (数据)")
        print(f"   - {TOPIC_STATUS} (状态)")
        print(f"   - {TOPIC_COMMAND} (命令)")
        print("\n" + "=" * 70)
        print("等待接收数据...")
        print("=" * 70 + "\n")
    else:
        print(f"\n❌ MQTT 连接失败, 返回码: {rc}")


def on_disconnect(client, userdata, rc, properties=None):
    """MQTT 断开回调"""
    print(f"\n⚠️ MQTT 断开连接, 返回码: {rc}")
    print("尝试重连...")


def on_message(client, userdata, msg):
    """接收消息回调"""
    global data_count, last_data

    try:
        payload = json.loads(msg.payload.decode('utf-8'))
        data_count += 1
        last_data = payload

        timestamp = datetime.now().strftime("%H:%M:%S")

        print(f"\n{'=' * 70}")
        print(f"📨 [{timestamp}] 收到消息 #{data_count}")
        print(f"📌 Topic: {msg.topic}")
        print(f"{'=' * 70}")

        # 根据主题类型显示不同内容
        if msg.topic == TOPIC_DATA:
            print_air_quality_data(payload)
        elif msg.topic == TOPIC_STATUS:
            print_device_status(payload)
        elif msg.topic == TOPIC_COMMAND:
            print_command_response(payload)
        else:
            print(f"📄 原始数据: {json.dumps(payload, indent=2, ensure_ascii=False)}")

    except json.JSONDecodeError as e:
        print(f"\n❌ JSON 解析失败: {e}")
        print(f"原始消息: {msg.payload.decode('utf-8')}")
    except Exception as e:
        print(f"\n❌ 处理消息失败: {e}")


def print_air_quality_data(data):
    """打印空气质量数据"""
    print("🌍 空气检测数据")
    print("-" * 70)

    # 时间信息
    timestamp = data.get('timestamp', '未知')
    seq = data.get('seq', '未知')
    print(f"⏰ 时间: {timestamp}")
    print(f"🔢 序列号: {seq}")

    # 核心参数
    print(f"\n📊 核心参数:")
    print(f"   🌡️  温度: {data.get('temperature_c', 0)} °C")
    print(f"   💧 湿度: {data.get('humidity_percent', 0)} %")
    print(f"   🔋 电池电量: {data.get('battery_percent', 0)} %")

    # 空气质量参数
    print(f"\n🏭 空气质量:")
    pm25 = data.get('pm25_ugm3', 0)
    pm10 = data.get('pm10_ugm3', 0)
    aqi = data.get('aqi', 0)

    # 空气质量等级
    if pm25 <= 35:
        quality = "优 😊"
        quality_color = "🟢"
    elif pm25 <= 75:
        quality = "良 🙂"
        quality_color = "🟡"
    elif pm25 <= 115:
        quality = "轻度污染 😷"
        quality_color = "🟠"
    elif pm25 <= 150:
        quality = "中度污染 ⚠️"
        quality_color = "🔴"
    else:
        quality = "重度污染 ❌"
        quality_color = "⚫"

    print(f"   PM2.5: {pm25} μg/m³")
    print(f"   PM10:  {pm10} μg/m³")
    print(f"   AQI:   {aqi} ({quality})")

    # 环境参数
    print(f"\n☁️ 环境参数:")
    print(f"   ☀️ 太阳辐射: {data.get('solar_radiation_wm2', 0)} W/m²")
    print(f"   💨 风速: {data.get('wind_speed_ms', 0)} m/s")

    # 设备状态
    print(f"\n📟 设备状态:")
    status = data.get('device_status', 'unknown')
    status_code = data.get('device_status_code', 0)

    if status == 'normal':
        status_icon = "✅"
    elif status == 'warning':
        status_icon = "⚠️"
    elif status == 'error':
        status_icon = "❌"
    else:
        status_icon = "❓"

    print(f"   {status_icon} 状态: {status} (code: {status_code})")

    # 告警信息
    print(f"\n🚨 告警状态:")
    alarms = []
    if data.get('pm25_alarm'):
        alarms.append("PM2.5超标")
    if data.get('low_battery_alarm'):
        alarms.append("低电量")
    if data.get('high_temp_alarm'):
        alarms.append("高温")

    if alarms:
        for alarm in alarms:
            print(f"   ⚠️ {alarm}")
    else:
        print("   ✅ 无告警")

    # 设备标识
    print(f"\n🆔 设备标识:")
    print(f"   Device ID: {data.get('device_id', '未知')}")
    print(f"   Client ID: {data.get('client_id', '未知')}")


def print_device_status(data):
    """打印设备状态"""
    print("📟 设备状态信息")
    print("-" * 70)
    print(f"   状态: {data.get('status', 'unknown')}")
    print(f"   设备ID: {data.get('device_id', '未知')}")
    print(f"   电池电量: {data.get('battery_percent', '未知')}%")
    print(f"   设备类型: {data.get('device_type', '未知')}")
    print(f"   固件版本: {data.get('firmware_version', '未知')}")
    print(f"   时间戳: {data.get('timestamp', '未知')}")


def print_command_response(data):
    """打印命令响应"""
    print("📨 命令响应")
    print("-" * 70)
    response_to = data.get('response_to', 'unknown')
    print(f"   响应命令: {response_to}")
    print(f"   状态: {data.get('status', 'unknown')}")

    # 如果是状态响应，显示额外信息
    if response_to == 'get_status':
        print(f"   温度: {data.get('temperature', '未知')} °C")
        print(f"   PM2.5: {data.get('pm25', '未知')} μg/m³")
        print(f"   PM10: {data.get('pm10', '未知')} μg/m³")
        print(f"   电池: {data.get('battery', '未知')} %")

    print(f"   时间戳: {data.get('timestamp', '未知')}")


def test_command():
    """测试发送命令到设备"""
    try:
        import paho.mqtt.publish as publish

        print("\n" + "=" * 70)
        print("📝 发送测试命令")
        print("=" * 70)
        print("1. get_status - 获取设备状态")
        print("2. calibrate_sensor - 校准传感器")
        print("3. set_report_interval - 设置上报间隔")
        print("0. 取消")

        choice = input("\n请选择命令: ").strip()

        if choice == '1':
            command = {"command": "get_status"}
            print(f"\n发送命令: {command}")
            publish.single(TOPIC_COMMAND, json.dumps(command),
                           hostname=MQTT_BROKER, port=MQTT_PORT,
                           auth={'username': MQTT_USERNAME, 'password': MQTT_PASSWORD})
            print("✅ 命令已发送")

        elif choice == '2':
            command = {"command": "calibrate_sensor"}
            print(f"\n发送命令: {command}")
            publish.single(TOPIC_COMMAND, json.dumps(command),
                           hostname=MQTT_BROKER, port=MQTT_PORT,
                           auth={'username': MQTT_USERNAME, 'password': MQTT_PASSWORD})
            print("✅ 命令已发送")

        elif choice == '3':
            interval = input("请输入上报间隔(秒): ").strip()
            command = {"command": "set_report_interval", "value": int(interval)}
            print(f"\n发送命令: {command}")
            publish.single(TOPIC_COMMAND, json.dumps(command),
                           hostname=MQTT_BROKER, port=MQTT_PORT,
                           auth={'username': MQTT_USERNAME, 'password': MQTT_PASSWORD})
            print("✅ 命令已发送")

        elif choice == '0':
            print("已取消")
        else:
            print("❌ 无效选择")

    except Exception as e:
        print(f"❌ 发送命令失败: {e}")


def main():
    print("=" * 70)
    print("   🌍 空气检测设备 MQTT 接收测试工具")
    print("=" * 70)
    print(f"MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"监听设备: {DEVICE_ID}")
    print(f"数据主题: {TOPIC_DATA}")
    print(f"状态主题: {TOPIC_STATUS}")
    print(f"命令主题: {TOPIC_COMMAND}")
    print("=" * 70)

    # 创建 MQTT 客户端
    try:
        client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    except (AttributeError, TypeError):
        client = mqtt.Client()

    # 设置认证
    if MQTT_USERNAME:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    # 设置回调
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    try:
        # 连接
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()

        print("\n✅ 测试工具已启动")
        print("📖 可用命令:")
        print("  stats - 显示统计信息")
        print("  send  - 发送测试命令")
        print("  quit  - 退出程序")
        print("\n等待接收设备数据...\n")

        while True:
            cmd = input().strip().lower()

            if cmd == 'quit' or cmd == 'exit':
                print("\n🛑 正在关闭...")
                break
            elif cmd == 'stats':
                print("\n📊 统计信息:")
                print(f"   已接收数据: {data_count} 条")
                if last_data:
                    print(f"   最后数据时间: {last_data.get('timestamp', '未知')}")
            elif cmd == 'send':
                test_command()
            elif cmd == 'help':
                print("\n📖 可用命令:")
                print("  stats - 显示统计信息")
                print("  send  - 发送测试命令")
                print("  quit  - 退出程序")
            elif cmd:
                print(f"❌ 未知命令: {cmd}")

    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断")
    except ConnectionRefusedError:
        print(f"\n❌ 无法连接 MQTT 服务器: {MQTT_BROKER}:{MQTT_PORT}")
        print("请检查 MQTT 服务是否运行")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
    finally:
        if client:
            client.loop_stop()
            client.disconnect()
        print("\n测试工具已关闭")
        print(f"共接收数据: {data_count} 条")


if __name__ == "__main__":
    import os
    import sys

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from _runtime_guard import require_testmqtt_enabled

    require_testmqtt_enabled("test_air_quality_receiver")
    main()