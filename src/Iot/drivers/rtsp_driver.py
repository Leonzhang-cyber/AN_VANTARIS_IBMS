# src/Iot/drivers/rtsp_driver.py
"""
RTSP 数据流驱动 - 直接解析 RTP 包
"""

import os
import socket
import threading
import time
import json
import struct
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from src.Iot.drivers.base_driver import BaseProtocolDriver
from src.Iot.exceptions import ProtocolError
from src.api.iot.sse_api import push_to_device

logger = logging.getLogger(__name__)


class RTSPDriver(BaseProtocolDriver):
    """RTSP 数据流驱动 - 直接接收 RTP 包"""

    def __init__(self):
        super().__init__("rtsp")
        self.devices: Dict[str, Dict] = {}
        self.data_threads: Dict[str, threading.Thread] = {}
        self.data_running: Dict[str, bool] = {}
        self.sockets: Dict[str, socket.socket] = {}
        self.rtp_port = 5060  # RTP 接收端口

    def connect(self, device_did: str, config: Dict[str, Any]) -> bool:
        rtsp_url = config.get('rtsp_url')
        if not rtsp_url:
            raise ProtocolError("缺少 rtsp_url")

        device_code = config.get('device_code', device_did[:20])

        # print(f"\n{'=' * 50}")
        # print(f"[RTSP] 连接设备: {device_code}")
        # print(f"[RTSP] RTSP地址: {rtsp_url}")
        # print(f"{'=' * 50}")
        print(f"[RTSP] 设备（等待连接）")

        self.devices[device_did] = {
            'rtsp_url': rtsp_url,
            'config': config,
            'device_code': device_code,
            'status': 'connecting',
            'connected_at': None,
            'fps': config.get('fps', 2)
        }

        self._on_status(device_did, 'online')
        # print(f"[RTSP] ✅ 设备已注册")

        # 启动数据接收
        self.start_data_receive(device_did)

        # print(f"{'=' * 50}\n")
        return True

    def disconnect(self, device_did: str) -> bool:
        self.stop_data_receive(device_did)

        if device_did in self.sockets:
            try:
                self.sockets[device_did].close()
            except:
                pass
            del self.sockets[device_did]

        if device_did in self.devices:
            device_code = self.devices[device_did].get('device_code', 'unknown')
            del self.devices[device_did]
            self._on_status(device_did, 'offline')
            print(f"[RTSP] 设备 {device_code} 已断开")

        return True

    def start_data_receive(self, device_did: str):
        """启动 RTP 数据接收"""
        device = self.devices.get(device_did)
        if not device:
            return

        device_code = device.get('device_code', 'unknown')
        self.stop_data_receive(device_did)

        self.data_running[device_did] = True

        def data_receive_loop():
            """接收 RTP 数据循环"""
            # print(f"[RTSP] 📡 数据接收启动: {device_code} (端口: {self.rtp_port})")

            # 创建 UDP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('0.0.0.0', self.rtp_port))
            sock.settimeout(2)
            self.sockets[device_did] = sock

            data_count = 0

            while self.data_running.get(device_did, False):
                try:
                    data, addr = sock.recvfrom(65536)

                    if len(data) < 12:
                        continue

                    # 解析 RTP 头
                    # 前12字节是 RTP 头
                    rtp_header = data[:12]
                    payload = data[12:]

                    # 检查 RTP 版本 (应该是 2)
                    version = (rtp_header[0] >> 6) & 0x03
                    if version != 2:
                        continue

                    # 获取 PT (Payload Type)
                    pt = rtp_header[1] & 0x7F

                    # 如果是动态类型 (96) 或文本数据
                    if pt == 96:
                        try:
                            # 尝试解析 JSON 数据
                            json_str = payload.decode('utf-8')
                            sensor_data = json.loads(json_str)

                            data_count += 1

                            # 打印接收到的数据
                            print(f"[RTSP] 📊 收到数据 #{data_count}: {json.dumps(sensor_data, ensure_ascii=False)}")

                            # 推送到 DeviceManager
                            self._on_data(device_did, {
                                'type': 'sensor_data',
                                'payload': sensor_data,
                                'timestamp': datetime.now().isoformat()
                            })

                        except json.JSONDecodeError:
                            print(f"[RTSP] ⚠️ JSON 解析失败: {payload[:100]}")
                        except UnicodeDecodeError:
                            print(f"[RTSP] ⚠️ 不是文本数据: {len(payload)} 字节")

                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"[RTSP] ⚠️ 接收异常: {e}")
                    time.sleep(1)

            sock.close()
            print(f"[RTSP] 🛑 数据接收停止: {device_code}")

        thread = threading.Thread(target=data_receive_loop, daemon=True)
        thread.start()
        self.data_threads[device_did] = thread
        # print(f"[RTSP] ✅ 数据接收线程已启动: {device_code}")

    def stop_data_receive(self, device_did: str):
        """停止数据接收"""
        self.data_running[device_did] = False
        if device_did in self.data_threads:
            self.data_threads[device_did].join(timeout=2)
            del self.data_threads[device_did]
        if device_did in self.data_running:
            del self.data_running[device_did]

    def send_command(self, device_did: str, command: Dict[str, Any]) -> Dict[str, Any]:
        method = command.get('method')
        if method == 'start_data':
            self.start_data_receive(device_did)
            return {'success': True, 'message': '数据接收已启动'}
        elif method == 'stop_data':
            self.stop_data_receive(device_did)
            return {'success': True, 'message': '数据接收已停止'}
        else:
            raise ProtocolError(f"未知命令: {method}")

    def subscribe(self, device_did: str, topics: Optional[list] = None):
        pass

    def __del__(self):
        for device_did in list(self.data_running.keys()):
            self.stop_data_receive(device_did)
        for device_did in list(self.sockets.keys()):
            try:
                self.sockets[device_did].close()
            except:
                pass