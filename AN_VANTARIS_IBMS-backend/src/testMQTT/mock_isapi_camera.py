#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
海康 ISAPI 摄像头模拟器
支持将 video.mp4 转换为 MJPEG 视频流（不需要 ffmpeg）
"""

from flask import Flask, Response, jsonify, request
import xml.etree.ElementTree as ET
from datetime import datetime
import random
import threading
import time
import os
import cv2
import numpy as np

app = Flask(__name__)

# ========== 配置信息 ==========
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEO_FILE = os.path.join(SCRIPT_DIR, "video.mp4")
MJPEG_PORT = 5002

# 检查视频文件
video_available = os.path.exists(VIDEO_FILE)
if video_available:
    print(f"✅ 找到视频文件: {VIDEO_FILE}")
else:
    print(f"⚠️ 视频文件不存在: {VIDEO_FILE}，将使用测试图案")

# ========== 模拟设备信息 ==========
DEVICE_INFO = {
    'device_id': 'MOCK-HIKVISION-001',
    'model': 'DS-2CD2T25F-I5',
    'firmware': 'V5.5.0',
    'serial_no': '20241010AAC123456789',
    'channels': 2,
    'ptz_support': True,
    'alarm_inputs': 4,
    'alarm_outputs': 2
}

# 模拟通道状态
CHANNELS = [
    {'id': 1, 'name': 'Camera 01', 'status': 'on', 'resolution': '1920x1080',
     'mjpeg_url': f'http://localhost:{MJPEG_PORT}/mjpeg'},
    {'id': 2, 'name': 'Camera 02', 'status': 'on', 'resolution': '1280x720',
     'mjpeg_url': f'http://localhost:{MJPEG_PORT}/mjpeg'}
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


def get_video_frame():
    """获取视频帧（循环播放）"""
    global video_cap

    with cap_lock:
        if video_cap is None and video_available:
            video_cap = cv2.VideoCapture(VIDEO_FILE)

        if video_cap is not None and video_cap.isOpened():
            ret, frame = video_cap.read()
            if not ret:
                # 循环播放
                video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = video_cap.read()

            if ret:
                # 缩放
                height, width = frame.shape[:2]
                if width > 640:
                    scale = 640 / width
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    frame = cv2.resize(frame, (new_width, new_height))
                return frame

        # 生成测试图案
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(frame, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        return frame


def generate_mjpeg_frames():
    """生成 MJPEG 帧"""
    fps = 10  # 10帧/秒
    frame_interval = 1.0 / fps

    while True:
        frame = get_video_frame()
        ret, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
        time.sleep(frame_interval)


def start_mjpeg_server():
    """启动 MJPEG 服务器（独立线程）"""

    def run_mjpeg():
        mjpeg_app = Flask(__name__)

        @mjpeg_app.route('/mjpeg')
        def mjpeg_feed():
            return Response(generate_mjpeg_frames(),
                            mimetype='multipart/x-mixed-replace; boundary=frame')

        @mjpeg_app.route('/')
        def index():
            return '''
            <html>
            <body>
                <h1>ISAPI Camera Simulator</h1>
                <img src="/mjpeg" width="640" height="480">
            </body>
            </html>
            '''

        mjpeg_app.run(host='0.0.0.0', port=MJPEG_PORT, debug=False, threaded=True)

    thread = threading.Thread(target=run_mjpeg, daemon=True)
    thread.start()
    print(f"🎬 MJPEG 流已启动: http://localhost:{MJPEG_PORT}/mjpeg")


# ========== ISAPI 接口 ==========
@app.route('/ISAPI/System/capabilities', methods=['GET'])
def get_capabilities():
    """获取设备能力集"""
    xml_response = f'''<?xml version="1.0" encoding="UTF-8"?>
    <DeviceCap version="2.0" xmlns="http://www.isapi.org/ver20/XMLSchema">
        <deviceName>Mock Camera</deviceName>
        <model>{DEVICE_INFO['model']}</model>
        <firmwareVersion>{DEVICE_INFO['firmware']}</firmwareVersion>
        <serialNumber>{DEVICE_INFO['serial_no']}</serialNumber>
        <channelNum>{DEVICE_INFO['channels']}</channelNum>
        <ptzSupport>{str(DEVICE_INFO['ptz_support']).lower()}</ptzSupport>
        <alarmInNum>{DEVICE_INFO['alarm_inputs']}</alarmInNum>
        <alarmOutNum>{DEVICE_INFO['alarm_outputs']}</alarmOutNum>
    </DeviceCap>'''
    return Response(xml_response, mimetype='application/xml')


@app.route('/ISAPI/System/deviceInfo', methods=['GET'])
def get_device_info():
    """获取设备基本信息"""
    xml_response = f'''<?xml version="1.0" encoding="UTF-8"?>
    <DeviceInfo version="2.0" xmlns="http://www.isapi.org/ver20/XMLSchema">
        <deviceName>Mock Camera</deviceName>
        <deviceID>{DEVICE_INFO['device_id']}</deviceID>
        <deviceDescription>Mock ISAPI Camera Simulator</deviceDescription>
        <model>{DEVICE_INFO['model']}</model>
        <serialNumber>{DEVICE_INFO['serial_no']}</serialNumber>
        <macAddress>00:11:22:33:44:55</macAddress>
        <firmwareVersion>{DEVICE_INFO['firmware']}</firmwareVersion>
        <firmwareReleasedDate>2024-01-01</firmwareReleasedDate>
        <bootTime>{datetime.now().isoformat()}</bootTime>
    </DeviceInfo>'''
    return Response(xml_response, mimetype='application/xml')


@app.route('/ISAPI/ContentMgmt/InputProxy/channels/status', methods=['GET'])
def get_channels_status():
    """获取通道状态（包含视频流地址）"""
    xml_channels = []
    for ch in CHANNELS:
        xml_channels.append(f'''
        <Channel>
            <id>{ch['id']}</id>
            <name>{ch['name']}</name>
            <status>{ch['status']}</status>
            <resolution>{ch['resolution']}</resolution>
            <mjpegUrl>{ch['mjpeg_url']}</mjpegUrl>
        </Channel>''')

    xml_response = f'''<?xml version="1.0" encoding="UTF-8"?>
    <ChannelList version="2.0" xmlns="http://www.isapi.org/ver20/XMLSchema">
        {''.join(xml_channels)}
    </ChannelList>'''
    return Response(xml_response, mimetype='application/xml')


@app.route('/ISAPI/Streaming/channels/<path:channel_id>', methods=['GET'])
def get_stream_info(channel_id):
    """获取流信息"""
    ch = CHANNELS[0] if channel_id.startswith('101') else CHANNELS[1]
    xml_response = f'''<?xml version="1.0" encoding="UTF-8"?>
    <StreamingChannel version="2.0" xmlns="http://www.isapi.org/ver20/XMLSchema">
        <id>{channel_id}</id>
        <channelName>{ch['name']}</channelName>
        <enabled>true</enabled>
        <Video>
            <enabled>true</enabled>
            <videoCodecType>H.264</videoCodecType>
            <videoResolutionWidth>1920</videoResolutionWidth>
            <videoResolutionHeight>1080</videoResolutionHeight>
        </Video>
        <mjpegUrl>{ch['mjpeg_url']}</mjpegUrl>
    </StreamingChannel>'''
    return Response(xml_response, mimetype='application/xml')


@app.route('/ISAPI/PTZCtrl/channels/<int:channel>/continuous', methods=['PUT'])
def ptz_continuous(channel):
    """PTZ 连续控制"""
    try:
        xml_data = request.data.decode('utf-8')
        print(f"[PTZ] 收到控制命令 - 通道{channel}")

        if 'panTilt>up<' in xml_data:
            PTZ_STATUS['tilt'] = min(90, PTZ_STATUS['tilt'] + 5)
            print(f"  ↑ 向上转动, 当前角度: {PTZ_STATUS['tilt']}°")
        elif 'panTilt>down<' in xml_data:
            PTZ_STATUS['tilt'] = max(-90, PTZ_STATUS['tilt'] - 5)
            print(f"  ↓ 向下转动, 当前角度: {PTZ_STATUS['tilt']}°")
        elif 'panTilt>left<' in xml_data:
            PTZ_STATUS['pan'] = max(-360, PTZ_STATUS['pan'] - 5)
            print(f"  ← 向左转动, 当前角度: {PTZ_STATUS['pan']}°")
        elif 'panTilt>right<' in xml_data:
            PTZ_STATUS['pan'] = min(360, PTZ_STATUS['pan'] + 5)
            print(f"  → 向右转动, 当前角度: {PTZ_STATUS['pan']}°")
        elif 'zoom>in<' in xml_data:
            PTZ_STATUS['zoom'] = min(20, PTZ_STATUS['zoom'] + 0.5)
            print(f"  🔍 放大, 当前变倍: {PTZ_STATUS['zoom']}x")
        elif 'zoom>out<' in xml_data:
            PTZ_STATUS['zoom'] = max(1, PTZ_STATUS['zoom'] - 0.5)
            print(f"  🔍 缩小, 当前变倍: {PTZ_STATUS['zoom']}x")
        elif 'panTilt>stop<' in xml_data:
            print("  ■ 停止转动")

        return Response('''<?xml version="1.0" encoding="UTF-8"?><Response status="200" />''',
                        mimetype='application/xml')
    except Exception as e:
        print(f"[PTZ] 控制失败: {e}")
        return Response('''<?xml version="1.0" encoding="UTF-8"?><Response status="400" />''',
                        mimetype='application/xml', status=400)


@app.route('/ISAPI/PTZCtrl/channels/<int:channel>/presets', methods=['GET'])
def get_presets(channel):
    """获取预置位列表"""
    xml_response = f'''<?xml version="1.0" encoding="UTF-8"?>
    <PresetList version="2.0" xmlns="http://www.isapi.org/ver20/XMLSchema">
        <Preset>
            <id>1</id>
            <presetName>Preset 1 - Entrance</presetName>
        </Preset>
        <Preset>
            <id>2</id>
            <presetName>Preset 2 - Gate</presetName>
        </Preset>
        <Preset>
            <id>3</id>
            <presetName>Preset 3 - Parking</presetName>
        </Preset>
    </PresetList>'''
    return Response(xml_response, mimetype='application/xml')


@app.route('/ISAPI/Event/notification/alertStream', methods=['GET'])
def get_alert_stream():
    """获取报警流"""
    if random.random() > 0.95:
        event_types = ['motiondetect', 'linedetection', 'regionenter']
        event_type = random.choice(event_types)
        xml_response = f'''<?xml version="1.0" encoding="UTF-8"?>
        <EventList>
            <Event>
                <eventType>{event_type}</eventType>
                <eventTime>{datetime.now().isoformat()}</eventTime>
                <channelID>1</channelID>
                <eventState>active</eventState>
            </Event>
        </EventList>'''
        print(f"[ALARM] 报警事件: {event_type}")
        return Response(xml_response, mimetype='application/xml')

    return Response('''<?xml version="1.0" encoding="UTF-8"?><EventList />''',
                    mimetype='application/xml')


@app.route('/ISAPI/Image/channels/<int:channel>/current', methods=['GET'])
def get_image_params(channel):
    """获取图像参数"""
    xml_response = f'''<?xml version="1.0" encoding="UTF-8"?>
    <Image version="2.0" xmlns="http://www.isapi.org/ver20/XMLSchema">
        <brightness>50</brightness>
        <contrast>50</contrast>
        <saturation>50</saturation>
        <sharpness>50</sharpness>
    </Image>'''
    return Response(xml_response, mimetype='application/xml')


@app.route('/ISAPI/System/reboot', methods=['PUT'])
def reboot_device():
    """重启设备"""
    print(f"[SYSTEM] 设备重启命令已接收")
    return Response('''<?xml version="1.0" encoding="UTF-8"?><Response status="200" />''',
                    mimetype='application/xml')


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "ok",
        "device": DEVICE_INFO['device_id'],
        "mjpeg_stream": f"http://localhost:{MJPEG_PORT}/mjpeg",
        "video_file": video_available
    })


@app.route('/snapshot', methods=['GET'])
def get_snapshot():
    """获取实时截图"""
    frame = get_video_frame()
    ret, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
    return Response(jpeg.tobytes(), mimetype='image/jpeg')


def print_banner():
    """打印启动横幅"""
    print("=" * 70)
    print("   📹 海康 ISAPI 摄像头模拟器 (纯 Python 实现，无需 ffmpeg)")
    print("=" * 70)
    print(f"设备ID: {DEVICE_INFO['device_id']}")
    print(f"设备型号: {DEVICE_INFO['model']}")
    print(f"视频文件: {VIDEO_FILE if video_available else '不存在(使用测试图案)'}")
    print("=" * 70)
    print("📡 视频流地址:")
    print(f"   MJPEG: http://localhost:{MJPEG_PORT}/mjpeg")
    print(f"   截图:  http://localhost/snapshot")
    print("=" * 70)
    print("📡 ISAPI 接口:")
    print(f"   GET  /ISAPI/System/capabilities")
    print(f"   GET  /ISAPI/ContentMgmt/InputProxy/channels/status")
    print(f"   PUT  /ISAPI/PTZCtrl/channels/1/continuous")
    print(f"   GET  /ISAPI/Event/notification/alertStream")
    print("=" * 70)
    print("\n按 Ctrl+C 退出\n")


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

    require_simulator_enabled("mock_isapi_camera")
    import atexit

    atexit.register(cleanup)

    # 启动 MJPEG 服务器
    start_mjpeg_server()

    print_banner()

    try:
        # 启动主 Flask 服务器（ISAPI 接口）
        app.run(host='0.0.0.0', port=80, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n\n🛑 正在关闭模拟器...")
        cleanup()
        print("✅ 模拟器已关闭")