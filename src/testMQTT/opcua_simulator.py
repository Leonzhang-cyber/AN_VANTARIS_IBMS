# src/testMQTT/opcua_simulator.py

"""
OPC UA 设备模拟器
模拟一个支持 OPC UA 协议的设备，用于测试 OpcUaDriver

使用方法:
    python src/testMQTT/opcua_simulator.py

配置:
    - 默认监听端口: 4840
    - 支持用户名密码认证
    - 模拟工业传感器数据
"""

import sys
import os
import random
import time
import asyncio
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ASYNCUA_AVAILABLE = False

# 兼容不同版本的 asyncua
try:
    from asyncua import ua, Server

    ASYNCUA_AVAILABLE = True
    print("[OPC UA Simulator] ✅ asyncua 加载成功")
except ImportError as e:
    print(f"[OPC UA Simulator] ❌ asyncua 导入失败: {e}")
    print("[OPC UA Simulator] 请运行: pip install asyncua")
    sys.exit(1)


class OpcUaSimulator:
    """
    OPC UA 设备模拟器

    使用字符串 NodeId (ns=2;s=Temperature)，方便驱动配置
    """

    def __init__(self, port: int = 4840, username: str = None, password: str = None):
        self.port = port
        self.username = username
        self.password = password
        self.server = None
        self.running = False
        self.nodes = {}

        # 数据初始值
        self.values = {
            'temperature': 25.0,
            'humidity': 55.0,
            'pressure': 101.3,
            'motor_speed': 0.0,
            'motor_status': 0,
            'battery_level': 85.0,
            'power': 0.0,
            'energy': 0.0,
            'vibration': 0.5,
            'setpoint': 25.0,
            'production_count': 0,
            'alarm_status': 0,
        }

    def _update_data(self):
        """更新模拟数据"""
        setpoint = self.values.get('setpoint', 25.0)
        temp = setpoint + random.uniform(-2, 2)
        self.values['temperature'] = round(temp, 1)

        self.values['humidity'] = round(45 + random.random() * 30, 1)
        self.values['pressure'] = round(99 + random.random() * 4, 2)

        if self.values['motor_status'] == 1:
            self.values['motor_speed'] = round(500 + random.random() * 1500, 0)
            self.values['power'] = round(500 + self.values['motor_speed'] * 0.5, 0)
            self.values['energy'] += self.values['power'] * 0.0001
        else:
            self.values['motor_speed'] = 0
            self.values['power'] = 0

        battery = self.values['battery_level']
        battery = max(5, battery - random.uniform(0, 0.2))
        if battery < 5:
            battery = 95
        self.values['battery_level'] = round(battery, 1)

        self.values['vibration'] = round(0.1 + random.random() * 1.9, 2)

        if self.values['motor_status'] == 1 and random.random() < 0.1:
            self.values['production_count'] += random.randint(1, 5)

        if random.random() < 0.005:
            self.values['alarm_status'] = 1
        elif random.random() < 0.01:
            self.values['alarm_status'] = 0

    async def _create_server(self):
        """创建 OPC UA 服务器"""
        self.server = Server()
        await self.server.init()
        self.server.set_endpoint(f"opc.tcp://0.0.0.0:{self.port}")
        self.server.set_server_name("IMBS OPC UA Simulator")

        # 认证设置 (兼容不同版本)
        try:
            if hasattr(self.server, 'user_manager'):
                if self.username and self.password:
                    self.server.user_manager.set_user(self.username, self.password)
                    self.server.user_manager.allow_anonymous = False
                    print(f"[OPC UA Simulator] 🔐 启用认证: {self.username}")
                else:
                    self.server.user_manager.allow_anonymous = True
                    print("[OPC UA Simulator] 🔓 匿名访问已开启")
            else:
                print("[OPC UA Simulator] 🔓 匿名访问")
        except Exception as e:
            print(f"[OPC UA Simulator] ⚠️ 认证设置失败: {e}，使用匿名模式")

        # 创建地址空间
        objects = self.server.get_objects_node()
        uri = "http://imbs.simulator/opcua"
        idx = await self.server.register_namespace(uri)

        device_obj = await objects.add_object(idx, "IMBS_Device")
        sensor_folder = await device_obj.add_folder(idx, "Sensors")
        actuator_folder = await device_obj.add_folder(idx, "Actuators")
        status_folder = await device_obj.add_folder(idx, "Status")

        # ============================================================
        # 添加变量节点 - 使用字符串 NodeId
        # 注意：add_variable 的参数顺序是 (nodeid, name, initial_value)
        # 如果使用 idx 和 name 组合，nodeid 参数会冲突
        # 正确做法：直接构造 NodeId 作为第一个参数
        # ============================================================

        # 温度 (ns=2;s=Temperature)
        temp_node = await sensor_folder.add_variable(
            ua.NodeId("Temperature", 2),  # 直接作为第一个参数
            "Temperature",
            self.values['temperature']
        )
        await temp_node.set_writable(False)
        self.nodes['temperature'] = temp_node

        # 湿度 (ns=2;s=Humidity)
        hum_node = await sensor_folder.add_variable(
            ua.NodeId("Humidity", 2),
            "Humidity",
            self.values['humidity']
        )
        await hum_node.set_writable(False)
        self.nodes['humidity'] = hum_node

        # 压力 (ns=2;s=Pressure)
        press_node = await sensor_folder.add_variable(
            ua.NodeId("Pressure", 2),
            "Pressure",
            self.values['pressure']
        )
        await press_node.set_writable(False)
        self.nodes['pressure'] = press_node

        # 电机转速 (ns=2;s=MotorSpeed)
        speed_node = await sensor_folder.add_variable(
            ua.NodeId("MotorSpeed", 2),
            "MotorSpeed",
            self.values['motor_speed']
        )
        await speed_node.set_writable(False)
        self.nodes['motor_speed'] = speed_node

        # 电池电量 (ns=2;s=BatteryLevel)
        battery_node = await sensor_folder.add_variable(
            ua.NodeId("BatteryLevel", 2),
            "BatteryLevel",
            self.values['battery_level']
        )
        await battery_node.set_writable(False)
        self.nodes['battery_level'] = battery_node

        # 功率 (ns=2;s=Power)
        power_node = await sensor_folder.add_variable(
            ua.NodeId("Power", 2),
            "Power",
            self.values['power']
        )
        await power_node.set_writable(False)
        self.nodes['power'] = power_node

        # 累计能耗 (ns=2;s=Energy)
        energy_node = await sensor_folder.add_variable(
            ua.NodeId("Energy", 2),
            "Energy",
            self.values['energy']
        )
        await energy_node.set_writable(False)
        self.nodes['energy'] = energy_node

        # 振动值 (ns=2;s=Vibration)
        vib_node = await sensor_folder.add_variable(
            ua.NodeId("Vibration", 2),
            "Vibration",
            self.values['vibration']
        )
        await vib_node.set_writable(False)
        self.nodes['vibration'] = vib_node

        # ============================================================
        # 执行器节点 (可读写)
        # ============================================================

        # 设定值 (ns=2;s=Setpoint)
        setpoint_node = await actuator_folder.add_variable(
            ua.NodeId("Setpoint", 2),
            "Setpoint",
            self.values['setpoint']
        )
        await setpoint_node.set_writable(True)
        self.nodes['setpoint'] = setpoint_node

        # 电机控制 (ns=2;s=MotorControl)
        motor_control_node = await actuator_folder.add_variable(
            ua.NodeId("MotorControl", 2),
            "MotorControl",
            self.values['motor_status']
        )
        await motor_control_node.set_writable(True)
        self.nodes['motor_status'] = motor_control_node

        # ============================================================
        # 状态节点
        # ============================================================

        # 生产计数 (ns=2;s=ProductionCount)
        prod_node = await status_folder.add_variable(
            ua.NodeId("ProductionCount", 2),
            "ProductionCount",
            self.values['production_count']
        )
        await prod_node.set_writable(False)
        self.nodes['production_count'] = prod_node

        # 告警状态 (ns=2;s=AlarmStatus)
        alarm_node = await status_folder.add_variable(
            ua.NodeId("AlarmStatus", 2),
            "AlarmStatus",
            self.values['alarm_status']
        )
        await alarm_node.set_writable(False)
        self.nodes['alarm_status'] = alarm_node

        # 设备名称 (ns=2;s=DeviceName)
        name_node = await status_folder.add_variable(
            ua.NodeId("DeviceName", 2),
            "DeviceName",
            "IMBS-SIM-001"
        )
        await name_node.set_writable(False)
        self.nodes['device_name'] = name_node

        # 版本信息 (ns=2;s=FirmwareVersion)
        version_node = await status_folder.add_variable(
            ua.NodeId("FirmwareVersion", 2),
            "FirmwareVersion",
            "v1.0.0"
        )
        await version_node.set_writable(False)
        self.nodes['firmware_version'] = version_node

        print("[OPC UA Simulator] ✅ 地址空间创建完成")
        print(f"   - 传感器节点: 8 个 (字符串 NodeId)")
        print(f"   - 执行器节点: 2 个 (可读写)")
        print(f"   - 状态节点: 4 个")
        print(f"   - 命名空间索引: {idx}")

    async def _update_loop(self):
        """数据更新循环"""
        while self.running:
            try:
                self._update_data()

                for name, node in self.nodes.items():
                    if name in self.values:
                        try:
                            # 不覆盖用户修改的执行器节点
                            if name in ['setpoint', 'motor_status']:
                                continue
                            await node.write_value(self.values[name])
                        except Exception as e:
                            # 忽略写入错误
                            pass

                # 每30秒打印一次状态
                if int(time.time()) % 30 < 1:
                    self._print_status()

            except Exception as e:
                print(f"[OPC UA Simulator] 更新错误: {e}")

            await asyncio.sleep(1)

    def _print_status(self):
        """打印当前状态"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"\n[{now}] 📊 OPC UA 设备数据:")
        print("-" * 70)

        print(f"   🌡️ 温度: {self.values['temperature']:.1f}℃")
        print(f"   💧 湿度: {self.values['humidity']:.1f}%")
        print(f"   📊 压力: {self.values['pressure']:.2f}kPa")

        status_map = {0: '停止', 1: '运行', 2: '故障'}
        print(f"   ⚡ 电机: {status_map.get(self.values['motor_status'], '未知')}")
        print(f"   🔄 转速: {self.values['motor_speed']:.0f} RPM")
        print(f"   ⚡ 功率: {self.values['power']:.0f} W")
        print(f"   🔋 电量: {self.values['battery_level']:.1f}%")

        print(f"   📈 累计能耗: {self.values['energy']:.2f} kWh")
        print(f"   📦 生产计数: {self.values['production_count']}")
        print(f"   🔔 告警状态: {'⚠️ 告警' if self.values['alarm_status'] == 1 else '✅ 正常'}")
        print("-" * 70)

    async def start(self):
        """启动 OPC UA 服务器"""
        if self.running:
            print("[OPC UA Simulator] 模拟器已在运行")
            return

        print("[OPC UA Simulator] 🚀 启动 OPC UA 服务器...")
        print(f"[OPC UA Simulator] 📡 监听端口: {self.port}")
        print(f"[OPC UA Simulator] 🔗 连接地址: opc.tcp://localhost:{self.port}")
        print("[OPC UA Simulator] 💡 按 Ctrl+C 停止")
        print("-" * 70)

        try:
            await self._create_server()
            self.running = True

            # 启动数据更新任务
            update_task = asyncio.create_task(self._update_loop())

            # 启动服务器 - 兼容不同版本
            print("[OPC UA Simulator] ✅ 服务器已启动，等待客户端连接...")

            # 方法1: 使用 start (新版本)
            try:
                await self.server.start()
                # 保持运行
                while self.running:
                    await asyncio.sleep(1)
            except AttributeError:
                pass

            # 方法2: 使用 serve_forever (旧版本)
            try:
                if hasattr(self.server, 'serve_forever'):
                    await self.server.serve_forever()
            except AttributeError:
                pass

        except KeyboardInterrupt:
            print("\n[OPC UA Simulator] 收到停止信号")
        except Exception as e:
            print(f"[OPC UA Simulator] 服务器错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.running = False
            # 尝试停止服务器
            try:
                if hasattr(self.server, 'stop'):
                    await self.server.stop()
            except:
                pass
            print("[OPC UA Simulator] 已停止")


def main():
    """主函数"""
    if not ASYNCUA_AVAILABLE:
        print("[OPC UA Simulator] ❌ asyncua 未正确安装")
        print("[OPC UA Simulator] 请运行: pip install asyncua")
        sys.exit(1)

    import argparse

    parser = argparse.ArgumentParser(description='OPC UA 设备模拟器')
    parser.add_argument('--port', type=int, default=4840, help='服务器端口 (默认: 4840)')
    parser.add_argument('--username', type=str, default=None, help='认证用户名 (可选)')
    parser.add_argument('--password', type=str, default=None, help='认证密码 (可选)')
    args = parser.parse_args()

    simulator = OpcUaSimulator(
        port=args.port,
        username=args.username,
        password=args.password
    )

    try:
        asyncio.run(simulator.start())
    except KeyboardInterrupt:
        print("\n[OPC UA Simulator] 用户中断")
    except Exception as e:
        print(f"[OPC UA Simulator] 异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()