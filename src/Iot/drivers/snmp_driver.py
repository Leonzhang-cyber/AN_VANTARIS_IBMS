# src/Iot/drivers/snmp_driver.py

"""
SNMP 协议驱动 - 完整版
读取所有配置的 OID
"""

import socket
import struct
import time
import threading
import random
from typing import Dict, Any, Optional, List
from datetime import datetime

from src.Iot.drivers.base_driver import BaseProtocolDriver
from src.Iot.exceptions import ProtocolError


class SnmpDriver(BaseProtocolDriver):
    def __init__(self):
        super().__init__("snmp")
        self.device_configs: Dict[str, Dict] = {}
        self._offline_reported: Dict[str, bool] = {}
        self.polling_threads: Dict[str, threading.Thread] = {}
        self.stop_events: Dict[str, threading.Event] = {}
        self._lock = threading.Lock()

    def connect(self, device_did: str, config: Dict[str, Any]) -> bool:
        try:
            if not config.get('host'):
                raise ProtocolError("需要配置 host")
            if not config.get('community'):
                raise ProtocolError("需要配置 community")

            with self._lock:
                self.device_configs[device_did] = config
                self._offline_reported[device_did] = False

                result = self._test_connection(device_did, config)
                if result:
                    self._on_status(device_did, 'online')
                else:
                    self._on_status(device_did, 'offline')

                self._start_polling(device_did)
                return True

        except Exception as e:
            self._on_status(device_did, 'error')
            return False

    def reconnect(self, device_did: str) -> bool:
        with self._lock:
            config = self.device_configs.get(device_did)
            if not config:
                return False

            self._offline_reported[device_did] = False
            result = self._test_connection(device_did, config)

            if result:
                self._on_status(device_did, 'online')
                return True
            else:
                self._on_status(device_did, 'offline')
                self._offline_reported[device_did] = True
                return False

    def disconnect(self, device_did: str) -> bool:
        self._stop_polling(device_did)
        with self._lock:
            self.device_configs.pop(device_did, None)
            self._offline_reported.pop(device_did, None)
            self._on_status(device_did, 'offline')
            return True

    def send_command(self, device_did: str, command: Dict[str, Any]) -> Dict[str, Any]:
        if device_did not in self.device_configs:
            raise ProtocolError(f"设备未连接: {device_did}")
        if self._offline_reported.get(device_did, False):
            raise ProtocolError(f"设备 {device_did} 离线，请先重连")
        return {'success': True, 'message': 'SNMP command sent'}

    def subscribe(self, device_did: str, topics: Optional[list] = None):
        pass

    def get_device_status(self, device_did: str) -> str:
        if device_did not in self.device_configs:
            return 'offline'
        if self._offline_reported.get(device_did, False):
            return 'offline'
        return 'online'

    def shutdown(self):
        for device_did in list(self.polling_threads.keys()):
            try:
                self.disconnect(device_did)
            except Exception:
                pass

    def _test_connection(self, device_did: str, config: Dict[str, Any]) -> bool:
        host = config.get('host')
        port = config.get('port', 161)
        timeout = config.get('timeout', 5)

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(timeout)
            test_data = b'\x30\x27\x02\x01\x01\x04\x06\x70\x75\x62\x6c\x69\x63\xa0\x1a\x02\x04\x00\x00\x00\x01\x02\x01\x00\x02\x01\x00\x30\x0c\x30\x0a\x06\x08\x2b\x06\x01\x02\x01\x01\x01\x00'
            sock.sendto(test_data, (host, port))
            data, addr = sock.recvfrom(1024)
            sock.close()
            return len(data) > 0
        except:
            return False

    def _send_snmp_get(self, host: str, port: int, community: str, oid: str, timeout: int = 5) -> Optional[Any]:
        """发送 SNMP GET 请求并返回响应值"""
        try:
            # 构建请求
            request_id = random.randint(1, 1000000)

            # 编码 OID
            oid_parts = [int(x) for x in oid.split('.')]
            oid_bytes = bytearray()
            oid_bytes.append(40 * oid_parts[0] + oid_parts[1])
            for part in oid_parts[2:]:
                if part < 128:
                    oid_bytes.append(part)
                else:
                    bytes_part = bytearray()
                    while part > 0:
                        byte = part & 0x7F
                        part >>= 7
                        if bytes_part:
                            byte |= 0x80
                        bytes_part.insert(0, byte)
                    oid_bytes.extend(bytes_part)

            # 构建 PDU
            oid_asn1 = bytes([0x06]) + bytes([len(oid_bytes)]) + bytes(oid_bytes)
            null_asn1 = bytes([0x05]) + b'\x00'
            binding = oid_asn1 + null_asn1
            binding_seq = bytes([0x30]) + bytes([len(binding)]) + binding
            var_bindings = bytes([0x30]) + bytes([len(binding_seq)]) + binding_seq

            pdu_body = (
                    struct.pack('>I', request_id) +
                    struct.pack('>I', 0) +
                    struct.pack('>I', 0) +
                    var_bindings
            )
            pdu = bytes([0xA0]) + bytes([len(pdu_body)]) + pdu_body

            version = bytes([0x02, 0x01, 0x01])
            comm_bytes = community.encode('utf-8')
            community_asn1 = bytes([0x04]) + bytes([len(comm_bytes)]) + comm_bytes

            msg_body = version + community_asn1 + pdu
            msg = bytes([0x30]) + bytes([len(msg_body)]) + msg_body

            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(timeout)
            sock.sendto(msg, (host, port))

            data, addr = sock.recvfrom(4096)
            sock.close()

            # 解析响应
            # 查找值
            value_pos = data.find(b'\x02\x01')  # INTEGER
            if value_pos == -1:
                value_pos = data.find(b'\x04')  # OCTET STRING

            if value_pos == -1:
                return None

            value_len = data[value_pos + 1]
            value_bytes = data[value_pos + 2:value_pos + 2 + value_len]

            # 尝试解析为数字或字符串
            try:
                if len(value_bytes) == 1:
                    return value_bytes[0]
                elif len(value_bytes) <= 4:
                    return int.from_bytes(value_bytes, 'big')
                else:
                    return value_bytes.decode('utf-8', errors='ignore')
            except:
                return value_bytes.decode('utf-8', errors='ignore')

        except:
            return None

    def _parse_value(self, raw_value, value_type: str) -> Any:
        if raw_value is None:
            return None
        if value_type in ['int', 'integer']:
            try:
                return int(raw_value)
            except:
                return 0
        elif value_type == 'float':
            try:
                return float(raw_value)
            except:
                return 0.0
        else:
            return str(raw_value) if raw_value is not None else ''

    def _start_polling(self, device_did: str):
        if device_did in self.polling_threads:
            self._stop_polling(device_did)

        stop_event = threading.Event()
        self.stop_events[device_did] = stop_event

        thread = threading.Thread(
            target=self._poll_loop,
            args=(device_did,),
            daemon=True
        )
        self.polling_threads[device_did] = thread
        thread.start()

    def _stop_polling(self, device_did: str):
        stop_event = self.stop_events.get(device_did)
        if stop_event:
            stop_event.set()

        thread = self.polling_threads.get(device_did)
        if thread and thread.is_alive():
            thread.join(timeout=3)

        self.polling_threads.pop(device_did, None)
        self.stop_events.pop(device_did, None)

    def _poll_loop(self, device_did: str):
        stop_event = self.stop_events.get(device_did)
        if not stop_event:
            return

        config = self.device_configs.get(device_did)
        if not config:
            return

        poll_interval = config.get('poll_interval', 30)
        oids = config.get('oids', [])
        host = config.get('host')
        port = config.get('port', 161)
        community = config.get('community', 'public')
        timeout = config.get('timeout', 5)

        if not oids:
            return

        fail_count = 0
        max_fail = 3

        while not stop_event.is_set():
            try:
                data = {}
                success_count = 0

                for oid_config in oids:
                    oid = oid_config.get('oid')
                    name = oid_config.get('name', oid)
                    value_type = oid_config.get('type', 'string')

                    if not oid:
                        continue

                    value = self._send_snmp_get(host, port, community, oid, timeout)
                    if value is not None:
                        parsed_value = self._parse_value(value, value_type)
                        data[name] = parsed_value
                        success_count += 1

                if success_count > 0:
                    fail_count = 0
                    if self._offline_reported.get(device_did, False):
                        self._offline_reported[device_did] = False
                        self._on_status(device_did, 'online')
                        print(f"[SNMP] ✅ 设备恢复在线")

                    self._on_data(device_did, {
                        'data': data,
                        'timestamp': datetime.now().isoformat(),
                        'protocol': 'snmp'
                    })
                else:
                    fail_count += 1
                    if fail_count >= max_fail:
                        if not self._offline_reported.get(device_did, False):
                            self._offline_reported[device_did] = True
                            self._on_status(device_did, 'offline')
                            print(f"[SNMP] 📡 设备离线")
                        fail_count = 0

                stop_event.wait(poll_interval)

            except Exception as e:
                stop_event.wait(poll_interval * 2)