#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt
import json
import time
import csv
import random
import math
from datetime import datetime, timedelta
import signal
import sys
import os
import threading

# ========== 配置信息 ==========
MQTT_BROKER = os.getenv("IBMS_MQTT_HOST", "127.0.0.1").strip() or "127.0.0.1"
MQTT_PORT = int(os.getenv("IBMS_MQTT_PORT", "1883").strip() or "1883")
MQTT_USERNAME = os.getenv("IBMS_MQTT_USERNAME", "replace-with-mqtt-user").strip() or "replace-with-mqtt-user"
MQTT_PASSWORD = os.getenv("IBMS_MQTT_PASSWORD", "replace-with-mqtt-password").strip() or "replace-with-mqtt-password"
MQTT_CLIENT_ID = f"air_quality_simulator_{int(time.time())}"

DEVICE_ID = "AIR_QUALITY_001"

TOPIC_DATA = f"building/air/{DEVICE_ID}/data"
TOPIC_COMMAND = f"building/air/{DEVICE_ID}/command"
TOPIC_STATUS = f"building/air/{DEVICE_ID}/status"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE_PATH = os.path.join(SCRIPT_DIR, "air_quality_data.csv")

SEND_INTERVAL = 5  # 发送间隔（秒）
SIMULATE_MODE = True  # CSV不存在时使用实时模拟

running = True
client = None
csv_data = None
connected = False
send_limit = None
sent_count = 0
publish_thread = None
user_input_thread = None


def generate_mock_csv_if_needed():
    """生成模拟CSV数据（典型的一天空气数据）"""
    if os.path.exists(CSV_FILE_PATH):
        return True

    print(f"⚠️ CSV文件不存在，正在生成模拟数据: {CSV_FILE_PATH}")

    data_rows = []
    start_time = datetime(2025, 6, 1, 0, 0, 0)

    for i in range(288):  # 24小时 * 12 (每5分钟)
        current_time = start_time + timedelta(minutes=5 * i)
        hour = current_time.hour

        # 基于时间的模拟数据
        # PM2.5: 早晚高峰较高，白天较低
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            pm25_base = 75 + random.uniform(-15, 25)  # 高峰时段
        elif 22 <= hour or hour <= 5:
            pm25_base = 45 + random.uniform(-10, 15)  # 夜间
        else:
            pm25_base = 55 + random.uniform(-15, 20)  # 白天

        # PM10 通常是 PM2.5 的 1.2-1.8 倍
        pm10_base = pm25_base * random.uniform(1.2, 1.8)

        # 温度: 14:00最高，凌晨最低
        temp_base = 15 + 12 * math.sin((hour - 14) * math.pi / 12)

        # 湿度: 与温度相反
        humidity_base = 80 - 30 * math.sin((hour - 14) * math.pi / 12)

        # 太阳辐射: 白天有，晚上为0
        if 6 <= hour <= 18:
            solar_base = 300 + 500 * math.sin((hour - 6) * math.pi / 12)
            solar_base = max(0, min(800, solar_base))
        else:
            solar_base = 0

        # 风速: 随机变化，白天稍大
        wind_base = random.uniform(1, 8) + (2 if 10 <= hour <= 16 else 0)

        # 电池电量: 缓慢下降，每天降2-3%
        battery_base = 98 - (i / 288) * 3

        # 设备状态: 大部分时间正常
        # 0=正常, 1=警告, 2=故障
        if random.random() > 0.98:  # 2% 概率警告
            status_code = 1
        elif random.random() > 0.995:  # 0.5% 概率故障
            status_code = 2
        else:
            status_code = 0

        row = {
            'timestamp': current_time.isoformat(),
            'temperature_c': round(temp_base + random.uniform(-1.5, 1.5), 1),
            'battery_percent': round(battery_base, 1),
            'status_code': status_code,  # 🆕 改为数字状态码
            'pm10_ugm3': round(pm10_base, 1),
            'pm25_ugm3': round(pm25_base, 1),
            'humidity_percent': round(humidity_base + random.uniform(-5, 5), 1),
            'solar_radiation_wm2': round(solar_base + random.uniform(-30, 30), 1),
            'wind_speed_ms': round(wind_base + random.uniform(-1, 1), 1)
        }
        data_rows.append(row)

    # 写入CSV
    with open(CSV_FILE_PATH, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['timestamp', 'temperature_c', 'battery_percent', 'status_code',
                      'pm10_ugm3', 'pm25_ugm3', 'humidity_percent',
                      'solar_radiation_wm2', 'wind_speed_ms']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data_rows)

    print(f"✅ 已生成 {len(data_rows)} 条模拟数据")
    return True


def load_csv_data():
    global csv_data
    try:
        with open(CSV_FILE_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            csv_data = list(reader)
        print(f"✅ 已加载 {len(csv_data)} 条空气检测数据")

        if len(csv_data) > 0:
            print(f"📋 CSV列: {list(csv_data[0].keys())}")
        return True
    except FileNotFoundError:
        if SIMULATE_MODE:
            return generate_mock_csv_if_needed() and load_csv_data()
        print(f"❌ CSV文件不存在: {CSV_FILE_PATH}")
        return False
    except Exception as e:
        print(f"❌ 加载CSV失败: {e}")
        return False


def get_next_data():
    if not hasattr(get_next_data, 'index'):
        get_next_data.index = 0

    if not csv_data:
        return generate_real_time_data()

    if get_next_data.index >= len(csv_data):
        get_next_data.index = 0
        print("\n🔄 数据循环，重新从第一条开始")

    row = csv_data[get_next_data.index]
    get_next_data.index += 1

    def safe_float(key, default=0.0):
        val = row.get(key, '')
        if val and str(val).strip():
            try:
                return float(val)
            except:
                return default
        return default

    def safe_int(key, default=0):
        val = row.get(key, '')
        if val and str(val).strip():
            try:
                return int(float(val))
            except:
                return default
        return default

    def safe_str(key, default=''):
        val = row.get(key, '')
        return str(val) if val else default

    data = {
        "device_id": DEVICE_ID,
        "client_id": MQTT_CLIENT_ID,
        "timestamp": row.get('timestamp', datetime.now().isoformat()),
        "seq": get_next_data.index,

        # 核心参数
        "temperature_c": safe_float('temperature_c'),
        "battery_percent": safe_float('battery_percent'),
        "status_code": safe_int('status_code', 0),  # 🆕 数字状态码

        # 空气质量参数
        "pm10_ugm3": safe_float('pm10_ugm3'),
        "pm25_ugm3": safe_float('pm25_ugm3'),

        # 环境参数
        "humidity_percent": safe_float('humidity_percent'),
        "solar_radiation_wm2": safe_float('solar_radiation_wm2'),
        "wind_speed_ms": safe_float('wind_speed_ms'),

        # 空气质量指数（计算值）
        "aqi": calculate_aqi(safe_float('pm25_ugm3'), safe_float('pm10_ugm3')),

        # 告警标志
        "pm25_alarm": safe_float('pm25_ugm3') > 75,
        "low_battery_alarm": safe_float('battery_percent') < 20,
        "high_temp_alarm": safe_float('temperature_c') > 35
    }

    return data


def calculate_aqi(pm25, pm10):
    """简化的AQI计算（基于PM2.5和PM10）"""
    if pm25 <= 35:
        aqi = int(pm25 * 50 / 35)
    elif pm25 <= 75:
        aqi = int(50 + (pm25 - 35) * 50 / 40)
    elif pm25 <= 115:
        aqi = int(100 + (pm25 - 75) * 50 / 40)
    elif pm25 <= 150:
        aqi = int(150 + (pm25 - 115) * 50 / 35)
    else:
        aqi = int(200 + (pm25 - 150) * 100 / 150)

    return min(500, max(0, aqi))


def get_status_text(code):
    """状态码转文本"""
    status_map = {0: "normal", 1: "warning", 2: "error"}
    return status_map.get(code, "unknown")


def generate_real_time_data():
    """实时生成模拟数据"""
    now = datetime.now()
    hour = now.hour

    # 基于时间的模拟逻辑
    if 7 <= hour <= 9 or 17 <= hour <= 19:
        pm25_base = 75 + random.uniform(-15, 25)
    elif 22 <= hour or hour <= 5:
        pm25_base = 45 + random.uniform(-10, 15)
    else:
        pm25_base = 55 + random.uniform(-15, 20)

    pm10_base = pm25_base * random.uniform(1.2, 1.8)

    # 温度模拟
    temp_base = 15 + 12 * math.sin((hour - 14) * math.pi / 12)

    # 湿度模拟
    humidity_base = 80 - 30 * math.sin((hour - 14) * math.pi / 12)

    # 太阳辐射模拟
    if 6 <= hour <= 18:
        solar_base = 300 + 500 * math.sin((hour - 6) * math.pi / 12)
        solar_base = max(0, min(800, solar_base))
    else:
        solar_base = 0

    # 风速模拟
    wind_base = random.uniform(1, 8) + (2 if 10 <= hour <= 16 else 0)

    # 电池模拟（缓慢下降）
    if not hasattr(generate_real_time_data, 'battery'):
        generate_real_time_data.battery = 98
    generate_real_time_data.battery -= 0.001
    if generate_real_time_data.battery < 5:
        generate_real_time_data.battery = 98

    # 设备状态模拟 (0=正常, 1=警告, 2=故障)
    status_random = random.random()
    if status_random > 0.98:
        status_code = 1  # 警告
    elif status_random > 0.995:
        status_code = 2  # 故障
    else:
        status_code = 0  # 正常

    pm25 = pm25_base + random.uniform(-5, 10)
    pm10 = pm10_base + random.uniform(-10, 20)

    return {
        "device_id": DEVICE_ID,
        "client_id": MQTT_CLIENT_ID,
        "timestamp": now.isoformat(),
        "seq": int(time.time()),

        "temperature_c": round(temp_base + random.uniform(-1.5, 1.5), 1),
        "battery_percent": round(generate_real_time_data.battery, 1),
        "status_code": status_code,  # 🆕 数字状态码

        "pm10_ugm3": round(max(0, pm10), 1),
        "pm25_ugm3": round(max(0, pm25), 1),

        "humidity_percent": round(humidity_base + random.uniform(-5, 5), 1),
        "solar_radiation_wm2": round(max(0, solar_base + random.uniform(-30, 30)), 1),
        "wind_speed_ms": round(wind_base + random.uniform(-1, 1), 1),

        "aqi": calculate_aqi(max(0, pm25), max(0, pm10)),
        "pm25_alarm": pm25 > 75,
        "low_battery_alarm": generate_real_time_data.battery < 20,
        "high_temp_alarm": (temp_base + random.uniform(-1.5, 1.5)) > 35
    }


def on_connect(client, userdata, flags, rc, properties=None):
    global connected
    if rc == 0:
        connected = True
        print(f"\n✅ MQTT连接成功!")
        print(f"  Broker: {MQTT_BROKER}:{MQTT_PORT}")
        print(f"  Client ID: {MQTT_CLIENT_ID}")
        print(f"  Device ID: {DEVICE_ID}")

        client.subscribe(TOPIC_COMMAND)
        print(f"📡 已订阅命令Topic: {TOPIC_COMMAND}")

        status_msg = {
            "status": "online",
            "timestamp": datetime.now().isoformat(),
            "device_id": DEVICE_ID,
            "client_id": MQTT_CLIENT_ID,
            "device_type": "air_quality_monitor",
            "battery_percent": 98,
            "firmware_version": "2.1.0"
        }
        client.publish(TOPIC_STATUS, json.dumps(status_msg), qos=1)
        print(f"📢 已发布上线状态: {TOPIC_STATUS}")

        print("\n✅ 空气检测设备已就绪")
        print("📊 监测参数: 温度 | 湿度 | PM2.5 | PM10 | 太阳辐射 | 风速 | 电池电量")
        print("💡 命令: send 10 (发送10条), send (无限发送), quit (退出)\n")
    else:
        connected = False
        print(f"\n❌ MQTT连接失败, 返回码: {rc}")


def on_disconnect(client, userdata, rc, properties=None):
    global connected
    connected = False
    print(f"\n⚠️ MQTT断开连接, 返回码: {rc}")


def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode('utf-8')
        print(f"\n📨 [收到命令] [{msg.topic}]: {payload}")

        try:
            command = json.loads(payload)
            cmd_type = command.get('command') or command.get('type')

            if cmd_type == 'get_status':
                print(f"  🔍 执行: 获取设备状态")
                response = {
                    "response_to": "get_status",
                    "status": "online",
                    "device_id": DEVICE_ID,
                    "temperature": 23.5,
                    "pm25": 45.2,
                    "pm10": 68.3,
                    "battery": 92,
                    "timestamp": datetime.now().isoformat()
                }
                client.publish(TOPIC_STATUS, json.dumps(response), qos=1)
                print(f"  📤 已回复设备状态")
            elif cmd_type == 'calibrate_sensor':
                print(f"  🔧 执行: 传感器校准")
                response = {
                    "response_to": "calibrate_sensor",
                    "status": "calibrated",
                    "timestamp": datetime.now().isoformat()
                }
                client.publish(TOPIC_STATUS, json.dumps(response), qos=1)
            elif cmd_type == 'set_report_interval':
                interval = command.get('value', 5)
                print(f"  ⏱️ 执行: 设置上报间隔 → {interval}秒")
            else:
                print(f"  ❓ 未知命令: {cmd_type}")
        except json.JSONDecodeError:
            print(f"  📄 非JSON命令: {payload}")
    except Exception as e:
        print(f"处理消息错误: {e}")


def get_quality_level(pm25):
    """获取空气质量等级"""
    if pm25 <= 35:
        return "优"
    elif pm25 <= 75:
        return "良"
    elif pm25 <= 115:
        return "轻度污染"
    elif pm25 <= 150:
        return "中度污染"
    else:
        return "重度污染"


def publish_loop():
    global running, connected, sent_count, send_limit

    sequence = 0
    error_count = 0

    while running:
        try:
            if not connected:
                time.sleep(1)
                continue

            if send_limit is not None and sent_count >= send_limit:
                print(f"\n✅ 已完成 {send_limit} 条数据发送")
                print("💡 输入 'send' 继续发送，'send 10' 发送10条，'quit' 退出\n")
                send_limit = None
                sent_count = 0
                time.sleep(1)
                continue

            data = get_next_data()
            if data is None:
                print("⚠️ 无可用数据，等待...")
                time.sleep(5)
                continue

            payload = json.dumps(data)

            result = client.publish(TOPIC_DATA, payload, qos=1)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                sent_count += 1

                # 空气质量图标
                aqi_level = get_quality_level(data.get('pm25_ugm3', 0))
                if data.get('pm25_ugm3', 0) <= 35:
                    quality_icon = "😊"
                elif data.get('pm25_ugm3', 0) <= 75:
                    quality_icon = "🙂"
                elif data.get('pm25_ugm3', 0) <= 115:
                    quality_icon = "😷"
                else:
                    quality_icon = "⚠️"

                # 状态文本
                status_text = get_status_text(data.get('status_code', 0))

                # 告警标识
                alarm_icons = []
                if data.get('pm25_alarm'):
                    alarm_icons.append("PM2.5超标")
                if data.get('low_battery_alarm'):
                    alarm_icons.append("低电量")
                if data.get('high_temp_alarm'):
                    alarm_icons.append("高温")
                alarm_str = f" [{'/'.join(alarm_icons)}]" if alarm_icons else ""

                if send_limit is None:
                    print(f"{quality_icon} [{sequence}] 📤 {alarm_str}")
                    print(
                        f"          🌡️ 温度:{data['temperature_c']}°C  💧湿度:{data['humidity_percent']}%  🔋电量:{data['battery_percent']}%")
                    print(
                        f"          🏭 PM2.5:{data['pm25_ugm3']}μg/m³  PM10:{data['pm10_ugm3']}μg/m³  AQI:{data.get('aqi', 0)} ({aqi_level})")
                    print(
                        f"          ☀️ 太阳辐射:{data['solar_radiation_wm2']}W/m²  💨风速:{data['wind_speed_ms']}m/s  📟状态:{status_text}({data['status_code']})")
                else:
                    print(f"{quality_icon} [{sequence}] 📤 [{sent_count}/{send_limit}] {alarm_str}")
                    print(
                        f"          🌡️ {data['temperature_c']}°C | PM2.5:{data['pm25_ugm3']} | PM10:{data['pm10_ugm3']} | 电量:{data['battery_percent']}% | 状态:{data['status_code']}")

                error_count = 0
            else:
                error_count += 1
                print(f"❌ 发布失败 ({error_count}), 返回码: {result.rc}")
                if error_count >= 3:
                    connected = False

            sequence += 1
            time.sleep(SEND_INTERVAL)

        except Exception as e:
            print(f"发布循环错误: {e}")
            time.sleep(1)


def user_input_handler():
    global running, send_limit, sent_count

    while running:
        try:
            user_input = input().strip().lower()

            if user_input in ['quit', 'exit', 'q']:
                print("\n🛑 正在关闭空气检测设备...")
                running = False
                break
            elif user_input == 'send':
                send_limit = None
                sent_count = 0
                print("\n🔄 切换到无限发送模式...\n")
            elif user_input.startswith('send '):
                parts = user_input.split()
                if len(parts) == 2:
                    try:
                        num = int(parts[1])
                        if num > 0:
                            send_limit = num
                            sent_count = 0
                            print(f"\n🔄 将发送 {num} 条数据...\n")
                        else:
                            print("❌ 请输入大于0的数字")
                    except ValueError:
                        print("❌ 请输入有效数字, 例如: send 10")
                else:
                    print("❌ 格式错误, 使用: send 数字 或 send")
            elif user_input == 'status':
                print(f"\n📊 设备状态:")
                print(f"  MQTT连接: {'✅ 已连接' if connected else '❌ 未连接'}")
                print(f"  已发送数据: {sent_count} 条")
                print(f"  发送限制: {'无限制' if send_limit is None else f'{send_limit} 条'}")
                print(f"  数据源: {'CSV文件' if csv_data else '实时生成'}")
                print(f"  发送间隔: {SEND_INTERVAL} 秒\n")
            elif user_input == 'help':
                print("\n📖 可用命令:")
                print("  send        - 无限循环发送数据")
                print("  send 10     - 发送10条数据")
                print("  status      - 查看设备状态")
                print("  quit/exit   - 退出程序")
                print("  help        - 显示帮助")
                print("\n📊 监测参数说明:")
                print("  PM2.5/PM10  - 颗粒物浓度 (μg/m³)")
                print("  温度         - 环境温度 (℃)")
                print("  湿度         - 相对湿度 (%)")
                print("  太阳辐射     - 太阳辐射强度 (W/m²)")
                print("  风速         - 风速 (m/s)")
                print("  电池电量     - 设备电量 (%)")
                print("  状态码       - 0=正常,1=警告,2=故障\n")
            elif user_input:
                print(f"❌ 未知命令: {user_input}, 输入 'help' 查看帮助")

        except EOFError:
            break
        except Exception as e:
            print(f"输入错误: {e}")


def signal_handler(sig, frame):
    global running, client, connected
    print("\n\n🛑 正在关闭空气检测设备...")
    running = False

    if client and connected:
        try:
            offline_msg = {
                "status": "offline",
                "timestamp": datetime.now().isoformat(),
                "device_id": DEVICE_ID,
                "reason": "simulator_shutdown"
            }
            client.publish(TOPIC_STATUS, json.dumps(offline_msg), qos=1)
            print("📢 已发布离线状态")
            time.sleep(0.5)
        except Exception as e:
            print(f"发布离线状态失败: {e}")

        client.disconnect()
        client.loop_stop()

    print("✅ 空气检测设备已关闭")
    sys.exit(0)


def main():
    global client, send_limit, csv_data

    print("=" * 70)
    print("   🌍 MQTT 空气检测设备模拟器")
    print("=" * 70)
    print(f"MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"设备ID: {DEVICE_ID}")
    print(f"设备类型: 空气检测仪 (Air Quality Monitor)")
    print(f"数据Topic: {TOPIC_DATA} (发布)")
    print(f"命令Topic: {TOPIC_COMMAND} (订阅)")
    print(f"状态Topic: {TOPIC_STATUS}")
    print(f"发送间隔: {SEND_INTERVAL} 秒")
    print("=" * 70)

    if not load_csv_data() and not SIMULATE_MODE:
        print("\n❌ 无法加载数据，程序退出")
        sys.exit(1)

    try:
        client = mqtt.Client(client_id=MQTT_CLIENT_ID, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    except (AttributeError, TypeError):
        client = mqtt.Client(client_id=MQTT_CLIENT_ID)

    if MQTT_USERNAME:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    try:
        print(f"\n🔌 正在连接MQTT服务器 {MQTT_BROKER}:{MQTT_PORT}...")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        input_thread = threading.Thread(target=user_input_handler, daemon=True)
        input_thread.start()

        print("\n✅ 空气检测设备模拟器已启动!")
        print("📖 输入 'help' 查看帮助\n")

        while True:
            try:
                user_input = input("📝 请输入要发送的数据条数 (直接回车=无限循环, 输入数字=发送指定条数): ").strip()
                if user_input == "":
                    send_limit = None
                    print("\n🔁 模式: 无限循环发送\n")
                    break
                else:
                    num = int(user_input)
                    if num > 0:
                        send_limit = num
                        print(f"\n🔢 模式: 发送 {num} 条数据\n")
                        break
                    else:
                        print("❌ 请输入大于0的数字")
            except ValueError:
                print("❌ 请输入有效的数字，或直接回车")
            except KeyboardInterrupt:
                raise

        publish_thread = threading.Thread(target=publish_loop, daemon=True)
        publish_thread.start()

        while running:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断")
    except ConnectionRefusedError:
        print(f"\n❌ 无法连接MQTT服务器: {MQTT_BROKER}:{MQTT_PORT}")
        print("请检查MQTT服务是否运行")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
    finally:
        if client:
            client.loop_stop()
            client.disconnect()
        print("🌍 空气检测设备已关闭")


if __name__ == "__main__":
    import os
    import sys

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from _runtime_guard import require_testmqtt_enabled

    require_testmqtt_enabled("air_quality_simulator")
    main()