# src/Iot/drivers/isup_driver.py
"""
海康 ISUP/Ehome 协议驱动
用于4G摄像头、跨公网设备接入
支持：设备注册、心跳保活、告警接收、命令下发
"""

import socket
import struct
import threading
import json
import time
import base64
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from src.Iot.drivers.base_driver import BaseProtocolDriver
from src.Iot.exceptions import ProtocolError

logger = logging.getLogger(__name__)

# ========== ISUP 协议常量 ==========
ISUP_MAGIC = b'ISUP'
ISUP_VERSION = 1
DEFAULT_ISUP_PORT = 7660


# ========== ISUP 驱动主类 ==========
class ISUPDriver(BaseProtocolDriver):
    """
    海康 ISUP/Ehome 协议驱动

    工作模式：
    1. 服务端模式：启动 TCP 服务端，等待设备主动注册
    2. 设备连接后自动维持心跳，接收数据上报和告警
    3. 支持通过设备连接下发命令
    """

    def __init__(self):
        super().__init__("isup")

        # 设备管理
        self.devices: Dict[str, Dict] = {}  # {device_did: {client, info, config, ...}}
        self.device_id_to_did: Dict[str, str] = {}  # {device_serial: device_did}

        # 服务端
        self.server: Optional[socket.socket] = None
        self.running: bool = False
        self.port: int = DEFAULT_ISUP_PORT

        # 锁
        self._lock = threading.Lock()

        # 心跳管理
        self._heartbeat_threads: Dict[str, threading.Thread] = {}
        self._heartbeat_running: Dict[str, bool] = {}

    # ==================== 基类必须实现的方法 ====================

    def connect(self, device_did: str, config: Dict[str, Any]) -> bool:
        """
        注册 ISUP 设备（被动接入模式）
        实际连接由设备主动发起，此方法仅记录配置并启动服务端
        """
        device_serial = config.get('device_serial', '')  # 设备序列号，用于匹配
        device_code = config.get('device_code', device_did[:20])

        with self._lock:
            self.devices[device_did] = {
                'config': config,
                'device_serial': device_serial,
                'device_code': device_code,
                'status': 'pending',  # pending/online/offline
                'client': None,
                'addr': None,
                'info': {},
                'last_heartbeat': None,
                'connected_at': None
            }

            if device_serial:
                self.device_id_to_did[device_serial] = device_did

        self._on_status(device_did, 'online')
        print(f"[ISUP] 设备（等待连接）")
        logger.info(f"[ISUP] 设备已注册（等待连接）: {device_did} (serial: {device_serial})")

        # 如果服务未启动，自动启动
        if not self.running:
            port = config.get('port', DEFAULT_ISUP_PORT)
            self.start_server(port)

        return True

    def disconnect(self, device_did: str) -> bool:
        """断开设备连接"""
        with self._lock:
            if device_did not in self.devices:
                return False

            device = self.devices[device_did]

            # 停止心跳
            self._stop_heartbeat(device_did)

            # 关闭连接
            try:
                if device.get('client'):
                    device['client'].close()
            except:
                pass

            # 清理映射
            device_serial = device.get('device_serial', '')
            if device_serial and device_serial in self.device_id_to_did:
                del self.device_id_to_did[device_serial]

            del self.devices[device_did]
            self._on_status(device_did, 'offline')
            logger.info(f"[ISUP] 设备已断开: {device_did}")

        return True

    def send_command(self, device_did: str, command: Dict[str, Any]) -> Dict[str, Any]:
        """下发命令到 ISUP 设备"""
        with self._lock:
            device = self.devices.get(device_did)
            if not device:
                raise ProtocolError(f"设备未注册: {device_did}")

            if device.get('status') != 'online':
                raise ProtocolError(f"设备不在线: {device_did}")

            client = device.get('client')
            if not client:
                raise ProtocolError(f"设备连接已断开: {device_did}")

            device_serial = device.get('device_serial', '')

        method = command.get('method', '')
        params = command.get('params', {})

        # 构建 ISUP 命令包
        packet = self._build_command_packet(device_serial, method, params)

        try:
            client.send(packet)
            logger.info(f"[ISUP] 命令已下发: {device_did} -> {method}")

            # 如果是 PTZ 控制，记录日志
            if method == 'ptz':
                action = params.get('action', 'unknown')
                logger.info(f"[ISUP] PTZ 控制: {action}")

            return {
                'success': True,
                'method': method,
                'device_did': device_did,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            raise ProtocolError(f"命令下发失败: {e}")

    def subscribe(self, device_did: str, topics: Optional[list] = None):
        """
        订阅设备数据（ISUP 由设备主动上报，无需订阅）
        """
        logger.debug(f"[ISUP] 设备已就绪: {device_did}")
        pass

    # ==================== 服务端管理 ====================

    def start_server(self, port: int = DEFAULT_ISUP_PORT) -> bool:
        """启动 ISUP 服务端"""
        if self.running:
            logger.warning("[ISUP] 服务已在运行")
            return True

        self.port = port
        self.running = True

        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind(('0.0.0.0', port))
            self.server.listen(100)
            logger.info(f"[ISUP] 服务已启动，监听端口: {port}")

            thread = threading.Thread(target=self._accept_loop, daemon=True)
            thread.start()
            return True

        except Exception as e:
            logger.error(f"[ISUP] 启动服务失败: {e}")
            self.running = False
            return False

    def stop_server(self):
        """停止 ISUP 服务"""
        self.running = False

        # 停止所有心跳
        for device_did in list(self.devices.keys()):
            self._stop_heartbeat(device_did)

        # 关闭所有连接
        for device_did in list(self.devices.keys()):
            try:
                device = self.devices[device_did]
                if device.get('client'):
                    device['client'].close()
            except:
                pass

        if self.server:
            try:
                self.server.close()
            except:
                pass
            self.server = None

        logger.info("[ISUP] 服务已停止")

    # ==================== 内部连接处理 ====================

    def _accept_loop(self):
        """接受客户端连接循环"""
        while self.running:
            try:
                client, addr = self.server.accept()
                # 🆕 添加醒目日志
                print(f"\n{'=' * 50}")
                print(f"🔌 [ISUP] 新设备连接: {addr[0]}:{addr[1]}")
                print(f"{'=' * 50}\n")
                logger.info(f"[ISUP] 新连接来自: {addr[0]}:{addr[1]}")

                thread = threading.Thread(
                    target=self._handle_client,
                    args=(client, addr),
                    daemon=True
                )
                thread.start()
            except socket.error:
                if self.running:
                    logger.error("[ISUP] 接受连接失败")
                break
            except Exception as e:
                logger.error(f"[ISUP] 连接循环异常: {e}")

    def _handle_client(self, client: socket.socket, addr: tuple):
        """处理单个设备连接"""
        device_did = None
        device_serial = None

        # 设置超时
        client.settimeout(60)

        while self.running:
            try:
                data = client.recv(65536)
                if not data:
                    break

                # 解析 ISUP 协议包
                result = self._parse_packet(data)

                if result:
                    packet_type = result.get('type')
                    payload = result.get('payload', {})
                    serial = result.get('device_serial', '')

                    if packet_type == 'register':
                        # 处理注册
                        device_serial = serial
                        device_did = self.device_id_to_did.get(device_serial)

                        if device_did:
                            with self._lock:
                                if device_did in self.devices:
                                    self.devices[device_did]['client'] = client
                                    self.devices[device_did]['status'] = 'online'
                                    self.devices[device_did]['addr'] = addr
                                    self.devices[device_did]['info'] = payload
                                    self.devices[device_did]['connected_at'] = datetime.now().isoformat()
                                    self.devices[device_did]['device_serial'] = device_serial

                            # 启动心跳
                            self._start_heartbeat(device_did, client)

                            self._on_status(device_did, 'online')
                            logger.info(f"[ISUP] 设备上线: {device_did} (serial: {device_serial})")

                            # 发送注册响应
                            self._send_response(client, 0x0001, device_serial, 0)
                        else:
                            logger.warning(f"[ISUP] 未知设备注册: {device_serial}")
                            self._send_response(client, 0x0001, device_serial, 2)  # 设备不存在

                    elif packet_type == 'heartbeat':
                        # 处理心跳
                        if device_did:
                            with self._lock:
                                if device_did in self.devices:
                                    self.devices[device_did]['last_heartbeat'] = datetime.now().isoformat()
                            # 回复心跳响应
                            self._send_response(client, 0x0003, device_serial, 0)
                            logger.debug(f"[ISUP] 心跳来自: {device_did}")

                    elif packet_type == 'data':
                        # 处理数据上报
                        if device_did:
                            self._handle_data_report(device_did, payload)

                    elif packet_type == 'alarm':
                        # 处理告警
                        if device_did:
                            self._handle_alarm(device_did, payload)

                    elif packet_type == 'status':
                        # 处理状态上报
                        if device_did:
                            self._handle_status_report(device_did, payload)

                    elif packet_type == 'unregister':
                        # 处理注销
                        logger.info(f"[ISUP] 设备注销: {device_did or device_serial}")
                        if device_did:
                            self.disconnect(device_did)
                        break

                    elif packet_type == 'response':
                        # 处理命令响应
                        if device_did:
                            self._handle_command_response(device_did, payload)

            except socket.timeout:
                # 超时检查心跳
                if device_did and device_did in self.devices:
                    last_heartbeat = self.devices[device_did].get('last_heartbeat')
                    if last_heartbeat:
                        last_time = datetime.fromisoformat(last_heartbeat)
                        if (datetime.now() - last_time).seconds > 90:
                            logger.warning(f"[ISUP] 心跳超时: {device_did}")
                            self.disconnect(device_did)
                            break
                continue
            except ConnectionResetError:
                logger.warning(f"[ISUP] 设备连接重置: {device_did or addr}")
                break
            except Exception as e:
                logger.error(f"[ISUP] 处理设备数据异常: {e}")
                break

        # 清理连接
        if device_did and device_did in self.devices:
            self._on_status(device_did, 'offline')
            logger.info(f"[ISUP] 设备下线: {device_did}")

        try:
            client.close()
        except:
            pass

    # ==================== 心跳管理 ====================

    def _start_heartbeat(self, device_did: str, client: socket.socket):
        """启动心跳维护线程"""
        self._stop_heartbeat(device_did)

        self._heartbeat_running[device_did] = True

        def heartbeat_loop():
            while self._heartbeat_running.get(device_did, False):
                try:
                    # 发送心跳请求
                    packet = self._build_heartbeat_request()
                    client.send(packet)
                    time.sleep(30)  # 30秒心跳间隔
                except Exception as e:
                    logger.error(f"[ISUP] 心跳发送失败: {e}")
                    self._heartbeat_running[device_did] = False
                    break

        thread = threading.Thread(target=heartbeat_loop, daemon=True)
        thread.start()
        self._heartbeat_threads[device_did] = thread

    def _stop_heartbeat(self, device_did: str):
        """停止心跳"""
        self._heartbeat_running[device_did] = False
        if device_did in self._heartbeat_threads:
            self._heartbeat_threads[device_did].join(timeout=2)
            del self._heartbeat_threads[device_did]
        if device_did in self._heartbeat_running:
            del self._heartbeat_running[device_did]

    # ==================== 协议包解析和构建 ====================

    def _parse_packet(self, data: bytes) -> Optional[Dict]:
        """
        解析 ISUP 协议包

        ISUP 协议包结构（示例）：
        [魔数 4B][版本 2B][命令 2B][序列号 2B][设备ID长度 1B][设备ID N B][状态 2B][体长 4B][消息体 N B]
        """
        if len(data) < 20:
            return None

        # 检查魔数
        if data[0:4] != ISUP_MAGIC:
            return None

        try:
            version = struct.unpack('>H', data[4:6])[0]
            command = struct.unpack('>H', data[6:8])[0]
            sequence = struct.unpack('>H', data[8:10])[0]
            device_id_len = data[10]

            if device_id_len > 0:
                device_serial = data[11:11 + device_id_len].decode('utf-8', errors='ignore')
            else:
                device_serial = ''

            offset = 11 + device_id_len
            status = struct.unpack('>H', data[offset:offset + 2])[0]
            body_len = struct.unpack('>I', data[offset + 2:offset + 6])[0]

            body = data[offset + 6:offset + 6 + body_len] if body_len > 0 else b''

            # 🆕 添加调试日志
            if command == 0x0005 and body_len > 0:
                logger.info(f"[ISUP] 收到数据包: command=0x{command:04x}, body_len={body_len}")
                try:
                    body_str = body.decode('utf-8')
                    logger.info(f"[ISUP] body 内容: {body_str[:200]}...")
                except:
                    logger.info(f"[ISUP] body (hex): {body.hex()[:200]}...")

            # 解析消息体（JSON 格式）
            payload = {}
            if body_len > 0:
                try:
                    payload = json.loads(body.decode('utf-8'))
                    logger.info(f"[ISUP] JSON 解析成功: keys={list(payload.keys())}")
                except Exception as e:
                    logger.error(f"[ISUP] JSON 解析失败: {e}")
                    # 尝试作为二进制数据处理
                    payload = {
                        'binary': base64.b64encode(body).decode('utf-8'),
                        'length': body_len
                    }

            # 命令类型映射
            command_map = {
                0x0001: 'register',
                0x0002: 'unregister',
                0x0003: 'heartbeat',
                0x0004: 'keepalive',
                0x0005: 'data',
                0x0006: 'status',
                0x0007: 'alarm',
                0x0008: 'control',
                0x8000: 'response',
            }

            return {
                'type': command_map.get(command, f'unknown_{command:04x}'),
                'command': command,
                'sequence': sequence,
                'device_serial': device_serial,
                'status': status,
                'payload': payload,
                'raw_body': body
            }

        except Exception as e:
            logger.error(f"[ISUP] 解析数据包失败: {e}")
            return None

    def _build_packet(self, command: int, device_serial: str, body: bytes = b'', sequence: int = 0) -> bytes:
        """构建 ISUP 协议包"""
        device_bytes = device_serial.encode('utf-8')
        device_len = len(device_bytes)

        header = (
                ISUP_MAGIC +
                struct.pack('>H', ISUP_VERSION) +
                struct.pack('>H', command) +
                struct.pack('>H', sequence) +
                struct.pack('B', device_len) +
                device_bytes +
                struct.pack('>H', 0) +  # 状态码
                struct.pack('>I', len(body))
        )
        return header + body

    def _build_command_packet(self, device_serial: str, method: str, params: Dict) -> bytes:
        """构建命令包"""
        sequence = int(time.time() * 1000) % 65535

        command_body = json.dumps({
            'method': method,
            'params': params,
            'timestamp': datetime.now().isoformat()
        }).encode('utf-8')

        return self._build_packet(0x0008, device_serial, command_body, sequence)

    def _build_heartbeat_request(self) -> bytes:
        """构建心跳请求"""
        return self._build_packet(0x0003, '', b'')

    def _send_response(self, client: socket.socket, command: int, device_serial: str, status: int):
        """发送响应"""
        body = json.dumps({'status': status}).encode('utf-8')
        packet = self._build_packet(0x8000 | command, device_serial, body)
        try:
            client.send(packet)
        except:
            pass

    # ==================== 消息处理器 ====================

    def _handle_data_report(self, device_did: str, payload: Dict):
        """处理数据上报"""
        # 打印 payload 内容用于调试
        logger.info(f"[ISUP] _handle_data_report: device_did={device_did}, payload_keys={list(payload.keys())}")

        # 尝试获取实际数据
        actual_payload = payload.get('data', payload)

        # 获取 type
        data_type = payload.get('type') or actual_payload.get('type')
        logger.info(f"[ISUP] data_type: {data_type}")

        # 如果是音视频数据，推送到 SSE
        if data_type == 'video':
            from src.api.iot.sse_api import push_to_device

            # 获取图片数据
            image_data = payload.get('image') or actual_payload.get('image', '')
            img_format = payload.get('format') or actual_payload.get('format', 'jpeg')

            logger.info(f"[ISUP] 视频帧: device_did={device_did}, image_size={len(image_data)}")

            # 推送到 SSE
            push_to_device(device_did, {
                'type': 'video_frame',
                'device_did': device_did,
                'timestamp': datetime.now().isoformat(),
                'image': image_data,
                'format': img_format
            })

            # 🆕 调用基类回调，传入实际数据
            self._on_data(device_did, {
                'type': 'video_frame',
                'payload': actual_payload,  # 传入实际数据
                'timestamp': datetime.now().isoformat()
            })
        else:
            # 普通数据
            self._on_data(device_did, {
                'type': 'data',
                'payload': payload,
                'timestamp': datetime.now().isoformat()
            })

        logger.debug(f"[ISUP] 数据上报: {device_did}")

    def _handle_alarm(self, device_did: str, payload: Dict):
        """处理告警"""
        alarm_type = payload.get('alarm_type', 'unknown')
        alarm_level = payload.get('level', 'info')

        # 推送到 SSE
        from src.api.iot.sse_api import push_to_device
        push_to_device(device_did, {
            'type': 'alarm',
            'device_did': device_did,
            'alarm_type': alarm_type,
            'level': alarm_level,
            'message': payload.get('message', ''),
            'timestamp': datetime.now().isoformat()
        })

        # 调用基类的数据回调
        self._on_data(device_did, {
            'type': 'alarm',
            'alarm_type': alarm_type,
            'level': alarm_level,
            'payload': payload,
            'timestamp': datetime.now().isoformat()
        })

        logger.warning(f"[ISUP] 设备告警: {device_did} -> {alarm_type}")

    def _handle_status_report(self, device_did: str, payload: Dict):
        """处理状态上报"""
        status = payload.get('status', 'unknown')

        self._on_data(device_did, {
            'type': 'status',
            'status': status,
            'payload': payload,
            'timestamp': datetime.now().isoformat()
        })

        logger.info(f"[ISUP] 设备状态: {device_did} -> {status}")

    def _handle_command_response(self, device_did: str, payload: Dict):
        """处理命令响应"""
        command = payload.get('command', 'unknown')
        result = payload.get('result', 'success')

        self._on_data(device_did, {
            'type': 'command_response',
            'command': command,
            'result': result,
            'payload': payload,
            'timestamp': datetime.now().isoformat()
        })

        logger.info(f"[ISUP] 命令响应: {device_did} -> {command} = {result}")

    # ==================== 资源管理 ====================

    def __del__(self):
        """清理资源"""
        self.stop_server()