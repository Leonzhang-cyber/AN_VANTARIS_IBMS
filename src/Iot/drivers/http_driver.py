# src/Iot/drivers/http_driver.py
"""
HTTP协议驱动 - 支持 HTTP/HTTPS 设备通信
"""

import requests
from typing import Dict, Any, Optional
from datetime import datetime
import json

from src.Iot.drivers.base_driver import BaseProtocolDriver
from src.Iot.exceptions import ProtocolError


class HTTPDriver(BaseProtocolDriver):
    """HTTP协议驱动 - 支持主动拉取和主动上报两种模式"""

    def __init__(self):
        super().__init__("http")
        self.device_endpoints: Dict[str, str] = {}  # {device_did: base_url}
        self.device_configs: Dict[str, Dict] = {}  # {device_did: config}
        self.session = requests.Session()

    def connect(self, device_did: str, config: Dict[str, Any]) -> bool:
        """
        连接HTTP设备
        支持两种模式：
        1. 主动拉取模式：需要提供 base_url，驱动会主动轮询设备
        2. 主动上报模式：不需要 base_url，设备主动 POST 数据到 /ingest/http
        """
        base_url = config.get('base_url', '')

        # 🆕 主动上报模式：没有 base_url，不需要主动连接
        if not base_url:
            self.device_endpoints[device_did] = ""
            self.device_configs[device_did] = config
            self._on_status(device_did, 'online')
            print(f"[HTTP] 设备 {device_did} 已就绪（主动上报模式）")
            return True

        # 主动拉取模式：验证连接
        verify_endpoint = config.get('verify_endpoint', '/health')
        timeout = config.get('timeout', 10)

        try:
            url = f"{base_url}{verify_endpoint}"
            response = self.session.get(url, timeout=timeout)
            if response.status_code < 500:
                self.device_endpoints[device_did] = base_url
                self.device_configs[device_did] = config
                self._on_status(device_did, 'online')
                print(f"[HTTP] 设备 {device_did} 连接成功（主动拉取模式）: {base_url}")
                return True
            else:
                raise ProtocolError(f"HTTP连接失败: {response.status_code}")
        except requests.RequestException as e:
            raise ProtocolError(f"HTTP连接失败: {str(e)}")

    def disconnect(self, device_did: str) -> bool:
        """断开设备连接"""
        if device_did in self.device_endpoints:
            del self.device_endpoints[device_did]
            del self.device_configs[device_did]
            self._on_status(device_did, 'offline')
            print(f"[HTTP] 设备 {device_did} 已断开")
        return True

    def send_command(self, device_did: str, command: Dict[str, Any]) -> Dict[str, Any]:
        """下发HTTP命令（仅主动拉取模式支持）"""
        base_url = self.device_endpoints.get(device_did)

        # 主动上报模式不支持命令下发
        if not base_url:
            raise ProtocolError(f"设备 {device_did} 为主动上报模式，不支持命令下发")

        config = self.device_configs.get(device_did, {})

        endpoint = command.get('endpoint', '/command')
        http_method = command.get('http_method', 'POST')
        params = command.get('params', {})
        headers = command.get('headers', {'Content-Type': 'application/json'})
        timeout = config.get('timeout', 10)

        url = f"{base_url}{endpoint}"

        print(f"[HTTP] 下发命令: method={http_method}, url={url}")

        try:
            if http_method.upper() == 'GET':
                response = self.session.get(url, params=params, headers=headers, timeout=timeout)
            elif http_method.upper() == 'PUT':
                response = self.session.put(url, json=params, headers=headers, timeout=timeout)
            elif http_method.upper() == 'DELETE':
                response = self.session.delete(url, json=params, headers=headers, timeout=timeout)
            else:
                response = self.session.post(url, json=params, headers=headers, timeout=timeout)

            try:
                response_data = response.json() if response.text else {}
            except:
                response_data = {'raw_response': response.text}

            return {
                'success': 200 <= response.status_code < 300,
                'method': http_method,
                'url': url,
                'status_code': response.status_code,
                'response': response_data,
                'timestamp': datetime.now().isoformat()
            }

        except requests.Timeout:
            raise ProtocolError(f"HTTP命令超时: {timeout}s")
        except requests.RequestException as e:
            raise ProtocolError(f"HTTP命令失败: {str(e)}")

    def subscribe(self, device_did: str, topics: Optional[list] = None):
        """HTTP 轮询机制（仅主动拉取模式）"""
        config = self.device_configs.get(device_did, {})
        base_url = self.device_endpoints.get(device_did, "")

        # 主动上报模式不需要轮询
        if not base_url:
            print(f"[HTTP] 设备 {device_did} 为主动上报模式，跳过轮询")
            return

        poll_interval = config.get('poll_interval', 30)
        poll_endpoint = config.get('poll_endpoint', '/data')

        import threading
        import time

        def poll_loop():
            while device_did in self.device_endpoints:
                try:
                    if base_url:
                        url = f"{base_url}{poll_endpoint}"
                        response = self.session.get(url, timeout=10)
                        if response.status_code == 200:
                            try:
                                data = response.json()
                                self._on_data(device_did, {
                                    'payload': data,
                                    'timestamp': datetime.now().isoformat()
                                })
                            except:
                                pass
                except Exception as e:
                    print(f"[HTTP] 轮询错误: {e}")

                time.sleep(poll_interval)

        if config.get('poll_enabled', False):
            thread = threading.Thread(target=poll_loop, daemon=True)
            thread.start()
            print(f"[HTTP] 启动轮询: {poll_interval}s")

    # 🆕 新增方法：处理设备主动上报的数据
    def ingest_data(self, device_did: str, payload: Dict[str, Any]) -> None:
        """
        处理设备主动上报的数据
        供 /ingest/http 接口调用
        """
        print(f"[HTTP] 设备 {device_did} 主动上报数据")
        self._on_data(device_did, {
            'payload': payload,
            'timestamp': datetime.now().isoformat()
        })