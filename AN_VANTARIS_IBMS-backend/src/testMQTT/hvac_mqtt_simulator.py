#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt
import json
import time
import csv
from datetime import datetime
import signal
import sys
import os
import threading

MQTT_BROKER = os.getenv("IBMS_MQTT_HOST", "127.0.0.1").strip() or "127.0.0.1"
MQTT_PORT = int(os.getenv("IBMS_MQTT_PORT", "1883").strip() or "1883")
MQTT_USERNAME = os.getenv("IBMS_MQTT_USERNAME", "replace-with-mqtt-user").strip() or "replace-with-mqtt-user"
MQTT_PASSWORD = os.getenv("IBMS_MQTT_PASSWORD", "replace-with-mqtt-password").strip() or "replace-with-mqtt-password"
MQTT_CLIENT_ID = f"hvac_simulator_{int(time.time())}"

DEVICE_ID = "HVAC_SIM_001"

TOPIC_DATA = f"building/hvac/{DEVICE_ID}/data"
TOPIC_COMMAND = f"building/hvac/{DEVICE_ID}/command"
TOPIC_STATUS = f"building/hvac/{DEVICE_ID}/status"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE_PATH = os.path.join(SCRIPT_DIR, "hvac_2025_prediction_data.csv")

SEND_INTERVAL = 5

running = True
client = None
csv_data = None
connected = False
send_limit = None  # 发送次数限制，None表示无限循环
sent_count = 0  # 已发送计数
publish_thread = None  # 发送线程
user_input_thread = None  # 用户输入线程


def load_csv_data():
    global csv_data
    try:
        with open(CSV_FILE_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            csv_data = list(reader)
        print(f"Loaded {len(csv_data)} records from CSV")

        if len(csv_data) > 0:
            print(f"CSV columns: {list(csv_data[0].keys())}")
        return True
    except FileNotFoundError:
        print(f"CSV file not found: {CSV_FILE_PATH}")
        return False
    except Exception as e:
        print(f"Failed to load CSV: {e}")
        return False


def get_next_data():
    if not hasattr(get_next_data, 'index'):
        get_next_data.index = 0

    if not csv_data:
        return None

    if get_next_data.index >= len(csv_data):
        get_next_data.index = 0
        print("\nData looped, restart from first record")

    row = csv_data[get_next_data.index]
    get_next_data.index += 1

    def safe_float(key):
        val = row.get(key, '')
        if val and str(val).strip():
            try:
                return float(val)
            except:
                return 0.0
        return 0.0

    def safe_int(key):
        val = row.get(key, '')
        if val and str(val).strip():
            try:
                return int(float(val))
            except:
                return 0
        return 0

    # 🆕 从 CSV 中获取原始时间戳，如果没有则使用当前时间
    original_timestamp = row.get('timestamp', '')
    if original_timestamp:
        # 保留原始时间戳
        final_timestamp = original_timestamp
    else:
        # 如果没有原始时间戳，使用当前时间
        final_timestamp = datetime.now().isoformat()

    data = {
        "device_id": MQTT_CLIENT_ID,
        # "timestamp": datetime.now().isoformat(),
        "timestamp": final_timestamp,
        "seq": get_next_data.index,
        "power_kw": safe_float('chiller_A_power_kW'),
        "setpoint_c": safe_float('chilled_water_temp_setpoint'),
        "temp_c": safe_float('zone_1_temp'),
        "damper_percent": safe_float('ahu_1_damper_pos'),
        "outdoor_temp_c": safe_float('outdoor_air_temp'),
        "dew_point_c": safe_float('dew_point_temp'),
        "solar_w_m2": safe_float('solar_radiation_w_m2'),
        "occupancy_rate": safe_float('occupancy_schedule'),
        "chiller_status": safe_int('chiller_A_status'),
        "is_holiday": row.get('is_holiday', 'False') == 'True'
    }

    return data


def on_connect(client, userdata, flags, rc, properties=None):
    global connected
    if rc == 0:
        connected = True
        print(f"\n✅ MQTT connected successfully!")
        print(f"  Broker: {MQTT_BROKER}:{MQTT_PORT}")
        print(f"  Client ID: {MQTT_CLIENT_ID}")

        client.subscribe(TOPIC_COMMAND)
        print(f"📡 Subscribed to command topic: {TOPIC_COMMAND}")

        status_msg = {
            "status": "online",
            "timestamp": datetime.now().isoformat(),
            "device_id": MQTT_CLIENT_ID
        }
        client.publish(TOPIC_STATUS, json.dumps(status_msg), qos=1)
        print(f"📢 Published online status to: {TOPIC_STATUS}")

        print("\n✅ 设备已就绪，可以接收命令")
        print("💡 输入 'send 5' 发送5条数据，输入 'send' 无限发送，输入 'quit' 退出\n")
    else:
        connected = False
        print(f"\n❌ MQTT connection failed, return code: {rc}")


def on_disconnect(client, userdata, rc, properties=None):
    global connected
    connected = False
    print(f"\n⚠️ MQTT disconnected, return code: {rc}")


def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode('utf-8')
        print(f"\n📨 [收到命令] [{msg.topic}]: {payload}")

        try:
            command = json.loads(payload)
            cmd_type = command.get('command') or command.get('type')

            if cmd_type == 'set_setpoint':
                new_setpoint = command.get('value')
                print(f"  🎛️ 执行: 设置温度 → {new_setpoint}°C")
            elif cmd_type == 'get_status':
                print(f"  🔍 执行: 获取设备状态")
                response = {
                    "response_to": "get_status",
                    "status": "online",
                    "temperature": 22.5,
                    "power": 45.2,
                    "timestamp": datetime.now().isoformat(),
                    "device_id": MQTT_CLIENT_ID
                }
                client.publish(TOPIC_STATUS, json.dumps(response), qos=1)
                print(f"  📤 已回复设备状态")
            elif cmd_type == 'set_damper':
                new_pos = command.get('value')
                print(f"  🎛️ 执行: 设置风门 → {new_pos}%")
            else:
                print(f"  ❓ 未知命令: {cmd_type}")
        except json.JSONDecodeError:
            print(f"  📄 非JSON命令: {payload}")
    except Exception as e:
        print(f"Error processing message: {e}")


def publish_loop():
    """数据发送循环"""
    global running, connected, sent_count, send_limit

    sequence = 0
    error_count = 0

    while running:
        try:
            if not connected:
                time.sleep(1)
                continue

            # 如果 send_limit 为 None，无限发送
            # 如果 send_limit 有值，发送指定数量后停止
            if send_limit is not None and sent_count >= send_limit:
                print(f"\n✅ 已完成 {send_limit} 条数据发送")
                print("💡 输入 'send' 继续发送，输入 'send 10' 发送10条，输入 'quit' 退出\n")
                # 重置限制，等待用户输入
                send_limit = None
                sent_count = 0
                time.sleep(1)
                continue

            data = get_next_data()
            if data is None:
                print("No data available, check CSV file")
                time.sleep(5)
                continue

            payload = json.dumps(data)

            result = client.publish(TOPIC_DATA, payload, qos=1)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                sent_count += 1
                if send_limit is None:
                    print(
                        f"[{sequence}] 📤 数据已发送 | 功率: {data['power_kw']}kW | 温度: {data['temp_c']}°C | 室外: {data['outdoor_temp_c']}°C")
                else:
                    print(
                        f"[{sequence}] 📤 数据已发送 ({sent_count}/{send_limit}) | 功率: {data['power_kw']}kW | 温度: {data['temp_c']}°C")
                error_count = 0
            else:
                error_count += 1
                print(f"❌ Publish failed ({error_count}), return code: {result.rc}")
                if error_count >= 3:
                    connected = False

            sequence += 1
            time.sleep(SEND_INTERVAL)

        except Exception as e:
            print(f"Publish loop error: {e}")
            time.sleep(1)


def user_input_handler():
    """处理用户输入"""
    global running, send_limit, sent_count

    while running:
        try:
            user_input = input().strip().lower()

            if user_input == 'quit' or user_input == 'exit':
                print("\n🛑 正在关闭模拟器...")
                running = False
                break
            elif user_input == 'send':
                # 无限发送
                send_limit = None
                sent_count = 0
                print("\n🔄 切换到无限发送模式，开始发送数据...\n")
            elif user_input.startswith('send '):
                # 发送指定数量，如 "send 10"
                parts = user_input.split()
                if len(parts) == 2:
                    try:
                        num = int(parts[1])
                        if num > 0:
                            send_limit = num
                            sent_count = 0
                            print(f"\n🔄 将发送 {num} 条数据，开始发送...\n")
                        else:
                            print("❌ 请输入大于0的数字")
                    except ValueError:
                        print("❌ 请输入有效的数字，例如: send 10")
                else:
                    print("❌ 格式错误，请使用: send 数字 或 send")
            elif user_input == 'help':
                print("\n📖 可用命令:")
                print("  send        - 无限循环发送数据")
                print("  send 10     - 发送10条数据")
                print("  quit/exit   - 退出程序")
                print("  help        - 显示帮助\n")
            elif user_input:
                print(f"❌ 未知命令: {user_input}，输入 'help' 查看帮助")

        except EOFError:
            break
        except Exception as e:
            print(f"Input error: {e}")


def signal_handler(sig, frame):
    global running, client, connected
    print("\n\n🛑 Shutting down MQTT simulator...")
    running = False

    if client and connected:
        try:
            offline_msg = {
                "status": "offline",
                "timestamp": datetime.now().isoformat(),
                "device_id": MQTT_CLIENT_ID
            }
            client.publish(TOPIC_STATUS, json.dumps(offline_msg), qos=1)
            print("📢 Published offline status")
            time.sleep(0.5)
        except Exception as e:
            print(f"Failed to publish offline status: {e}")

        client.disconnect()
        client.loop_stop()

    print("Simulator closed")
    sys.exit(0)


def main(on_publish=None):
    global client, send_limit

    print("=" * 70)
    print("   HVAC MQTT Device Simulator")
    print("=" * 70)
    print(f"MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"Device ID: {DEVICE_ID}")
    print(f"Data Topic: {TOPIC_DATA} (publish)")
    print(f"Command Topic: {TOPIC_COMMAND} (subscribe)")
    print(f"Send Interval: {SEND_INTERVAL} seconds")
    print("=" * 70)

    if not load_csv_data():
        print("\nCannot load CSV data, program exit")
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
    client.on_publish = on_publish

    try:
        print(f"\nConnecting to MQTT server {MQTT_BROKER}:{MQTT_PORT}...")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # 启动用户输入线程
        print("\n💬 正在启动命令控制台...")
        input_thread = threading.Thread(target=user_input_handler, daemon=True)
        input_thread.start()

        print("\n✅ 模拟器已启动！")
        print("📖 输入 'help' 查看可用命令\n")

        # 先询问用户要发送多少条
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

        # 启动数据发送线程
        publish_thread = threading.Thread(target=publish_loop, daemon=True)
        publish_thread.start()

        # 等待程序结束
        while running:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断")
    except ConnectionRefusedError:
        print(f"\n❌ Cannot connect to MQTT server: {MQTT_BROKER}:{MQTT_PORT}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        if client:
            client.loop_stop()
            client.disconnect()
        print("Simulator closed")


if __name__ == "__main__":
    import os
    import sys

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from _runtime_guard import require_testmqtt_enabled

    require_testmqtt_enabled("hvac_mqtt_simulator")
    main()