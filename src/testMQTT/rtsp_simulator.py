#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RTSP 协议设备模拟器 - 传输文字数据版
通过 RTSP 协议传输设备数据（温度、湿度等传感器数据）
"""

import cv2
import numpy as np
import threading
import time
import socket
import os
import sys
import json
import random
from datetime import datetime
from typing import Dict, Optional
import socketserver
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import re

# ========== 配置信息 ==========
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEO_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT_DIR))),
    "testMQTT", "video.mp4"
)
if not os.path.exists(VIDEO_FILE):
    VIDEO_FILE = os.path.join(SCRIPT_DIR, "video.mp4")

video_available = os.path.exists(VIDEO_FILE)
print(f"[VIDEO] video_available: {video_available}, path: {VIDEO_FILE}")

# ========== 模拟设备信息 ==========
DEVICE_INFO = {
    'device_id': 'RTSP-SIM-001',
    'device_name': '模拟RTSP传感器',
    'model': 'DS-2CD2T25F-I5',
    'manufacturer': 'Hikvision',
    'firmware_version': 'V5.5.0',
    'serial_no': '20241010AAC123456789',
    'channels': 2,
    'ptz_support': True
}

# 全局变量
video_cap = None
cap_lock = threading.Lock()
frame_counter = 0
fps = 10

# RTP 目标地址（直接发送到驱动监听的端口）
RTP_TARGET_PORT = 5060
RTP_TARGET_ADDR = ('127.0.0.1', RTP_TARGET_PORT)


def get_video_frame():
    """获取视频帧（仅用于测试图案）"""
    global video_cap, frame_counter

    with cap_lock:
        if video_cap is None and video_available:
            print(f"[VIDEO] 打开视频文件: {VIDEO_FILE}")
            video_cap = cv2.VideoCapture(VIDEO_FILE)
            if video_cap.isOpened():
                print(f"[VIDEO] 视频文件打开成功")
                print(f"[VIDEO] FPS: {video_cap.get(cv2.CAP_PROP_FPS)}")
                print(f"[VIDEO] 帧数: {video_cap.get(cv2.CAP_PROP_FRAME_COUNT)}")
                print(f"[VIDEO] 分辨率: {int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
            else:
                print(f"[VIDEO] 视频文件打开失败")

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

        x = int(320 + 200 * np.sin(frame_counter * 0.05))
        y = int(240 + 150 * np.cos(frame_counter * 0.07))
        cv2.circle(frame, (x, y), 50, (0, 255, 255), -1)

        cv2.putText(frame, "RTSP Data Simulator", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(frame, f"Frame: {frame_counter}", (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
        cv2.putText(frame, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), (50, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)

        frame_counter += 1
        return frame


def generate_sensor_data():
    """生成模拟传感器数据"""
    return {
        "type": "sensor_data",
        "temperature": round(20 + random.random() * 15, 1),
        "humidity": round(40 + random.random() * 40, 1),
        "battery": round(80 + random.random() * 20, 1),
        "signal_strength": round(60 + random.random() * 35, 0),
        "status": random.choice(["online", "online", "online", "warning"]),
        "timestamp": datetime.now().isoformat()
    }


# ========== RTSP 协议模拟 ==========
class RTSPHandler(socketserver.BaseRequestHandler):
    """RTSP 协议处理器"""

    def handle(self):
        try:
            data = self.request.recv(4096).decode('utf-8')
            if not data:
                return

            lines = data.split('\r\n')
            if not lines:
                return

            request_line = lines[0].split(' ')
            if len(request_line) < 2:
                return

            method = request_line[0]
            url = request_line[1]

            cseq = "1"
            for line in lines:
                if line.startswith('CSeq:'):
                    cseq = line.split(':')[1].strip()
                    break

            print(f"[RTSP] {method} {url} CSeq:{cseq}")

            if method == 'OPTIONS':
                self._handle_options(cseq)
            elif method == 'DESCRIBE':
                self._handle_describe(cseq)
            elif method == 'SETUP':
                self._handle_setup(data, cseq)
            elif method == 'PLAY':
                self._handle_play(cseq)
            elif method == 'PAUSE':
                self._handle_pause(cseq)
            elif method == 'TEARDOWN':
                self._handle_teardown(cseq)
            else:
                self._send_response(405, 'Method Not Allowed', cseq)

        except Exception as e:
            print(f"[RTSP] 异常: {e}")

    def _send_response(self, status_code: int, status_text: str, cseq: str,
                       headers: Dict = None, body: str = ""):
        response = f"RTSP/1.0 {status_code} {status_text}\r\n"
        response += f"CSeq: {cseq}\r\n"

        if headers:
            for key, value in headers.items():
                response += f"{key}: {value}\r\n"

        if body:
            response += f"Content-Length: {len(body)}\r\n"
            response += "\r\n"
            response += body
        else:
            response += "\r\n"

        self.request.send(response.encode('utf-8'))
        print(f"[RTSP] 响应: {status_code} {status_text}")

    def _handle_options(self, cseq: str):
        headers = {
            'Public': 'OPTIONS, DESCRIBE, SETUP, PLAY, PAUSE, TEARDOWN'
        }
        self._send_response(200, 'OK', cseq, headers)

    def _handle_describe(self, cseq: str):
        # 使用动态载荷类型 96 用于数据
        sdp = f"""v=0
o=- {int(time.time())} {int(time.time())} IN IP4 127.0.0.1
s=RTSP Data Simulator
c=IN IP4 127.0.0.1
t=0 0
a=range:npt=0-
m=application 0 RTP/AVP 96
a=rtpmap:96 JSON/90000
a=control:track1
"""
        headers = {
            'Content-Type': 'application/sdp'
        }
        self._send_response(200, 'OK', cseq, headers, sdp)

    def _handle_setup(self, data: str, cseq: str):
        print(f"[RTP] SETUP 请求，使用目标端口: {RTP_TARGET_PORT}")

        headers = {
            'Transport': f'RTP/AVP;unicast;client_port={RTP_TARGET_PORT}-{RTP_TARGET_PORT+1};server_port={RTP_TARGET_PORT+2}-{RTP_TARGET_PORT+3}',
            'Session': '12345678'
        }
        self._send_response(200, 'OK', cseq, headers)

    def _handle_play(self, cseq: str):
        headers = {
            'Range': 'npt=0.000-',
            'RTP-Info': 'url=rtsp://127.0.0.1:8554/stream;seq=1;rtptime=0',
            'Session': '12345678'
        }
        self._send_response(200, 'OK', cseq, headers)

    def _handle_pause(self, cseq: str):
        self._send_response(200, 'OK', cseq)

    def _handle_teardown(self, cseq: str):
        self._send_response(200, 'OK', cseq)


# ========== RTP 数据流服务 ==========
# ========== RTP 数据流服务 ==========
class RTPStreamServer:
    def __init__(self):
        self.running = False
        self.socket = None
        self.frame_count = 0
        self.fps = 2  # 每秒2条数据

    def start(self):
        try:
            # 🆕 只需要创建 socket，不需要 bind
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.running = True
            print(f"[RTP] 数据服务启动")
            print(f"[RTP] 发送目标: {RTP_TARGET_ADDR[0]}:{RTP_TARGET_ADDR[1]}")

            thread = threading.Thread(target=self._send_loop, daemon=True)
            thread.start()
            return True
        except Exception as e:
            print(f"[RTP] 启动失败: {e}")
            return False

    def stop(self):
        self.running = False
        if self.socket:
            self.socket.close()
            self.socket = None
        print("[RTP] 数据服务停止")

    def _send_loop(self):
        print(f"[RTP] 数据发送循环启动, 频率: {self.fps}条/秒")
        print(f"[RTP] 直接发送到: {RTP_TARGET_ADDR[0]}:{RTP_TARGET_ADDR[1]}")

        frame_interval = 1.0 / self.fps

        while self.running:
            start_time = time.time()

            try:
                # 直接发送到目标地址
                client_addr = RTP_TARGET_ADDR

                # 生成传感器数据
                sensor_data = generate_sensor_data()
                data_bytes = json.dumps(sensor_data).encode('utf-8')

                self.frame_count += 1

                # 构建 RTP 包 (动态载荷类型 96)
                rtp_header = bytearray(12)
                rtp_header[0] = 0x80
                rtp_header[1] = 0x60  # PT=96
                rtp_header[2:4] = (self.frame_count & 0xFFFF).to_bytes(2, 'big')
                rtp_header[4:8] = (int(time.time() * 90000) & 0xFFFFFFFF).to_bytes(4, 'big')
                rtp_header[8:12] = (0x12345678 & 0xFFFFFFFF).to_bytes(4, 'big')

                packet = bytes(rtp_header) + data_bytes

                if self.socket and self.running:
                    self.socket.sendto(packet, client_addr)

                if self.frame_count % 10 == 0:
                    print(f"[RTP] 已发送 {self.frame_count} 条数据")
                    print(f"    📊 {json.dumps(sensor_data, ensure_ascii=False)}")

            except Exception as e:
                print(f"[RTP] 异常: {e}")
                time.sleep(1)

            elapsed = time.time() - start_time
            if elapsed < frame_interval:
                time.sleep(frame_interval - elapsed)


# ========== ISAPI HTTP 模拟 ==========
class ISAPIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path == '/ISAPI/System/capabilities':
            self._send_capabilities()
        elif self.path == '/ISAPI/System/deviceInfo':
            self._send_device_info()
        elif self.path == '/ISAPI/ContentMgmt/InputProxy/channels/status':
            self._send_channels_status()
        elif self.path == '/health':
            self._send_health()
        else:
            self.send_response(404)
            self.end_headers()

    def do_PUT(self):
        if self.path.startswith('/ISAPI/PTZCtrl/channels/'):
            self._handle_ptz()
        else:
            self.send_response(404)
            self.end_headers()

    def _send_xml_response(self, xml_data: str):
        self.send_response(200)
        self.send_header('Content-Type', 'application/xml')
        self.end_headers()
        self.wfile.write(xml_data.encode('utf-8'))

    def _send_capabilities(self):
        xml = f'''<?xml version="1.0" encoding="UTF-8"?>
        <DeviceCap version="2.0" xmlns="http://www.isapi.org/ver20/XMLSchema">
            <deviceName>RTSP Data Simulator</deviceName>
            <model>{DEVICE_INFO['model']}</model>
            <firmwareVersion>{DEVICE_INFO['firmware_version']}</firmwareVersion>
            <serialNumber>{DEVICE_INFO['serial_no']}</serialNumber>
            <channelNum>{DEVICE_INFO['channels']}</channelNum>
            <ptzSupport>{str(DEVICE_INFO['ptz_support']).lower()}</ptzSupport>
        </DeviceCap>'''
        self._send_xml_response(xml)

    def _send_device_info(self):
        xml = f'''<?xml version="1.0" encoding="UTF-8"?>
        <DeviceInfo version="2.0" xmlns="http://www.isapi.org/ver20/XMLSchema">
            <deviceName>RTSP Data Simulator</deviceName>
            <deviceID>{DEVICE_INFO['device_id']}</deviceID>
            <model>{DEVICE_INFO['model']}</model>
            <serialNumber>{DEVICE_INFO['serial_no']}</serialNumber>
            <firmwareVersion>{DEVICE_INFO['firmware_version']}</firmwareVersion>
        </DeviceInfo>'''
        self._send_xml_response(xml)

    def _send_channels_status(self):
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <ChannelList version="2.0" xmlns="http://www.isapi.org/ver20/XMLSchema">
            <Channel>
                <id>1</id>
                <name>Data Channel</name>
                <status>on</status>
                <resolution>data</resolution>
            </Channel>
        </ChannelList>'''
        self._send_xml_response(xml)

    def _send_health(self):
        import json
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            "status": "ok",
            "device": DEVICE_INFO['device_id'],
            "rtsp_url": "rtsp://127.0.0.1:8554/stream",
            "data_type": "sensor_data",
            "rtp_target_port": RTP_TARGET_PORT
        }).encode('utf-8'))

    def _handle_ptz(self):
        print("[PTZ] 控制")
        xml = '''<?xml version="1.0" encoding="UTF-8"?><Response status="200" />'''
        self._send_xml_response(xml)


def run_isapi_server(port: int = 80):
    try:
        server = HTTPServer(('0.0.0.0', port), ISAPIHandler)
        print(f"[ISAPI] HTTP 启动, 端口: {port}")
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        return server
    except Exception as e:
        print(f"[ISAPI] 启动失败: {e}")
        return None


def run_rtsp_server(port: int = 8554):
    try:
        server = socketserver.TCPServer(('0.0.0.0', port), RTSPHandler)
        print(f"[RTSP] RTSP 启动, 端口: {port}")
        print(f"[RTSP] RTSP 地址: rtsp://127.0.0.1:{port}/stream")
        print(f"[RTSP] 传输数据类型: JSON 传感器数据")
        print(f"[RTSP] RTP 目标端口: {RTP_TARGET_PORT}")
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        return server
    except Exception as e:
        print(f"[RTSP] 启动失败: {e}")
        return None


def print_banner():
    print("=" * 60)
    print("RTSP 数据设备模拟器")
    print("=" * 60)
    print(f"设备ID: {DEVICE_INFO['device_id']}")
    print(f"视频文件: {VIDEO_FILE if video_available else '不存在'}")
    print(f"RTSP地址: rtsp://127.0.0.1:8554/stream")
    print(f"数据类型: JSON 传感器数据")
    print(f"数据频率: 2条/秒")
    print(f"RTP发送端口: {RTP_TARGET_PORT}")
    print("=" * 60)
    print("按 Ctrl+C 退出")
    print("")


def cleanup():
    global video_cap
    print("\n关闭模拟器...")
    if video_cap:
        video_cap.release()
        video_cap = None
    if 'rtp_server' in globals() and rtp_server:
        rtp_server.stop()
    print("已关闭")


if __name__ == '__main__':
    import atexit

    atexit.register(cleanup)

    rtsp_server = run_rtsp_server(8554)

    rtp_server = RTPStreamServer()
    rtp_server.start()

    isapi_server = run_isapi_server(80)

    print_banner()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup()