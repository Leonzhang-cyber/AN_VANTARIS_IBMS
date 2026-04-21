# test_websocket.py
import socketio
import time
import json

DEVICE_CODE = "HVAC_SIM_001"
sio = socketio.Client(logger=True, engineio_logger=True)

@sio.event
def connect():
    print("✅ 连接成功")
    sio.emit('subscribe_device', {'device_code': DEVICE_CODE})
    print("📡 已发送订阅")

@sio.event
def subscribed(data):
    print(f"✅ 订阅确认: {data}")

@sio.event
def device_data(data):
    print(f"\n📊 收到设备数据!")
    print(f"   设备: {data.get('device_code')}")
    print(f"   温度: {data.get('data', {}).get('temperature')}°C")
    print(f"   功率: {data.get('data', {}).get('power')}kW")

@sio.on('*')
def catch_all(event, data):
    print(f"📨 未处理事件: {event} -> {data}")

if __name__ == '__main__':
    sio.connect('http://localhost:5000', transports=['websocket'])
    print("等待数据...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        sio.disconnect()