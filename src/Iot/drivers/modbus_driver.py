# src/Iot/drivers/modbus_driver.py

import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from threading import Lock, Thread, Event

# 兼容 pymodbus 2.5.3 的导入方式
POMODBUS_AVAILABLE = False
try:
    # pymodbus 2.x 使用 client.sync
    from pymodbus.client.sync import ModbusTcpClient, ModbusSerialClient
    from pymodbus.exceptions import ModbusException, ConnectionException
    POMODBUS_AVAILABLE = True
    print("[Modbus] Registered driver:modbus")
except ImportError:
    try:
        # pymodbus 3.x 使用 client
        from pymodbus.client import ModbusTcpClient, ModbusSerialClient
        from pymodbus.exceptions import ModbusException, ConnectionException
        POMODBUS_AVAILABLE = True
        # print("[Modbus] ✅ pymodbus 3.x 加载成功")
    except ImportError as e:
        print(f"[Modbus] ❌ pymodbus 导入失败: {e}")
        print("[Modbus] 请运行: pip install pymodbus==2.5.3")

from src.Iot.drivers.base_driver import BaseProtocolDriver
from src.Iot.exceptions import ProtocolError


class ModbusDriver(BaseProtocolDriver):
    """
    Modbus协议驱动 - 支持RTU(串口)和TCP/IP两种模式

    重连策略:
    - 设备掉线后自动检测
    - 间隔5分钟尝试重连一次
    - 重连成功后自动恢复数据采集
    """

    # 重连间隔（秒）
    RECONNECT_INTERVAL = 300  # 5分钟

    def __init__(self):
        super().__init__("modbus")
        if not POMODBUS_AVAILABLE:
            raise ImportError("pymodbus library is required for ModbusDriver. Please run: pip install pymodbus==2.5.3")

        # 设备客户端映射: device_did -> (client, config)
        self.device_clients: Dict[str, tuple] = {}
        # 设备配置缓存
        self.device_configs: Dict[str, Dict] = {}
        # 设备轮询线程控制
        self.polling_threads: Dict[str, Thread] = {}
        self.polling_events: Dict[str, Event] = {}
        # 设备重连标志: device_did -> bool (True表示正在重连中)
        self.reconnecting: Dict[str, bool] = {}
        # 线程锁
        self._lock = Lock()
        # 寄存器映射缓存: device_did -> register_map
        self.register_maps: Dict[str, Dict] = {}

    def connect(self, device_did: str, config: Dict[str, Any]) -> bool:
        """连接Modbus设备"""
        try:
            self._validate_config(config)

            with self._lock:
                if device_did in self.device_clients:
                    self.disconnect(device_did)

                client = self._create_client(config)
                if not self._connect_client(client, config):
                    raise ProtocolError("Modbus连接失败")

                self.device_clients[device_did] = (client, config)
                self.device_configs[device_did] = config
                self.register_maps[device_did] = self._build_register_map(config)
                self.reconnecting[device_did] = False

                self._on_status(device_did, 'online')
                self._start_polling(device_did)

                print(f"[Modbus] 设备（等待连接）")
                return True

        except Exception as e:
            self._on_status(device_did, 'error')
            print(f"[Modbus] 设备（等待连接）")
            raise ProtocolError(f"Modbus连接失败: {str(e)}")

    def disconnect(self, device_did: str) -> bool:
        """断开设备连接"""
        with self._lock:
            if device_did not in self.device_clients:
                return False

            self._stop_polling(device_did)

            client, _ = self.device_clients.pop(device_did, (None, None))
            if client and hasattr(client, 'is_socket_open') and client.is_socket_open():
                try:
                    client.close()
                except Exception as e:
                    print(f"[Modbus] 关闭连接异常: {e}")

            self.device_configs.pop(device_did, None)
            self.register_maps.pop(device_did, None)
            self.reconnecting.pop(device_did, None)

            self._on_status(device_did, 'offline')
            print(f"[Modbus] 设备 {device_did} 已断开")
            return True

    def send_command(self, device_did: str, command: Dict[str, Any]) -> Dict[str, Any]:
        """下发Modbus命令"""
        if device_did not in self.device_clients:
            raise ProtocolError(f"设备未连接: {device_did}")

        client, config = self.device_clients[device_did]
        if client is None or not self._is_client_online(client):
            raise ProtocolError(f"设备 {device_did} 不在线")

        slave_id = config.get('slave_id', 1)
        method = command.get('method')
        params = command.get('params', {})

        from src.Iot.dao import StandardMethodDAO
        standard_method = StandardMethodDAO.get_by_code(method)
        if standard_method:
            return self._send_by_standard_method(device_did, method, params)

        return self._send_raw_command(client, slave_id, method, params, config)

    def subscribe(self, device_did: str, topics: Optional[list] = None):
        """Modbus使用轮询模式，订阅操作留空以兼容基类"""
        pass

    # ==================== 核心方法 ====================

    def _is_client_online(self, client) -> bool:
        """检查客户端是否在线"""
        if client is None:
            return False
        try:
            if hasattr(client, 'is_socket_open'):
                return client.is_socket_open()
            return False
        except:
            return False

    def _poll_device(self, device_did: str):
        """
        轮询设备数据

        重连策略: 设备掉线后，每5分钟尝试重连一次
        """
        event = self.polling_events.get(device_did)
        if not event:
            return

        config = self.device_configs.get(device_did)
        if not config:
            return

        poll_interval = config.get('poll_interval', 5)
        slave_id = config.get('slave_id', 1)

        while not event.is_set():
            try:
                # 获取客户端
                with self._lock:
                    if device_did not in self.device_clients:
                        break
                    client, config = self.device_clients[device_did]

                # 检查连接状态
                if client is None or not self._is_client_online(client):
                    # 设备掉线，触发状态更新
                    self._on_status(device_did, 'offline')

                    # 检查是否正在重连中
                    if self.reconnecting.get(device_did, False):
                        # 已在重连中，等待
                        event.wait(60)
                        continue

                    # 标记开始重连
                    self.reconnecting[device_did] = True
                    print(f"[Modbus] 设备 {device_did} 掉线，{self.RECONNECT_INTERVAL}秒后尝试重连...")

                    # 等待重连间隔（5分钟）
                    if event.wait(self.RECONNECT_INTERVAL):
                        # 如果被外部中断（disconnect），退出
                        break

                    # 执行重连
                    try:
                        print(f"[Modbus] 设备 {device_did} 开始重连...")
                        new_client = self._create_client(config)
                        if self._connect_client(new_client, config):
                            with self._lock:
                                if device_did in self.device_clients:
                                    old_client, _ = self.device_clients[device_did]
                                    if old_client:
                                        try:
                                            old_client.close()
                                        except:
                                            pass
                                    self.device_clients[device_did] = (new_client, config)
                            self._on_status(device_did, 'online')
                            self.reconnecting[device_did] = False
                            print(f"[Modbus] 设备 {device_did} 重连成功 ✅")
                            # 重连成功后立即读取一次数据
                            continue
                        else:
                            print(f"[Modbus] 设备 {device_did} 重连失败 ❌")
                            self.reconnecting[device_did] = False
                    except Exception as e:
                        print(f"[Modbus] 设备 {device_did} 重连异常: {e}")
                        self.reconnecting[device_did] = False

                    # 重连失败，继续等待下一轮
                    continue

                # 设备在线，正常读取数据
                if self.reconnecting.get(device_did, False):
                    self.reconnecting[device_did] = False
                    self._on_status(device_did, 'online')

                data = self._read_all_registers(device_did, client, slave_id)

                if data:
                    self._on_data(device_did, {
                        'data': data,
                        'timestamp': datetime.now().isoformat(),
                        'slave_id': slave_id,
                        'protocol': 'modbus'
                    })

                # 等待下次轮询
                event.wait(poll_interval)

            except Exception as e:
                print(f"[Modbus] 设备 {device_did} 通信异常: {e}")
                self._on_status(device_did, 'error')
                # 标记客户端为失效，下次循环会重连
                with self._lock:
                    if device_did in self.device_clients:
                        old_client, _ = self.device_clients[device_did]
                        if old_client:
                            try:
                                old_client.close()
                            except:
                                pass
                        self.device_clients[device_did] = (None, config)
                # 等待后进入重连流程
                event.wait(10)

    # ==================== 私有方法 ====================

    def _validate_config(self, config: Dict[str, Any]):
        """验证配置"""
        mode = config.get('mode', 'tcp').lower()
        if mode not in ['tcp', 'rtu']:
            raise ProtocolError(f"不支持的Modbus模式: {mode}，仅支持 tcp 或 rtu")

        if mode == 'tcp':
            if not config.get('host'):
                raise ProtocolError("TCP模式需要配置 host")
        else:
            if not config.get('serial_port'):
                raise ProtocolError("RTU模式需要配置 serial_port")

        if config.get('slave_id') is None:
            raise ProtocolError("需要配置 slave_id")

    def _create_client(self, config: Dict[str, Any]):
        """创建Modbus客户端"""
        mode = config.get('mode', 'tcp').lower()
        if mode == 'tcp':
            return ModbusTcpClient(
                host=config.get('host'),
                port=config.get('port', 502),
                timeout=config.get('timeout', 3)
            )
        else:
            return ModbusSerialClient(
                port=config.get('serial_port'),
                baudrate=config.get('baudrate', 9600),
                bytesize=config.get('bytesize', 8),
                parity=config.get('parity', 'N'),
                stopbits=config.get('stopbits', 1),
                timeout=config.get('timeout', 3)
            )

    def _connect_client(self, client, config: Dict[str, Any]) -> bool:
        """连接客户端（带重试）"""
        retry_count = config.get('retry_count', 3)
        retry_interval = config.get('retry_interval', 1)

        for attempt in range(retry_count):
            try:
                if client.connect():
                    print(f"[Modbus] 连接成功 (尝试 {attempt + 1}/{retry_count})")
                    return True
            except Exception as e:
                print(f"[Modbus] 连接尝试 {attempt + 1} 失败: {e}")

            if attempt < retry_count - 1:
                time.sleep(retry_interval)

        return False

    def _build_register_map(self, config: Dict[str, Any]) -> Dict:
        """构建寄存器映射表"""
        register_map = {
            'coils': {},
            'discrete_inputs': {},
            'input_registers': {},
            'holding_registers': {},
        }

        for reg_config in config.get('registers', []):
            reg_type = reg_config.get('type', 'holding_register')
            address = reg_config.get('address')
            name = reg_config.get('name')

            if reg_type == 'coil':
                register_map['coils'][address] = reg_config
            elif reg_type == 'discrete_input':
                register_map['discrete_inputs'][address] = reg_config
            elif reg_type == 'input_register':
                register_map['input_registers'][address] = reg_config
            elif reg_type == 'holding_register':
                register_map['holding_registers'][address] = reg_config

        return register_map

    def _read_register(self, client, slave_id: int, reg_type: str, address: int, count: int = 1):
        """读取寄存器"""
        try:
            if reg_type == 'coil':
                result = client.read_coils(address, count, unit=slave_id)
            elif reg_type == 'discrete_input':
                result = client.read_discrete_inputs(address, count, unit=slave_id)
            elif reg_type == 'input_register':
                result = client.read_input_registers(address, count, unit=slave_id)
            elif reg_type == 'holding_register':
                result = client.read_holding_registers(address, count, unit=slave_id)
            else:
                raise ProtocolError(f"不支持的寄存器类型: {reg_type}")

            if result.isError():
                raise ProtocolError(f"读取失败: {result}")

            return result.registers if hasattr(result, 'registers') else result.bits

        except ModbusException as e:
            raise ProtocolError(f"Modbus异常: {e}")

    def _parse_value(self, raw_value, config: Dict[str, Any]) -> Any:
        """解析值"""
        scale = config.get('scale', 1.0)
        offset = config.get('offset', 0)
        data_type = config.get('data_type', 'float')

        if isinstance(raw_value, list):
            raw_value = raw_value[0] if raw_value else 0

        value = raw_value * scale + offset

        if data_type == 'int':
            return int(value)
        elif data_type == 'float':
            return float(value)
        elif data_type == 'bool':
            return bool(value)
        else:
            return value

    def _read_all_registers(self, device_did: str, client, slave_id: int) -> Dict[str, Any]:
        """读取所有已配置的寄存器"""
        result = {}
        register_map = self.register_maps.get(device_did, {})

        for reg_type, reg_map in [
            ('coil', 'coils'),
            ('discrete_input', 'discrete_inputs'),
            ('input_register', 'input_registers'),
            ('holding_register', 'holding_registers')
        ]:
            for address, reg_config in register_map.get(reg_map, {}).items():
                try:
                    value = self._read_register(client, slave_id, reg_type, address)
                    result[reg_config['name']] = self._parse_value(value, reg_config)
                except Exception as e:
                    # print(f"[Modbus] 读取 {reg_type} {address} 失败: {e}")
                    result[reg_config['name']] = None

        return result

    def _start_polling(self, device_did: str):
        """启动轮询线程"""
        if device_did in self.polling_threads:
            self._stop_polling(device_did)

        event = Event()
        self.polling_events[device_did] = event

        thread = Thread(
            target=self._poll_device,
            args=(device_did,),
            daemon=True,
            name=f"ModbusPoll-{device_did[:8]}"
        )
        self.polling_threads[device_did] = thread
        thread.start()

    def _stop_polling(self, device_did: str):
        """停止轮询线程"""
        event = self.polling_events.get(device_did)
        if event:
            event.set()

        thread = self.polling_threads.get(device_did)
        if thread and thread.is_alive():
            thread.join(timeout=2)

        self.polling_threads.pop(device_did, None)
        self.polling_events.pop(device_did, None)

    def _send_by_standard_method(self, device_did: str, method: str, params: Dict) -> Dict[str, Any]:
        """通过标准方法下发命令"""
        from src.Iot.dao import StandardMethodDAO, MethodMappingDAO

        standard_method = StandardMethodDAO.get_by_code(method)
        if not standard_method:
            raise ProtocolError(f"未知的标准方法: {method}")

        if standard_method.params_schema:
            schema = standard_method.params_schema
            if isinstance(schema, str):
                schema = json.loads(schema)
            required = schema.get('required', [])
            for req in required:
                if req not in params:
                    raise ProtocolError(f"缺少必要参数: {req}")

        method_mapping = MethodMappingDAO.get_mapping_by_standard(
            device_did, 'modbus', 'downlink', method
        )

        if not method_mapping:
            raise ProtocolError(f"设备未配置方法映射: {method}")

        extra = method_mapping.extra or {}
        address = extra.get('address')
        reg_type = extra.get('register_type', 'holding_register')
        value = params.get('value')

        if address is None:
            raise ProtocolError("方法映射缺少 address 配置")

        with self._lock:
            if device_did not in self.device_clients:
                raise ProtocolError(f"设备未连接: {device_did}")
            client, config = self.device_clients[device_did]

        if client is None or not self._is_client_online(client):
            raise ProtocolError(f"设备 {device_did} 不在线")

        slave_id = config.get('slave_id', 1)
        success = self._write_register(client, slave_id, reg_type, address, value)

        return {
            'success': success,
            'method': method,
            'address': address,
            'value': value,
            'register_type': reg_type,
            'timestamp': datetime.now().isoformat()
        }

    def _send_raw_command(self, client, slave_id: int, method: str, params: Dict, config: Dict) -> Dict[str, Any]:
        """发送原始Modbus命令"""
        if method == 'write_register':
            address = params.get('address')
            value = params.get('value')
            reg_type = params.get('register_type', 'holding_register')
            success = self._write_register(client, slave_id, reg_type, address, value)
            return {
                'success': success,
                'method': method,
                'address': address,
                'value': value,
                'timestamp': datetime.now().isoformat()
            }
        elif method == 'write_coil':
            address = params.get('address')
            value = params.get('value')
            success = self._write_register(client, slave_id, 'coil', address, value)
            return {
                'success': success,
                'method': method,
                'address': address,
                'value': bool(value),
                'timestamp': datetime.now().isoformat()
            }
        elif method == 'read_register':
            address = params.get('address')
            reg_type = params.get('register_type', 'holding_register')
            count = params.get('count', 1)
            raw_value = self._read_register(client, slave_id, reg_type, address, count)
            return {
                'success': True,
                'method': method,
                'address': address,
                'value': raw_value,
                'timestamp': datetime.now().isoformat()
            }
        else:
            raise ProtocolError(f"不支持的Modbus方法: {method}")

    def _write_register(self, client, slave_id: int, reg_type: str, address: int, value,
                        function_code: int = None) -> bool:
        """写入寄存器"""
        try:
            if reg_type in ['coil', 'discrete_input']:
                value = bool(value)
                result = client.write_coil(address, value, unit=slave_id)
            else:
                result = client.write_register(address, int(value), unit=slave_id)

            if result.isError():
                raise ProtocolError(f"写入失败: {result}")

            return True

        except ModbusException as e:
            raise ProtocolError(f"Modbus写入异常: {e}")

    # ==================== 公开辅助方法 ====================

    def read_registers(self, device_did: str, address: int, count: int = 1, reg_type: str = 'holding_register') -> Any:
        """手动读取寄存器"""
        with self._lock:
            if device_did not in self.device_clients:
                raise ProtocolError(f"设备未连接: {device_did}")
            client, config = self.device_clients[device_did]

        if client is None or not self._is_client_online(client):
            raise ProtocolError(f"设备 {device_did} 不在线")

        slave_id = config.get('slave_id', 1)
        return self._read_register(client, slave_id, reg_type, address, count)

    def write_register(self, device_did: str, address: int, value, reg_type: str = 'holding_register') -> bool:
        """手动写入寄存器"""
        with self._lock:
            if device_did not in self.device_clients:
                raise ProtocolError(f"设备未连接: {device_did}")
            client, config = self.device_clients[device_did]

        if client is None or not self._is_client_online(client):
            raise ProtocolError(f"设备 {device_did} 不在线")

        slave_id = config.get('slave_id', 1)
        return self._write_register(client, slave_id, reg_type, address, value)

    def get_device_status(self, device_did: str) -> str:
        """获取设备状态"""
        with self._lock:
            if device_did not in self.device_clients:
                return 'offline'
            client, _ = self.device_clients[device_did]

        if self._is_client_online(client):
            return 'online'
        return 'offline'

    def update_register_map(self, device_did: str, registers: List[Dict[str, Any]]):
        """动态更新寄存器映射"""
        with self._lock:
            if device_did not in self.device_clients:
                raise ProtocolError(f"设备未连接: {device_did}")

            config = self.device_configs.get(device_did, {})
            config['registers'] = registers
            self.register_maps[device_did] = self._build_register_map(config)

    def shutdown(self):
        """关闭所有连接"""
        print("[Modbus] 正在关闭所有连接...")
        for device_did in list(self.device_clients.keys()):
            try:
                self.disconnect(device_did)
            except Exception as e:
                print(f"[Modbus] 关闭设备 {device_did} 失败: {e}")
        print("[Modbus] 所有连接已关闭")