# src/testMQTT/snmp_simulator.py

"""
SNMP 设备模拟器 - 完整版
模拟 12 个 OID 数据
"""

import socket
import struct
import time
import random
import threading
from datetime import datetime


class SnmpSimulator:
    def __init__(self, host='0.0.0.0', port=11610, community='public'):
        self.host = host
        self.port = port
        self.community = community
        self.running = False
        self.sock = None
        self.start_time = time.time()

        # 模拟数据 - 对应 12 个 OID
        self.values = {
            '1.3.6.1.2.1.1.5.0': 'SNMP-SIM-001',  # sys_name
            '1.3.6.1.2.1.1.1.0': 'SNMP Simulator v1.0',  # sys_descr
            '1.3.6.1.2.1.1.3.0': 0,  # uptime
            '1.3.6.1.4.1.2011.1': 45.2,  # cpu_usage
            '1.3.6.1.4.1.2011.2': 60.5,  # memory_usage
            '1.3.6.1.4.1.2011.3': 24.5,  # temperature
            '1.3.6.1.4.1.2011.4': 55.0,  # humidity
            '1.3.6.1.4.1.2011.5': 85.0,  # battery
            '1.3.6.1.4.1.2011.6': 350.0,  # power
            '1.3.6.1.4.1.2011.7': 45.0,  # disk_usage
            '1.3.6.1.4.1.2011.8': 1,  # device_status
            '1.3.6.1.4.1.2011.9': 25.0,  # setpoint
        }

    def _update_data(self):
        """更新所有模拟数据"""
        # CPU: 10-80%
        self.values['1.3.6.1.4.1.2011.1'] = round(10 + random.random() * 70, 1)

        # 内存: 30-85%
        self.values['1.3.6.1.4.1.2011.2'] = round(30 + random.random() * 55, 1)

        # 温度: 在设定值附近波动 ±3℃
        setpoint = self.values.get('1.3.6.1.4.1.2011.9', 25.0)
        temp = setpoint + random.uniform(-3, 3)
        self.values['1.3.6.1.4.1.2011.3'] = round(temp, 1)

        # 湿度: 40-75%
        self.values['1.3.6.1.4.1.2011.4'] = round(40 + random.random() * 35, 1)

        # 电池: 缓慢下降，低于5%重置到95%
        battery = self.values.get('1.3.6.1.4.1.2011.5', 85.0)
        battery -= random.uniform(0, 0.3)
        if battery < 5:
            battery = 95
        self.values['1.3.6.1.4.1.2011.5'] = round(battery, 1)

        # 功率: 0-1000W (10%概率为0)
        if random.random() < 0.1:
            self.values['1.3.6.1.4.1.2011.6'] = 0
        else:
            self.values['1.3.6.1.4.1.2011.6'] = round(random.random() * 1000, 1)

        # 磁盘使用率: 20-90%
        self.values['1.3.6.1.4.1.2011.7'] = round(20 + random.random() * 70, 1)

        # 设备状态: 0=离线, 1=在线, 2=故障 (98%在线)
        rand = random.random()
        if rand < 0.98:
            self.values['1.3.6.1.4.1.2011.8'] = 1
        elif rand < 0.99:
            self.values['1.3.6.1.4.1.2011.8'] = 0
        else:
            self.values['1.3.6.1.4.1.2011.8'] = 2

        # 运行时间: 持续增加
        self.values['1.3.6.1.2.1.1.3.0'] = int((time.time() - self.start_time) * 100)

    def _build_response(self, request_id, oid, value):
        """构建 SNMP 响应"""
        # OID 编码
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

        # 值编码
        if isinstance(value, float):
            value_str = str(value)
            value_bytes = value_str.encode('utf-8')
            value_asn1 = bytes([0x04]) + bytes([len(value_bytes)]) + value_bytes
        elif isinstance(value, int):
            if value < 128:
                value_asn1 = bytes([0x02, 0x01, value])
            else:
                value_asn1 = bytes([0x02]) + bytes([4]) + value.to_bytes(4, 'big')
        else:
            value_str = str(value)
            value_bytes = value_str.encode('utf-8')
            value_asn1 = bytes([0x04]) + bytes([len(value_bytes)]) + value_bytes

        # Variable binding
        binding = bytes([0x06]) + bytes([len(oid_bytes)]) + bytes(oid_bytes) + value_asn1
        binding_seq = bytes([0x30]) + bytes([len(binding)]) + binding

        # Var bindings
        var_bindings = bytes([0x30]) + bytes([len(binding_seq)]) + binding_seq

        # PDU
        pdu_body = (
                struct.pack('>I', request_id) +
                struct.pack('>I', 0) +
                struct.pack('>I', 0) +
                var_bindings
        )
        pdu = bytes([0xA2]) + bytes([len(pdu_body)]) + pdu_body

        # Version + Community + PDU
        version = bytes([0x02, 0x01, 0x01])
        comm_bytes = self.community.encode('utf-8')
        community_asn1 = bytes([0x04]) + bytes([len(comm_bytes)]) + comm_bytes

        msg_body = version + community_asn1 + pdu
        msg = bytes([0x30]) + bytes([len(msg_body)]) + msg_body

        return msg

    def _handle_request(self, data, addr):
        """处理 SNMP 请求"""
        try:
            if len(data) < 10:
                return None

            pdu_pos = data.find(b'\xA0')
            if pdu_pos == -1:
                return None

            pos = pdu_pos + 2
            request_id = struct.unpack('>I', data[pos:pos + 4])[0]
            pos += 4
            pos += 8

            oid_pos = data.find(b'\x06', pos)
            if oid_pos == -1:
                return None

            oid_len = data[oid_pos + 1]
            oid_bytes = data[oid_pos + 2:oid_pos + 2 + oid_len]

            oid_parts = []
            if oid_bytes:
                first = oid_bytes[0]
                oid_parts = [first // 40, first % 40]
                i = 1
                while i < len(oid_bytes):
                    if oid_bytes[i] < 128:
                        oid_parts.append(oid_bytes[i])
                        i += 1
                    else:
                        value = 0
                        while i < len(oid_bytes) and oid_bytes[i] >= 128:
                            value = (value << 7) | (oid_bytes[i] & 0x7F)
                            i += 1
                        if i < len(oid_bytes):
                            value = (value << 7) | oid_bytes[i]
                            i += 1
                        oid_parts.append(value)

            oid = '.'.join(str(x) for x in oid_parts)

            if oid in self.values:
                value = self.values[oid]
            else:
                value = None

            if value is not None:
                return self._build_response(request_id, oid, value)
            return None

        except Exception as e:
            return None

    def start(self):
        if self.running:
            return

        print("[SNMP Simulator] 🚀 启动...")
        print(f"[SNMP Simulator] 📡 端口: {self.port}")
        print(f"[SNMP Simulator] 🔑 Community: {self.community}")
        print("[SNMP Simulator] 💡 Ctrl+C 停止")

        self.running = True

        update_thread = threading.Thread(target=self._update_loop, daemon=True)
        update_thread.start()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

        print(f"[SNMP Simulator] ✅ 已启动，等待请求...")

        try:
            while self.running:
                try:
                    data, addr = self.sock.recvfrom(4096)
                    if len(data) == 0:
                        continue

                    response = self._handle_request(data, addr)
                    if response:
                        self.sock.sendto(response, addr)

                except socket.timeout:
                    continue
                except Exception as e:
                    pass

        except KeyboardInterrupt:
            print("\n[SNMP Simulator] 停止")
        finally:
            self.running = False
            if self.sock:
                self.sock.close()

    def _update_loop(self):
        last_print = 0
        while self.running:
            try:
                self._update_data()
                now = time.time()
                if now - last_print > 30:
                    self._print_status()
                    last_print = now
            except:
                pass
            time.sleep(2)

    def _print_status(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status_map = {0: '离线', 1: '在线', 2: '故障'}

        print(f"\n[{now}] 📊 SNMP 设备数据:")
        print("-" * 50)
        print(f"  📟 设备: {self.values.get('1.3.6.1.2.1.1.5.0', 'N/A')}")
        print(f"  💻 CPU: {self.values.get('1.3.6.1.4.1.2011.1', 0):.1f}%")
        print(f"  🧠 内存: {self.values.get('1.3.6.1.4.1.2011.2', 0):.1f}%")
        print(f"  🌡️  温度: {self.values.get('1.3.6.1.4.1.2011.3', 0):.1f}℃")
        print(f"  💧 湿度: {self.values.get('1.3.6.1.4.1.2011.4', 0):.1f}%")
        print(f"  🔋 电池: {self.values.get('1.3.6.1.4.1.2011.5', 0):.1f}%")
        print(f"  ⚡ 功率: {self.values.get('1.3.6.1.4.1.2011.6', 0):.1f}W")
        print(f"  💾 硬盘: {self.values.get('1.3.6.1.4.1.2011.7', 0):.1f}%")
        print(f"  📟 状态: {status_map.get(self.values.get('1.3.6.1.4.1.2011.8', 1), '未知')}")
        print(f"  🎯 设定值: {self.values.get('1.3.6.1.4.1.2011.9', 0):.1f}℃")
        print("-" * 50)


if __name__ == "__main__":
    sim = SnmpSimulator(port=11610)
    sim.start()