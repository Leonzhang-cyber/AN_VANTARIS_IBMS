# src/Iot/drivers/opcua_driver.py

import asyncio
import json
import threading
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

from src.Iot.drivers.base_driver import BaseProtocolDriver
from src.Iot.exceptions import ProtocolError

# 导入 asyncua
ASYNCUA_AVAILABLE = False
try:
    from asyncua import Client, Node, ua
    ASYNCUA_AVAILABLE = True
except ImportError:
    print("[OPC UA] ⚠️ asyncua 未安装，请运行: pip install asyncua")


class OpcUaDriver(BaseProtocolDriver):
    """OPC UA 协议驱动 - 客户端模式"""

    def __init__(self):
        super().__init__("opcua")
        if not ASYNCUA_AVAILABLE:
            raise ImportError("asyncua library is required. Please run: pip install asyncua")

        self.device_clients: Dict[str, Client] = {}
        self.device_configs: Dict[str, Dict] = {}
        self.subscription_threads: Dict[str, threading.Thread] = {}
        self.stop_events: Dict[str, threading.Event] = {}
        self.loops: Dict[str, asyncio.AbstractEventLoop] = {}
        self._lock = threading.Lock()
        # 用于记录是否已打印"等待连接"
        self._waiting_printed: Dict[str, bool] = {}

    def connect(self, device_did: str, config: Dict[str, Any]) -> bool:
        """连接 OPC UA 服务器"""
        try:
            if not config.get('url'):
                raise ProtocolError("OPC UA 驱动需要配置 'url'")

            # 打印"等待连接"
            if not self._waiting_printed.get(device_did, False):
                print(f"[OPC UA] 设备（等待连接）")
                self._waiting_printed[device_did] = True

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.loops[device_did] = loop

            success = loop.run_until_complete(
                self._async_connect(device_did, config)
            )

            if success:
                self.device_configs[device_did] = config
                self._on_status(device_did, 'online')
                self._start_subscription(device_did)
                return True
            else:
                self._on_status(device_did, 'error')
                return False

        except Exception as e:
            self._on_status(device_did, 'error')
            return False

    async def _async_connect(self, device_did: str, config: Dict[str, Any]) -> bool:
        """异步连接逻辑"""
        url = config['url']

        if '127.0.0.1' in url and 'localhost' not in url:
            url = url.replace('127.0.0.1', 'localhost')

        try:
            client = Client(url=url)
            client.timeout = 10

            if config.get('username') and config.get('password'):
                try:
                    client.set_user(config['username'])
                    client.set_password(config['password'])
                except Exception:
                    pass

            await asyncio.wait_for(client.connect(), timeout=10)
            self.device_clients[device_did] = client
            return True

        except Exception:
            return False

    def disconnect(self, device_did: str) -> bool:
        """断开设备连接"""
        self._stop_subscription(device_did)

        with self._lock:
            if device_did not in self.device_clients:
                return False

            client = self.device_clients.pop(device_did, None)
            loop = self.loops.pop(device_did, None)

            if client:
                try:
                    if loop and not loop.is_closed():
                        future = asyncio.run_coroutine_threadsafe(client.disconnect(), loop)
                        future.result(timeout=5)
                except Exception:
                    pass

            self.device_configs.pop(device_did, None)
            self._waiting_printed.pop(device_did, None)
            self._on_status(device_did, 'offline')
            return True

    def send_command(self, device_did: str, command: Dict[str, Any]) -> Dict[str, Any]:
        """下发命令"""
        if device_did not in self.device_clients:
            raise ProtocolError(f"设备未连接: {device_did}")

        method = command.get('method')
        params = command.get('params', {})

        try:
            from src.Iot.dao import StandardMethodDAO, MethodMappingDAO
            standard_method = StandardMethodDAO.get_by_code(method)
            if standard_method:
                method_mapping = MethodMappingDAO.get_mapping_by_standard(
                    device_did, 'opcua', 'downlink', method
                )
                if method_mapping:
                    extra = method_mapping.extra or {}
                    node_id = extra.get('node_id')
                    data_type = extra.get('data_type', 'Float')
                    if node_id:
                        value = params.get('value')
                        if value is not None:
                            return self._write_value(device_did, {
                                'node_id': node_id,
                                'value': value,
                                'data_type': data_type
                            })
        except ImportError:
            pass

        if method == 'write_value':
            return self._write_value(device_did, params)
        elif method == 'call_method':
            return self._call_method(device_did, params)
        else:
            raise ProtocolError(f"不支持的 OPC UA 方法: {method}")

    def _write_value(self, device_did: str, params: Dict) -> Dict[str, Any]:
        """向 OPC UA 节点写入值"""
        node_id = params.get('node_id')
        value = params.get('value')
        data_type = params.get('data_type', 'Float')

        if not node_id:
            raise ProtocolError("缺少 node_id 参数")

        client = self.device_clients.get(device_did)
        if not client:
            raise ProtocolError("客户端未连接")

        loop = self.loops.get(device_did)
        if not loop or loop.is_closed():
            raise ProtocolError("事件循环已关闭")

        try:
            node = client.get_node(node_id)
            future = asyncio.run_coroutine_threadsafe(
                self._async_write_value(node, value, data_type),
                loop
            )
            success = future.result(timeout=10)

            return {
                'success': success,
                'node_id': node_id,
                'value': value,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            raise ProtocolError(f"写入失败: {e}")

    async def _async_write_value(self, node: Node, value, data_type: str):
        """异步写入值"""
        try:
            if data_type == 'Float':
                await node.write_value(float(value))
            elif data_type == 'Int':
                await node.write_value(int(value))
            elif data_type == 'Bool':
                await node.write_value(bool(value))
            elif data_type == 'String':
                await node.write_value(str(value))
            else:
                await node.write_value(value)
            return True
        except Exception:
            return False

    def _call_method(self, device_did: str, params: Dict) -> Dict[str, Any]:
        """调用 OPC UA 节点的方法"""
        raise NotImplementedError("OPC UA 方法调用待实现")

    def subscribe(self, device_did: str, topics: Optional[list] = None):
        """订阅 OPC UA 节点数据"""
        pass

    def _start_subscription(self, device_did: str):
        """启动订阅线程"""
        if device_did in self.subscription_threads:
            self._stop_subscription(device_did)

        stop_event = threading.Event()
        self.stop_events[device_did] = stop_event

        thread = threading.Thread(
            target=self._subscription_loop,
            args=(device_did,),
            daemon=True,
            name=f"OpcUaSubscription-{device_did[:8]}"
        )
        self.subscription_threads[device_did] = thread
        thread.start()

    def _subscription_loop(self, device_did: str):
        """订阅循环 - 在独立线程中运行"""
        stop_event = self.stop_events.get(device_did)
        if not stop_event:
            return

        config = self.device_configs.get(device_did)
        if not config:
            return

        nodes_config = config.get('nodes', [])
        poll_interval = config.get('poll_interval', 2)

        if not nodes_config:
            return

        loop = self.loops.get(device_did)
        if not loop or loop.is_closed():
            return

        while not stop_event.is_set():
            try:
                client = self.device_clients.get(device_did)
                if not client:
                    stop_event.wait(poll_interval * 2)
                    continue

                node_values = loop.run_until_complete(
                    self._async_read_nodes(client, nodes_config)
                )

                if node_values:
                    self._on_data(device_did, {
                        'data': node_values,
                        'timestamp': datetime.now().isoformat(),
                        'protocol': 'opcua'
                    })
                    self._on_status(device_did, 'online')

                stop_event.wait(poll_interval)

            except Exception:
                stop_event.wait(poll_interval * 2)

    async def _async_read_nodes(self, client: Client, nodes_config: List[Dict]) -> Dict[str, Any]:
        """异步读取多个节点"""
        result = {}
        for node_config in nodes_config:
            try:
                node_id = node_config.get('node_id')
                name = node_config.get('name', node_id)
                if not node_id:
                    continue
                node = client.get_node(node_id)
                value = await node.read_value()
                result[name] = value
            except Exception:
                result[node_config.get('name', node_id)] = None
        return result

    def _stop_subscription(self, device_did: str):
        """停止订阅线程"""
        stop_event = self.stop_events.get(device_did)
        if stop_event:
            stop_event.set()

        thread = self.subscription_threads.get(device_did)
        if thread and thread.is_alive():
            thread.join(timeout=3)

        self.subscription_threads.pop(device_did, None)
        self.stop_events.pop(device_did, None)

    def get_device_status(self, device_did: str) -> str:
        """获取设备状态"""
        with self._lock:
            if device_did not in self.device_clients:
                return 'offline'
            client = self.device_clients.get(device_did)
            if client:
                try:
                    loop = self.loops.get(device_did)
                    if loop and not loop.is_closed():
                        return 'online'
                except:
                    pass
            return 'offline'

    def shutdown(self):
        """关闭所有连接"""
        for device_did in list(self.device_clients.keys()):
            try:
                self.disconnect(device_did)
            except Exception:
                pass