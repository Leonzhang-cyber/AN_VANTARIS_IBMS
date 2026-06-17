#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
海康 ISUP/Ehome 设备模拟器
模拟 4G 摄像头，通过 ISUP 协议主动注册到驱动并上报视频流
支持：设备注册、心跳保活、视频上报、PTZ控制响应

运行模式：
1. 客户端模式：主动连接 ISUP 驱动（默认）
2. 独立模式：即使没有驱动，也正常运行，等待连接
"""

import socket
import struct
import threading
import json
import time
import base64
import cv2
import numpy as np
import os
import sys
import random
from datetime import datetime
from typing import Dict, Any, Optional

# ========== ISUP 协议常量 ==========
ISUP_MAGIC = b'ISUP'
ISUP_VERSION = 1
DEFAULT_PORT = 7660

# ========== 配置信息 ==========
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 查找 video.mp4
VIDEO_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT_DIR))),
    "testMQTT", "video.mp4"
)
if not os.path.exists(VIDEO_FILE):
    VIDEO_FILE = os.path.join(SCRIPT_DIR, "video.mp4")

video_available = os.path.exists(VIDEO_FILE)
if video_available:
    print(f"✅ 找到视频文件: {VIDEO_FILE}")
else:
    print(f"⚠️ 视频文件不存在: {VIDEO_FILE}，将使用测试图案")

# ========== 模拟设备信息 ==========
DEVICE_INFO = {
    'device_serial': 'ISUP-SIM-001',
    'device_name': '模拟4G摄像头',
    'model': 'DS-2DE4A425IW-DE',
    'manufacturer': 'Hikvision',
    'firmware_version': 'V5.5.0',
    'hardware_version': 'V1.0',
    'channel_count': 2,
    'mac': '00:11:22:33:44:55',
    'ptz_support': True
}

# 模拟通道状态
CHANNELS = [
    {'id': 1, 'name': 'Camera 01', 'status': 'online'},
    {'id': 2, 'name': 'Camera 02', 'status': 'online'}
]

# 模拟 PTZ 状态
PTZ_STATUS = {
    'pan': 0,
    'tilt': 0,
    'zoom': 1,
    'focus': 50
}

# 全局视频捕获对象
video_cap = None
cap_lock = threading.Lock()


class ISUPDeviceSimulator:
    """ISUP 设备模拟器 - 主动连接驱动，但即使连接失败也继续运行"""

    def __init__(self,
                 device_serial: str = "ISUP-SIM-001",
                 device_name: str = "模拟4G摄像头",
                 driver_host: str = "127.0.0.1",
                 driver_port: int = DEFAULT_PORT,
                 auto_connect: bool = True,
                 debug: bool = True):
        """
        初始化 ISUP 设备模拟器

        Args:
            device_serial: 设备序列号（唯一标识）
            device_name: 设备名称
            driver_host: ISUP 驱动服务端地址
            driver_port: ISUP 驱动服务端端口
            auto_connect: 是否自动连接驱动
            debug: 是否打印调试信息
        """
        self.device_serial = device_serial
        self.device_name = device_name
        self.driver_host = driver_host
        self.driver_port = driver_port
        self.auto_connect = auto_connect
        self.debug = debug

        # 连接状态
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.running = False
        self.sequence = 0

        # 视频流
        self.video_thread: Optional[threading.Thread] = None
        self.video_running = False
        self.frame_count = 0
        self.fps = 10

        # 心跳
        self.heartbeat_thread: Optional[threading.Thread] = None
        self.heartbeat_running = False

        # 接收线程
        self.receive_thread: Optional[threading.Thread] = None

        # 报警线程
        self.alarm_thread: Optional[threading.Thread] = None
        self.alarm_running = False

        # 重连线程
        self.reconnect_thread: Optional[threading.Thread] = None
        self.reconnect_running = False

        # 锁
        self._lock = threading.Lock()

    # ==================== 连接管理 ====================

    def connect(self) -> bool:
        """主动连接到 ISUP 驱动服务端"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect((self.driver_host, self.driver_port))
            self.connected = True

            print(f"✅ 已连接到 ISUP 驱动: {self.driver_host}:{self.driver_port}")

            # 发送注册请求
            self._send_register()

            # 启动心跳
            self._start_heartbeat()

            # 启动接收线程
            self._start_receive_thread()

            return True

        except ConnectionRefusedError:
            print(f"⚠️ ISUP 驱动未启动 (端口 {self.driver_port})")
            print(f"   模拟器将在独立模式下运行，等待驱动启动...")
            print(f"   驱动启动后会自动连接")
            self.connected = False
            return False
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """断开连接"""
        self.connected = False
        self.heartbeat_running = False
        self.reconnect_running = False

        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None

    # ==================== 重连机制 ====================

    def _start_reconnect(self):
        """启动重连线程"""
        self.reconnect_running = True

        def reconnect_loop():
            while self.running and self.reconnect_running:
                if not self.connected:
                    print(f"🔄 尝试重新连接 ISUP 驱动...")
                    if self.connect():
                        print("✅ 重新连接成功，继续上报视频流")
                    else:
                        time.sleep(10)
                else:
                    time.sleep(5)

        self.reconnect_thread = threading.Thread(target=reconnect_loop, daemon=True)
        self.reconnect_thread.start()

    # ==================== 协议包 ====================

    def _build_packet(self, command: int, device_serial: str, body: bytes = b'') -> bytes:
        """构建 ISUP 协议包"""
        self.sequence = (self.sequence + 1) % 65535

        device_bytes = device_serial.encode('utf-8')
        device_len = len(device_bytes)

        header = (
                ISUP_MAGIC +
                struct.pack('>H', ISUP_VERSION) +
                struct.pack('>H', command) +
                struct.pack('>H', self.sequence) +
                struct.pack('B', device_len) +
                device_bytes +
                struct.pack('>H', 0) +
                struct.pack('>I', len(body))
        )
        return header + body

    def _send_packet(self, command: int, device_serial: str, body: bytes = b'') -> bool:
        """发送协议包"""
        if not self.connected or not self.socket:
            return False

        try:
            packet = self._build_packet(command, device_serial, body)
            self.socket.send(packet)
            return True
        except Exception as e:
            print(f"❌ 发送失败: {e}")
            self.connected = False
            return False

    def _send_register(self):
        """发送注册请求"""
        register_data = {
            "device_id": self.device_serial,
            "device_name": self.device_name,
            "model": DEVICE_INFO["model"],
            "manufacturer": DEVICE_INFO["manufacturer"],
            "firmware_version": DEVICE_INFO["firmware_version"],
            "hardware_version": DEVICE_INFO["hardware_version"],
            "channel_count": DEVICE_INFO["channel_count"],
            "mac": DEVICE_INFO["mac"],
            "timestamp": datetime.now().isoformat()
        }
        body = json.dumps(register_data).encode('utf-8')

        # 🆕 打印注册数据
        if self.debug:
            print(f"📤 [发送] 注册数据: {json.dumps(register_data, ensure_ascii=False)[:200]}...")

        self._send_packet(0x0001, self.device_serial, body)
        print(f"📝 注册请求已发送: {self.device_serial}")

    # ==================== 心跳 ====================

    def _start_heartbeat(self):
        """启动心跳"""
        self.heartbeat_running = True

        def heartbeat_loop():
            count = 0
            while self.heartbeat_running and self.running:
                time.sleep(30)
                if not self.heartbeat_running:
                    break
                self._send_packet(0x0003, self.device_serial, b'')
                count += 1
                if count % 10 == 0:
                    status = "已连接" if self.connected else "未连接"
                    print(f"💓 心跳 #{count} ({status})")

        self.heartbeat_thread = threading.Thread(target=heartbeat_loop, daemon=True)
        self.heartbeat_thread.start()

    # ==================== 接收命令 ====================

    def _start_receive_thread(self):
        """启动接收线程"""

        def receive_loop():
            while self.running and self.connected:
                try:
                    self.socket.settimeout(5)
                    data = self.socket.recv(8192)
                    if not data:
                        break
                    self._parse_and_handle(data)
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"❌ 接收异常: {e}")
                    self.connected = False
                    break

        self.receive_thread = threading.Thread(target=receive_loop, daemon=True)
        self.receive_thread.start()

    def _parse_and_handle(self, data: bytes):
        """解析并处理接收到的数据"""
        if len(data) < 20:
            return

        if data[0:4] != ISUP_MAGIC:
            return

        try:
            command = struct.unpack('>H', data[6:8])[0]
            device_id_len = data[10]
            device_serial = data[11:11 + device_id_len].decode('utf-8', errors='ignore') if device_id_len > 0 else ''
            offset = 11 + device_id_len
            body_len = struct.unpack('>I', data[offset + 2:offset + 6])[0]
            body = data[offset + 6:offset + 6 + body_len] if body_len > 0 else b''

            payload = {}
            if body_len > 0:
                try:
                    payload = json.loads(body.decode('utf-8'))
                except:
                    payload = {'raw': body.hex()}

            if command == 0x0008:  # 控制命令
                self._handle_control(payload)
            elif command == 0x8001:  # 注册响应
                print(f"✅ 注册成功: {payload.get('status', 'ok')}")
            elif command == 0x8003:  # 心跳响应
                pass

        except Exception as e:
            print(f"⚠️ 解析数据包失败: {e}")

    def _handle_control(self, payload: Dict):
        """处理控制命令"""
        method = payload.get('method', '')
        params = payload.get('params', {})

        print(f"🎮 收到控制命令: {method} {params}")

        if method == 'ptz':
            self._handle_ptz(params)
        elif method == 'get_status':
            self._send_status_response()
        elif method == 'reboot':
            print("🔄 设备重启中...")
            threading.Thread(target=self._handle_reboot, daemon=True).start()
        else:
            print(f"⚠️ 未知命令: {method}")

        self._send_command_response(method, "success")

    def _handle_ptz(self, params: Dict):
        """处理 PTZ 控制"""
        action = params.get('action', '')
        speed = params.get('speed', 0.5)

        if action == 'up':
            PTZ_STATUS['tilt'] = min(90, PTZ_STATUS['tilt'] + int(5 * speed))
            print(f"  ↑ 向上转动, 当前角度: {PTZ_STATUS['tilt']}°")
        elif action == 'down':
            PTZ_STATUS['tilt'] = max(-90, PTZ_STATUS['tilt'] - int(5 * speed))
            print(f"  ↓ 向下转动, 当前角度: {PTZ_STATUS['tilt']}°")
        elif action == 'left':
            PTZ_STATUS['pan'] = max(-360, PTZ_STATUS['pan'] - int(5 * speed))
            print(f"  ← 向左转动, 当前角度: {PTZ_STATUS['pan']}°")
        elif action == 'right':
            PTZ_STATUS['pan'] = min(360, PTZ_STATUS['pan'] + int(5 * speed))
            print(f"  → 向右转动, 当前角度: {PTZ_STATUS['pan']}°")
        elif action == 'zoom_in':
            PTZ_STATUS['zoom'] = min(20, PTZ_STATUS['zoom'] + 0.5 * speed)
            print(f"  🔍 放大, 当前变倍: {PTZ_STATUS['zoom']:.1f}x")
        elif action == 'zoom_out':
            PTZ_STATUS['zoom'] = max(1, PTZ_STATUS['zoom'] - 0.5 * speed)
            print(f"  🔍 缩小, 当前变倍: {PTZ_STATUS['zoom']:.1f}x")
        elif action == 'stop':
            print("  ■ 停止转动")

    def _send_status_response(self):
        """发送状态响应"""
        status_data = {
            "status": "online",
            "ptz": PTZ_STATUS,
            "channels": CHANNELS,
            "device_info": {
                "model": DEVICE_INFO["model"],
                "firmware": DEVICE_INFO["firmware_version"]
            },
            "timestamp": datetime.now().isoformat()
        }
        body = json.dumps(status_data).encode('utf-8')

        # 🆕 打印状态数据
        if self.debug:
            print(f"📤 [发送] 状态数据: {json.dumps(status_data, ensure_ascii=False)[:200]}...")

        self._send_packet(0x0006, self.device_serial, body)
        print("📊 状态已上报")

    def _send_command_response(self, command: str, result: str):
        """发送命令响应"""
        response_data = {
            "command": command,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        body = json.dumps(response_data).encode('utf-8')
        self._send_packet(0x8000 | 0x0008, self.device_serial, body)

    def _handle_reboot(self):
        """模拟重启"""
        time.sleep(2)
        print("🔄 设备已重启完成")
        self._send_register()

    # ==================== 视频流 ====================

    def get_video_frame(self):
        """获取视频帧（循环播放）"""
        global video_cap

        with cap_lock:
            if video_cap is None and video_available:
                video_cap = cv2.VideoCapture(VIDEO_FILE)

            if video_cap is not None and video_cap.isOpened():
                ret, frame = video_cap.read()
                if not ret:
                    video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, frame = video_cap.read()

                if ret:
                    height, width = frame.shape[:2]
                    if width > 640:
                        scale = 640 / width
                        new_width = int(width * scale)
                        new_height = int(height * scale)
                        frame = cv2.resize(frame, (new_width, new_height))
                    return frame

            # 测试图案
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            for i in range(480):
                color = int(100 + 100 * (i / 480))
                cv2.line(frame, (0, i), (640, i), (color, color, 100), 1)

            x = int(320 + 200 * np.sin(self.frame_count * 0.05))
            y = int(240 + 150 * np.cos(self.frame_count * 0.07))
            cv2.circle(frame, (x, y), 50, (0, 255, 255), -1)

            status = "✅ 已连接" if self.connected else "⏳ 等待连接..."
            cv2.putText(frame, f"ISUP Simulator - {self.device_serial}", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Status: {status}", (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0) if self.connected else (0, 255, 255), 2)
            cv2.putText(frame, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), (50, 150),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
            if not video_available:
                cv2.putText(frame, "⚠️ video.mp4 not found", (50, 430),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            return frame

    def _start_video_stream(self):
        """启动视频流上报"""
        self.video_running = True

        def video_loop():
            print(f"🎬 视频流已启动 (FPS: {self.fps})")
            print(f"   📡 状态: {'已连接到驱动' if self.connected else '等待连接...'}")
            print(f"   📡 数据流: 模拟器 -> {'ISUP驱动' if self.connected else '本地缓存'} -> SSE -> 前端")

            frame_interval = 1.0 / self.fps

            while self.video_running and self.running:
                start_time = time.time()

                try:
                    frame = self.get_video_frame()
                    if frame is None:
                        time.sleep(0.1)
                        continue

                    self.frame_count += 1

                    _, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
                    jpeg_base64 = base64.b64encode(jpeg).decode('utf-8')

                    video_data = {
                        "type": "video",
                        "format": "jpeg",
                        "image": jpeg_base64,
                        "width": frame.shape[1],
                        "height": frame.shape[0],
                        "frame_count": self.frame_count,
                        "timestamp": datetime.now().isoformat()
                    }

                    # ===== 🆕 打印完整数据 =====
                    if self.debug and self.frame_count % 10 == 0:
                        # 打印数据摘要（不打印完整base64，太长了）
                        print(f"📤 [发送] 视频帧 #{self.frame_count}:")
                        print(f"   type: {video_data['type']}")
                        print(f"   format: {video_data['format']}")
                        print(f"   width: {video_data['width']}, height: {video_data['height']}")
                        print(f"   image_size: {len(video_data['image'])} bytes")
                        print(f"   timestamp: {video_data['timestamp']}")
                        print(f"   --- 完整数据: {json.dumps(video_data, ensure_ascii=False)[:300]}...")

                    # ===== 打印更精简的日志 =====
                    if self.frame_count % 100 == 0:
                        status = "已连接" if self.connected else "等待连接"
                        print(f"🎬 已生成 {self.frame_count} 帧 ({status})")

                    # 只有连接成功时才发送
                    if self.connected:
                        self._send_packet(0x0005, self.device_serial,
                                          json.dumps(video_data).encode('utf-8'))
                    else:
                        if self.frame_count % 50 == 0:
                            print(f"⏳ 等待连接驱动... (已生成 {self.frame_count} 帧)")

                except Exception as e:
                    print(f"⚠️ 视频帧处理异常: {e}")
                    import traceback
                    if self.debug:
                        traceback.print_exc()

                elapsed = time.time() - start_time
                if elapsed < frame_interval:
                    time.sleep(frame_interval - elapsed)

        self.video_thread = threading.Thread(target=video_loop, daemon=True)
        self.video_thread.start()

    # ==================== 报警上报 ====================

    def _start_alarm_report(self):
        """启动报警上报"""
        self.alarm_running = True

        def alarm_loop():
            alarm_types = ['motiondetect', 'linedetection', 'regionenter']
            count = 0

            while self.alarm_running and self.running:
                time.sleep(30 + random.random() * 60)
                if not self.alarm_running:
                    break

                if self.connected and random.random() > 0.8:
                    alarm_type = random.choice(alarm_types)
                    alarm_data = {
                        "alarm_type": alarm_type,
                        "level": random.choice(["info", "warning", "critical"]),
                        "channel": random.choice([1, 2]),
                        "message": f"检测到{alarm_type}事件",
                        "timestamp": datetime.now().isoformat()
                    }

                    # 🆕 打印报警数据
                    if self.debug:
                        print(f"📤 [发送] 报警数据: {json.dumps(alarm_data, ensure_ascii=False)}")

                    body = json.dumps(alarm_data).encode('utf-8')
                    self._send_packet(0x0007, self.device_serial, body)
                    count += 1
                    print(f"🚨 报警 #{count}: {alarm_type} ({alarm_data['level']})")

        self.alarm_thread = threading.Thread(target=alarm_loop, daemon=True)
        self.alarm_thread.start()

    # ==================== 运行 ====================

    def run(self):
        """运行模拟器"""
        print("=" * 70)
        print("   📹 海康 ISUP 设备模拟器")
        print("=" * 70)
        print(f"设备序列号: {self.device_serial}")
        print(f"设备名称: {self.device_name}")
        print(f"设备型号: {DEVICE_INFO['model']}")
        print(f"驱动地址: {self.driver_host}:{self.driver_port}")
        print(f"视频文件: {VIDEO_FILE if video_available else '不存在(使用测试图案)'}")
        print(f"调试模式: {'✅ 开启' if self.debug else '❌ 关闭'}")
        print("=" * 70)
        print("📡 数据流:")
        print(f"   模拟器 -> ISUP驱动(端口{self.driver_port}) -> DeviceManager -> SSE -> 前端")
        print("=" * 70)
        print("\n💡 提示: 即使驱动未启动，模拟器也会正常运行")
        print("   一旦驱动启动，模拟器会自动连接并上报视频流")
        print("\n按 Ctrl+C 退出\n")

        self.running = True

        self.connect()

        if not self.connected:
            self._start_reconnect()

        self._start_video_stream()
        self._start_alarm_report()

        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 正在关闭模拟器...")
            self.running = False
            self.disconnect()
            cleanup()
            print("✅ 模拟器已关闭")


def cleanup():
    """清理资源"""
    global video_cap
    if video_cap:
        video_cap.release()


if __name__ == '__main__':
    import os
    import sys

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from _runtime_guard import require_simulator_enabled

    require_simulator_enabled("isup_simulator")
    import atexit

    atexit.register(cleanup)

    # 解析命令行参数
    device_serial = sys.argv[1] if len(sys.argv) > 1 else "ISUP-SIM-001"
    driver_host = sys.argv[2] if len(sys.argv) > 2 else "127.0.0.1"
    driver_port = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_PORT

    # 🆕 支持 --debug 参数
    debug = True
    if '--quiet' in sys.argv or '-q' in sys.argv:
        debug = False

    simulator = ISUPDeviceSimulator(
        device_serial=device_serial,
        device_name=f"模拟摄像头-{device_serial[-6:]}",
        driver_host=driver_host,
        driver_port=driver_port,
        debug=debug
    )

    simulator.run()