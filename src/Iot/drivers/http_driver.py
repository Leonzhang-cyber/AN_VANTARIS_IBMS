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
    """HTTP协议驱动"""

    def __init__(self):
        super().__init__("http")
        self.device_endpoints: Dict[str, str] = {}  # {device_did: base_url}
        self.device_configs: Dict[str, Dict] = {}  # {device_did: config}
        self.session = requests.Session()

    def connect(self, device_did: str, config: Dict[str, Any]) -> bool:
        """连接HTTP设备（验证连接）"""
        base_url = config.get('base_url')
        if not base_url:
            raise ProtocolError("缺少 base_url 配置")

        # 可选：验证连接
        verify_endpoint = config.get('verify_endpoint', '/health')
        timeout = config.get('timeout', 10)

        try:
            url = f"{base_url}{verify_endpoint}"
            response = self.session.get(url, timeout=timeout)
            if response.status_code < 500:
                self.device_endpoints[device_did] = base_url
                self.device_configs[device_did] = config
                self._on_status(device_did, 'online')
                print(f"[HTTP] 设备 {device_did} 连接成功: {base_url}")
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
        """下发HTTP命令"""
        base_url = self.device_endpoints.get(device_did)
        if not base_url:
            raise ProtocolError(f"设备未连接: {device_did}")

        config = self.device_configs.get(device_did, {})

        # 获取命令参数
        endpoint = command.get('endpoint', '/command')
        http_method = command.get('http_method', 'POST')
        params = command.get('params', {})
        headers = command.get('headers', {'Content-Type': 'application/json'})
        timeout = config.get('timeout', 10)

        url = f"{base_url}{endpoint}"

        print(f"[HTTP] 下发命令: method={http_method}, url={url}, params={params}")

        try:
            if http_method.upper() == 'GET':
                response = self.session.get(url, params=params, headers=headers, timeout=timeout)
            elif http_method.upper() == 'PUT':
                response = self.session.put(url, json=params, headers=headers, timeout=timeout)
            elif http_method.upper() == 'DELETE':
                response = self.session.delete(url, json=params, headers=headers, timeout=timeout)
            else:  # POST 默认
                response = self.session.post(url, json=params, headers=headers, timeout=timeout)

            # 解析响应
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
        """HTTP 通常使用轮询，这里实现轮询机制"""
        config = self.device_configs.get(device_did, {})
        poll_interval = config.get('poll_interval', 30)
        poll_endpoint = config.get('poll_endpoint', '/data')

        import threading
        import time

        def poll_loop():
            while device_did in self.device_endpoints:
                try:
                    base_url = self.device_endpoints.get(device_did)
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