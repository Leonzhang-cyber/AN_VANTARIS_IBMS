# src/Iot/drivers/mqtt_driver.py - 修改 send_command 方法

import paho.mqtt.client as mqtt
import json
from typing import Dict, Any, Optional
from datetime import datetime

from src.Iot.drivers.base_driver import BaseProtocolDriver
from src.Iot.exceptions import ProtocolError


class MQTTDriver(BaseProtocolDriver):
    """MQTT协议驱动"""

    def __init__(self):
        super().__init__("mqtt")
        self.clients: Dict[str, mqtt.Client] = {}
        self.device_brokers: Dict[str, str] = {}
        self.device_configs: Dict[str, Dict] = {}

    def connect(self, device_did: str, config: Dict[str, Any]) -> bool:
        """连接MQTT设备"""
        try:
            broker = config.get('broker')
            port = config.get('port', 1883)
            broker_key = f"{broker}:{port}"

            if broker_key not in self.clients:
                client = self._create_client(broker_key)
                self._connect_client(client, broker, port, config)
                self.clients[broker_key] = client

            self.device_brokers[device_did] = broker_key
            self.device_configs[device_did] = config

            # 订阅设备 topics
            self.subscribe(device_did, config.get('subscribe_topics'))

            # 触发上线状态
            self._on_status(device_did, 'online')

            return True

        except Exception as e:
            self._on_status(device_did, 'error')
            raise ProtocolError(f"MQTT连接失败: {str(e)}")

    def _create_client(self, client_id: str) -> mqtt.Client:
        try:
            client = mqtt.Client(client_id=client_id, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        except (AttributeError, TypeError):
            client = mqtt.Client(client_id=client_id)

        client.on_connect = self._on_connect
        client.on_message = self._on_message
        client.on_disconnect = self._on_disconnect
        return client

    def _connect_client(self, client: mqtt.Client, broker: str, port: int, config: dict):
        username = config.get('username')
        password = config.get('password')

        if username and password:
            client.username_pw_set(username, password)

        client.connect(broker, port, 60)
        client.loop_start()

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            print(f"[MQTT] Connected to broker")
        else:
            print(f"[MQTT] Connection failed with code {rc}")

    def _on_disconnect(self, client, userdata, rc, properties=None):
        print(f"[MQTT] Disconnected, code {rc}")
        if rc != 0:
            client.reconnect()

    def _on_message(self, client, userdata, msg):

        print(f"📨 [MQTT] 收到消息: {msg.topic}")  # 添加这行

        topic = msg.topic
        payload = msg.payload.decode('utf-8')

        try:
            data = json.loads(payload) if payload else {}
        except:
            data = {"raw_payload": payload}

        for device_did, config in self.device_configs.items():
            subscribe_topics = config.get('subscribe_topics', [])
            for sub_topic in subscribe_topics:
                pattern = sub_topic.replace('{device_id}', device_did)
                if self._topic_matches(topic, pattern):
                    self._on_data(device_did, {
                        'topic': topic,
                        'payload': data,
                        'qos': msg.qos,
                        'timestamp': datetime.now().isoformat()
                    })
                    return

    def _topic_matches(self, topic: str, pattern: str) -> bool:
        try:
            return mqtt.topic_matches_sub(pattern, topic)
        except:
            return topic == pattern

    def disconnect(self, device_did: str) -> bool:
        if device_did not in self.device_brokers:
            return False

        broker_key = self.device_brokers[device_did]
        client = self.clients.get(broker_key)

        if client:
            config = self.device_configs.get(device_did, {})
            for topic in config.get('subscribe_topics', []):
                actual_topic = topic.replace('{device_id}', device_did)
                client.unsubscribe(actual_topic)

        del self.device_brokers[device_did]
        del self.device_configs[device_did]

        if not any(bk == broker_key for bk in self.device_brokers.values()):
            if client:
                client.loop_stop()
                client.disconnect()
            del self.clients[broker_key]

        self._on_status(device_did, 'offline')
        return True

    # ========== 重点修改：send_command 方法 ==========
    def send_command(self, device_did: str, command: Dict[str, Any]) -> Dict[str, Any]:
        """下发命令 - 使用标准方法验证和映射"""
        if device_did not in self.device_brokers:
            raise ProtocolError(f"设备未连接: {device_did}")

        broker_key = self.device_brokers[device_did]
        client = self.clients.get(broker_key)

        if not client:
            raise ProtocolError("MQTT客户端未就绪")

        method = command.get('method')
        params = command.get('params', {})

        # 1. 验证标准方法是否存在
        from src.Iot.dao import StandardMethodDAO
        standard_method = StandardMethodDAO.get_by_code(method)
        if not standard_method:
            raise ProtocolError(f"未知的标准方法: {method}")

        # 2. 验证参数（根据 params_schema）
        if standard_method.params_schema:
            import json as json_module
            schema = standard_method.params_schema
            if isinstance(schema, str):
                schema = json_module.loads(schema)
            required = schema.get('required', [])
            for req in required:
                if req not in params:
                    raise ProtocolError(f"缺少必要参数: {req}")

        # 3. 获取方法映射
        from src.Iot.dao import MethodMappingDAO
        from src.Iot.dao import DeviceDAO

        method_mapping = MethodMappingDAO.get_mapping_by_standard(
            device_did, 'mqtt', 'downlink', method
        )

        if not method_mapping:
            raise ProtocolError(f"设备未配置方法映射: {method}")

        # 4. 获取设备编号
        device_info = DeviceDAO.get_device_by_did(device_did)
        device_code = device_info.device_code if device_info else device_did

        # 5. 构建命令 topic（包含设备号）
        command_topic = method_mapping.raw_path
        command_topic = command_topic.replace('{device_id}', device_did)
        command_topic = command_topic.replace('{device_code}', device_code)

        # 如果 raw_path 是 "building/hvac/command" 且没有占位符，自动添加设备号
        if '{device_id}' not in method_mapping.raw_path and '{device_code}' not in method_mapping.raw_path:
            if command_topic.endswith('/command'):
                base_path = command_topic.replace('/command', '')
                command_topic = f"{base_path}/{device_code}/command"
            else:
                command_topic = f"{command_topic}/{device_code}"

        # 6. 构建命令 payload
        extra = method_mapping.extra or {}
        param_name = extra.get('param', method)

        # 根据方法构建 payload
        if method == 'set_temperature':
            payload_data = {'command': 'set_setpoint', 'value': params.get('value')}
        elif method == 'set_damper':
            payload_data = {'command': 'set_damper', 'value': params.get('value')}
        elif method == 'get_status':
            payload_data = {'command': 'get_status'}
        else:
            payload_data = {param_name: params.get('value', params)}

        payload = json.dumps(payload_data)

        print(f"[MQTT] 下发命令: method={method}, topic={command_topic}, payload={payload}")

        result = client.publish(command_topic, payload, qos=1)

        return {
            'success': result.rc == mqtt.MQTT_ERR_SUCCESS,
            'method': method,
            'topic': command_topic,
            'payload': payload,
            'timestamp': datetime.now().isoformat()
        }

    # ========== send_command 方法结束 ==========

    def subscribe(self, device_did: str, topics: Optional[list] = None):
        if device_did not in self.device_brokers:
            raise ProtocolError(f"设备未连接: {device_did}")

        broker_key = self.device_brokers[device_did]
        client = self.clients.get(broker_key)

        if not client:
            raise ProtocolError("MQTT客户端未就绪")

        config = self.device_configs.get(device_did, {})
        topics_to_sub = topics if topics else config.get('subscribe_topics', [])

        for topic in topics_to_sub:
            actual_topic = topic.replace('{device_id}', device_did)
            client.subscribe(actual_topic)