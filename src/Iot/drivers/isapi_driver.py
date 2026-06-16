# src/Iot/drivers/isapi_driver.py
"""
海康 ISAPI 协议驱动
用于局域网内设备管理、配置、控制和告警接收
支持视频流获取并通过 SSE 推送到前端
"""

import requests
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional
from datetime import datetime
import json
import threading
import time
import base64
import cv2
import numpy as np
from urllib.parse import urlparse

from src.Iot.drivers.base_driver import BaseProtocolDriver
from src.Iot.exceptions import ProtocolError
from src.api.iot.sse_api import push_to_device


class ISAPIDriver(BaseProtocolDriver):
    """海康 ISAPI 协议驱动"""

    def __init__(self):
        super().__init__("isapi")
        self.devices: Dict[str, Dict] = {}  # {device_did: {base_url, auth, ...}}
        self.session = requests.Session()
        self.video_threads: Dict[str, threading.Thread] = {}  # 视频推送线程
        self.video_running: Dict[str, bool] = {}  # 视频推送运行标志

    def connect(self, device_did: str, config: Dict[str, Any]) -> bool:
        """连接海康设备（验证 ISAPI 可用性）"""
        base_url = config.get('base_url')
        username = config.get('username', 'admin')
        password = config.get('password')

        if not base_url or not password:
            raise ProtocolError("缺少 base_url 或 password")

        device_code = config.get('device_code', 'unknown')

        # 保存设备信息
        self.devices[device_did] = {
            'base_url': base_url.rstrip('/'),
            'username': username,
            'password': password,
            'config': config,
            'device_code': device_code
        }

        print(f"[ISAPI] 设备（等待连接）【需要发起设备连接】")

        # 验证连接
        try:
            url = f"{base_url}/ISAPI/System/capabilities"
            response = self.session.get(url, auth=(username, password), timeout=5)

            if response.status_code == 200:
                self._on_status(device_did, 'online')
                # print(f"[ISAPI] ✅ 设备 {device_code} 连接成功")
                # print(f"[ISAPI]    状态: 在线")
                # 自动启动视频流推送
                self.start_video_push(device_did)
                return True
            else:
                # 设备在线但返回非200
                self._on_status(device_did, 'online')
                # print(f"[ISAPI] ✅ 设备 {device_code} 已响应 (状态码: {response.status_code})")
                return True

        except requests.exceptions.ConnectionError:
            # 设备未启动或网络不通
            self._on_status(device_did, 'offline')
            return True  # 返回 True，不阻塞设备管理器

        except requests.exceptions.Timeout:
            # 连接超时
            self._on_status(device_did, 'offline')
            return True

        except Exception as e:
            # 其他异常
            self._on_status(device_did, 'error')
            # print(f"[ISAPI] ⏳ 设备 {device_code} 等待连接")
            # print(f"[ISAPI]    地址: {base_url}")
            # print(f"[ISAPI]    状态: {str(e)}")
            # print(f"{'=' * 50}\n")
            return True
    # def connect(self, device_did: str, config: Dict[str, Any]) -> bool:
    #     """连接海康设备（验证 ISAPI 可用性）"""
    #     base_url = config.get('base_url')
    #     username = config.get('username', 'admin')
    #     password = config.get('password')
    #
    #     if not base_url or not password:
    #         raise ProtocolError("缺少 base_url 或 password")
    #
    #     self.devices[device_did] = {
    #         'base_url': base_url.rstrip('/'),
    #         'username': username,
    #         'password': password,
    #         'config': config,
    #         'device_code': config.get('device_code', 'unknown')
    #     }
    #
    #     # 验证连接
    #     try:
    #         url = f"{base_url}/ISAPI/System/capabilities"
    #         response = self.session.get(url, auth=(username, password), timeout=10)
    #         if response.status_code == 200:
    #             self._on_status(device_did, 'online')
    #             print(f"[ISAPI] 设备 {device_did} 连接成功")
    #
    #             # 自动启动视频流推送
    #             self.start_video_push(device_did)
    #             return True
    #         else:
    #             print(f"[ISAPI] 设备（等待连接）")
    #             raise ProtocolError(f"ISAPI 验证失败: {response.status_code}")
    #     except Exception as e:
    #         raise ProtocolError(f"[ISAPI] 协议启动成功，等待设备接入")

    def disconnect(self, device_did: str) -> bool:
        """断开连接"""
        # 停止视频推送
        self.stop_video_push(device_did)

        if device_did in self.devices:
            del self.devices[device_did]
            self._on_status(device_did, 'offline')
        return True

    def _request(self, device_did: str, method: str, endpoint: str, data: Any = None) -> Dict:
        """发送 ISAPI 请求"""
        device = self.devices.get(device_did)
        if not device:
            raise ProtocolError(f"设备未连接: {device_did}")

        url = f"{device['base_url']}/{endpoint.lstrip('/')}"
        auth = (device['username'], device['password'])

        try:
            if method == 'GET':
                response = self.session.get(url, auth=auth, timeout=10)
            elif method == 'POST':
                response = self.session.post(url, data=data, auth=auth, timeout=10)
            elif method == 'PUT':
                response = self.session.put(url, data=data, auth=auth, timeout=10)
            else:
                response = self.session.delete(url, auth=auth, timeout=10)

            return {
                'success': 200 <= response.status_code < 300,
                'status_code': response.status_code,
                'data': response.text
            }
        except Exception as e:
            raise ProtocolError(f"ISAPI 请求失败: {e}")

    def get_video_stream_url(self, device_did: str, channel: int = 1) -> Optional[str]:
        """获取设备的视频流地址"""
        device = self.devices.get(device_did)
        if not device:
            return None

        # 尝试从通道状态接口获取 MJPEG 地址
        try:
            result = self._request(device_did, 'GET', '/ISAPI/ContentMgmt/InputProxy/channels/status')
            if result.get('success') and result.get('data'):
                # 解析 XML 获取 MJPEG 地址
                import re
                # 查找 mjpegUrl
                match = re.search(r'<mjpegUrl>(.*?)</mjpegUrl>', result['data'])
                if match:
                    return match.group(1)
        except:
            pass

        # 返回默认的 MJPEG 地址
        base_url = device['base_url']
        return f"{base_url}/mjpeg"

    def start_video_push(self, device_did: str):
        """启动视频流 SSE 推送"""
        device = self.devices.get(device_did)
        if not device:
            # print(f"[ISAPI] 设备未连接，无法启动视频推送: {device_did}")
            return

        device_code = device.get('device_code', 'unknown')

        # 如果已经在推送，先停止
        self.stop_video_push(device_did)

        # 获取视频流地址
        video_url = self.get_video_stream_url(device_did)
        if not video_url:
            print(f"[ISAPI] 无法获取视频流地址: {device_did}")
            return

        # print(f"[ISAPI] 启动视频推送: {device_code}, 视频源: {video_url}")

        self.video_running[device_did] = True

        def video_push_loop():
            """视频推送循环"""
            device_code_local = device.get('device_code', 'unknown')
            cap = None
            frame_count = 0

            while self.video_running.get(device_did, False):
                try:
                    # 尝试从 MJPEG 流读取
                    if video_url.endswith('.mjpeg') or 'mjpeg' in video_url:
                        self._push_mjpeg_stream(device_did, device_code_local, video_url)
                        break
                    else:
                        # 使用 OpenCV 读取视频流
                        if cap is None or not cap.isOpened():
                            cap = cv2.VideoCapture(video_url)
                            if not cap.isOpened():
                                print(f"[ISAPI] 无法打开视频流: {video_url}")
                                time.sleep(5)
                                continue
                            print(f"[ISAPI] 视频流已连接: {device_code_local}")

                        ret, frame = cap.read()
                        if not ret:
                            # 重新连接
                            cap.release()
                            cap = None
                            time.sleep(2)
                            continue

                        frame_count += 1

                        # 缩放帧（减小传输大小）
                        height, width = frame.shape[:2]
                        if width > 640:
                            scale = 640 / width
                            new_width = int(width * scale)
                            new_height = int(height * scale)
                            frame = cv2.resize(frame, (new_width, new_height))

                        # 转换为 JPEG 并 base64 编码
                        _, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
                        jpeg_base64 = base64.b64encode(jpeg).decode('utf-8')

                        # 通过 SSE 推送
                        push_to_device(device_code_local, {
                            'type': 'video_frame',
                            'device_code': device_code_local,
                            'device_did': device_did,
                            'timestamp': datetime.now().isoformat(),
                            'frame_count': frame_count,
                            'image': jpeg_base64,
                            'width': new_width,
                            'height': new_height
                        })

                        # 控制帧率（约 10 fps）
                        time.sleep(0.1)

                except Exception as e:
                    print(f"[ISAPI] 视频推送异常: {e}")
                    time.sleep(2)

            # 清理
            if cap:
                cap.release()
            # print(f"[ISAPI] 视频推送已停止: {device_code_local}")

        # 启动推送线程
        thread = threading.Thread(target=video_push_loop, daemon=True)
        thread.start()
        self.video_threads[device_did] = thread
        # print(f"[ISAPI] 视频 SSE 推送已启动: {device_code}")

    def _push_mjpeg_stream(self, device_did: str, device_code: str, mjpeg_url: str):
        """从 MJPEG 流读取并推送"""
        try:
            response = requests.get(mjpeg_url, stream=True, timeout=30)
            bytes_data = b''
            frame_count = 0

            for chunk in response.iter_content(chunk_size=4096):
                if not self.video_running.get(device_did, False):
                    break

                if chunk:
                    bytes_data += chunk
                    a = bytes_data.find(b'\xff\xd8')  # JPEG 开始标记
                    b = bytes_data.find(b'\xff\xd9')  # JPEG 结束标记

                    if a != -1 and b != -1:
                        jpg = bytes_data[a:b + 2]
                        bytes_data = bytes_data[b + 2:]
                        frame_count += 1

                        jpg_base64 = base64.b64encode(jpg).decode('utf-8')

                        push_to_device(device_code, {
                            'type': 'video_frame',
                            'device_code': device_code,
                            'device_did': device_did,
                            'timestamp': datetime.now().isoformat(),
                            'frame_count': frame_count,
                            'image': jpg_base64
                        })

                        time.sleep(0.05)  # 约 20 fps

        except Exception as e:
            print(f"[ISAPI] MJPEG 流读取失败: {e}")

    def stop_video_push(self, device_did: str):
        """停止视频流推送"""
        self.video_running[device_did] = False
        if device_did in self.video_threads:
            self.video_threads[device_did].join(timeout=2)
            del self.video_threads[device_did]
        if device_did in self.video_running:
            del self.video_running[device_did]

    def get_capabilities(self, device_did: str) -> Dict:
        """获取设备能力集"""
        return self._request(device_did, 'GET', '/ISAPI/System/capabilities')

    def get_channels(self, device_did: str) -> list:
        """获取视频通道列表"""
        result = self._request(device_did, 'GET', '/ISAPI/ContentMgmt/InputProxy/channels/status')
        return self._parse_channels_xml(result.get('data', ''))

    def _parse_channels_xml(self, xml_data: str) -> list:
        """解析通道 XML"""
        channels = []
        try:
            root = ET.fromstring(xml_data)
            for channel_elem in root.findall('.//Channel'):
                channel = {
                    'id': int(channel_elem.findtext('id', 0)),
                    'name': channel_elem.findtext('name', ''),
                    'status': channel_elem.findtext('status', ''),
                    'resolution': channel_elem.findtext('resolution', '')
                }
                # 获取视频流地址
                mjpeg_url = channel_elem.findtext('mjpegUrl', '')
                if mjpeg_url:
                    channel['mjpeg_url'] = mjpeg_url
                rtsp_url = channel_elem.findtext('rtspUrl', '')
                if rtsp_url:
                    channel['rtsp_url'] = rtsp_url
                channels.append(channel)
        except Exception as e:
            print(f"[ISAPI] 解析通道 XML 失败: {e}")
        return channels

    def get_rtsp_url(self, device_did: str, channel: int = 1, stream: int = 0) -> str:
        """获取 RTSP 取流地址"""
        device = self.devices.get(device_did)
        if not device:
            raise ProtocolError(f"设备未连接: {device_did}")

        username = device['username']
        password = device['password']
        host = device['base_url'].replace('http://', '').replace('https://', '')
        host = host.split(':')[0]  # 去掉端口

        stream_suffix = 101 + (channel - 1) * 2 + stream
        return f"rtsp://{username}:{password}@{host}:554/Streaming/Channels/{stream_suffix}"

    def ptz_control(self, device_did: str, channel: int, action: str, speed: float = 0.5) -> Dict:
        """PTZ 云台控制"""
        # 映射 action
        action_map = {
            'up': 'up', 'down': 'down', 'left': 'left', 'right': 'right',
            'up_left': 'upLeft', 'up_right': 'upRight',
            'down_left': 'downLeft', 'down_right': 'downRight',
            'stop': 'stop', 'zoom_in': 'zoomIn', 'zoom_out': 'zoomOut'
        }
        mapped_action = action_map.get(action, action)

        xml_body = f'''<?xml version="1.0" encoding="UTF-8"?>
        <PTZData version="2.0" xmlns="http://www.isapi.org/ver20/XMLSchema">
            <panTilt>{mapped_action}</panTilt>
            <panTiltSpeed>{speed}</panTiltSpeed>
        </PTZData>'''

        endpoint = f"/ISAPI/PTZCtrl/channels/{channel}/continuous"
        return self._request(device_did, 'PUT', endpoint, xml_body)

    def get_alarm_info(self, device_did: str) -> Dict:
        """获取报警信息"""
        return self._request(device_did, 'GET', '/ISAPI/Event/notification/alertStream')

    def send_command(self, device_did: str, command: Dict[str, Any]) -> Dict[str, Any]:
        """下发命令"""
        method = command.get('method')
        params = command.get('params', {})

        if method == 'ptz':
            return self.ptz_control(
                device_did,
                params.get('channel', 1),
                params.get('action'),
                params.get('speed', 0.5)
            )
        elif method == 'get_rtsp_url':
            return {
                'success': True,
                'rtsp_url': self.get_rtsp_url(
                    device_did,
                    params.get('channel', 1),
                    params.get('stream', 0)
                )
            }
        elif method == 'get_channels':
            return {'success': True, 'channels': self.get_channels(device_did)}
        elif method == 'start_video':
            self.start_video_push(device_did)
            return {'success': True, 'message': '视频推送已启动'}
        elif method == 'stop_video':
            self.stop_video_push(device_did)
            return {'success': True, 'message': '视频推送已停止'}
        else:
            raise ProtocolError(f"未知命令: {method}")

    def subscribe(self, device_did: str, topics: Optional[list] = None):
        """订阅报警（启动轮询）"""

        def poll_alarm():
            while device_did in self.devices:
                try:
                    result = self.get_alarm_info(device_did)
                    if result.get('success') and result.get('data'):
                        # 解析报警数据
                        self._on_data(device_did, {
                            'type': 'alarm',
                            'payload': result['data'],
                            'timestamp': datetime.now().isoformat()
                        })
                except Exception as e:
                    print(f"[ISAPI] 轮询报警失败: {e}")
                time.sleep(2)

        thread = threading.Thread(target=poll_alarm, daemon=True)
        thread.start()