# src/testMQTT/modbus_simulator.py

"""
Modbus 设备模拟器 - 适配 pymodbus 2.5.3
模拟一个支持 Modbus TCP 协议的设备，用于测试 ModbusDriver

使用方法:
    python src/testMQTT/modbus_simulator.py

配置:
    - 默认监听端口: 5020 (避免与真实Modbus设备冲突)
    - 模拟从站ID: 1
"""

import sys
import os
import random
import time
import threading
from datetime import datetime
from typing import Dict, Any

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

POMODBUS_AVAILABLE = False

# ============================================================
# 导入 pymodbus 2.5.3 (使用 sync 模块)
# ============================================================
try:
    from pymodbus.server.sync import StartTcpServer
    from pymodbus.device import ModbusDeviceIdentification
    from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext

    POMODBUS_AVAILABLE = True
    print("[Modbus Simulator] ✅ pymodbus 2.5.3 加载成功")
except ImportError as e:
    print(f"[Modbus Simulator] ❌ pymodbus 导入失败: {e}")
    print(f"[Modbus Simulator] 当前 Python: {sys.executable}")
    print("[Modbus Simulator] 请运行: pip install pymodbus==2.5.3")
    sys.exit(1)


class ModbusSimulator:
    """
    Modbus 设备模拟器

    模拟的数据字段:
    - temperature: 温度 (地址0, 缩放0.1)
    - humidity: 湿度 (地址1, 缩放0.1)
    - pressure: 大气压力 (地址2, 缩放0.01)
    - co2: 二氧化碳浓度 (地址3)
    - pm25: PM2.5 (地址4, 缩放0.1)
    - pm10: PM10 (地址5, 缩放0.1)
    - voc: 挥发性有机物 (地址6, 缩放0.01)
    - noise: 噪音 (地址7, 缩放0.1)
    - light: 光照强度 (地址8)
    - voltage: 电压 (地址9, 缩放0.1)
    - current: 电流 (地址10, 缩放0.01)
    - power: 功率 (地址11)
    - battery: 电池电量 (地址12, 缩放0.1)
    - fan_speed: 风速 (地址13)
    - mode: 运行模式 (地址14)
    - status: 设备状态 (地址15)
    - set_temperature: 设定温度 (地址16, 缩放0.1)
    """

    # 寄存器配置: (地址, 默认值, 最小值, 最大值, 缩放)
    REGISTERS = {
        'temperature': (0, 25.0, -40.0, 100.0, 10),
        'humidity': (1, 60.0, 0.0, 100.0, 10),
        'pressure': (2, 101.3, 80.0, 110.0, 100),
        'co2': (3, 450.0, 300.0, 5000.0, 1),
        'pm25': (4, 35.0, 0.0, 500.0, 10),
        'pm10': (5, 50.0, 0.0, 600.0, 10),
        'voc': (6, 2.0, 0.0, 100.0, 100),
        'noise': (7, 45.0, 30.0, 120.0, 10),
        'light': (8, 500.0, 0.0, 100000.0, 1),
        'voltage': (9, 220.0, 0.0, 400.0, 10),
        'current': (10, 5.0, 0.0, 100.0, 100),
        'power': (11, 1000.0, 0.0, 10000.0, 1),
        'battery': (12, 85.0, 0.0, 100.0, 10),
        'fan_speed': (13, 0, 0, 3, 1),
        'mode': (14, 0, 0, 4, 1),
        'status': (15, 0, 0, 3, 1),
        'set_temperature': (16, 24.0, 16.0, 30.0, 10),
    }

    ENUM_MAPS = {
        'fan_speed': {0: 'low', 1: 'medium', 2: 'high', 3: 'auto'},
        'mode': {0: 'cool', 1: 'heat', 2: 'fan', 3: 'auto', 4: 'off'},
        'status': {0: 'online', 1: 'offline', 2: 'error', 3: 'maintenance'},
    }

    def __init__(self, slave_id: int = 1, port: int = 5020):
        self.slave_id = slave_id
        self.port = port
        self.running = False
        self._init_data_blocks()

    def _init_data_blocks(self):
        """初始化数据块 (100个寄存器)"""
        # 初始化寄存器数据
        self.hr_data = [0] * 100
        self.co_data = [0] * 100

        # 初始化寄存器值
        for name, (address, default, min_val, max_val, scale) in self.REGISTERS.items():
            self.hr_data[address] = int(default * scale)

    def _get_value(self, name: str) -> float:
        """获取寄存器值（转换为实际值）"""
        address, default, min_val, max_val, scale = self.REGISTERS[name]
        raw = self.hr_data[address]
        return raw / scale

    def _set_value(self, name: str, value: float):
        """设置寄存器值（存储为原始值）"""
        address, default, min_val, max_val, scale = self.REGISTERS[name]
        value = max(min_val, min(max_val, value))
        self.hr_data[address] = int(round(value * scale))

    def update_data(self):
        """更新模拟数据"""
        set_temp = self._get_value('set_temperature')
        temp = set_temp + random.uniform(-2, 2)
        temp = max(self.REGISTERS['temperature'][2], min(self.REGISTERS['temperature'][3], temp))
        self._set_value('temperature', temp)

        self._set_value('humidity', 45 + random.random() * 30)
        self._set_value('pressure', 99 + random.random() * 4)
        self._set_value('co2', 400 + random.random() * 800)
        self._set_value('pm25', 10 + random.random() * 90)
        self._set_value('pm10', 20 + random.random() * 130)
        self._set_value('voc', 0.5 + random.random() * 9.5)
        self._set_value('noise', 35 + random.random() * 40)
        self._set_value('light', 100 + random.random() * 1900)
        self._set_value('voltage', 210 + random.random() * 20)
        self._set_value('current', 2 + random.random() * 18)
        self._set_value('power', 200 + random.random() * 2800)

        battery = self._get_value('battery')
        battery = max(5, battery - random.uniform(0, 0.5))
        if battery < 5:
            battery = 95
        self._set_value('battery', battery)

        self._set_value('fan_speed', random.randint(0, 3))
        if random.random() < 0.01:
            self._set_value('mode', random.randint(0, 4))

        status = 0
        if random.random() < 0.002:
            status = 2
        self._set_value('status', status)

    def get_current_data(self) -> Dict[str, Any]:
        """获取当前所有数据"""
        data = {}
        for name in self.REGISTERS:
            value = self._get_value(name)
            if name in self.ENUM_MAPS:
                data[name] = {
                    'value': int(value),
                    'display': self.ENUM_MAPS[name].get(int(value), str(int(value)))
                }
            else:
                data[name] = value
        return data

    def start(self):
        """启动Modbus服务器"""
        if self.running:
            print("[Modbus Simulator] 模拟器已在运行")
            return

        print(f"[Modbus Simulator] 🚀 启动 Modbus TCP 服务器...")
        print(f"[Modbus Simulator] 📡 监听端口: {self.port}")
        print(f"[Modbus Simulator] 🆔 从站ID: {self.slave_id}")
        print(f"[Modbus Simulator] 💡 按 Ctrl+C 停止")
        print("-" * 60)

        self.running = True

        # 启动数据更新线程
        update_thread = threading.Thread(target=self._update_loop, daemon=True)
        update_thread.start()

        # 启动 Modbus 服务器
        try:
            self._start_server()
        except KeyboardInterrupt:
            print("\n[Modbus Simulator] 收到停止信号")
        except Exception as e:
            print(f"[Modbus Simulator] 服务器错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.running = False
            print("[Modbus Simulator] 已停止")

    def _start_server(self):
        """启动服务器 - 使用 ModbusSequentialDataBlock"""
        # 创建设备标识
        identity = ModbusDeviceIdentification()
        identity.VendorName = 'IMBS Simulator'
        identity.ProductCode = 'IMBS'
        identity.VendorUrl = 'http://github.com/IMBS'
        identity.ProductName = 'Modbus Simulator Device'
        identity.ModelName = 'IMBS-SIM-001'
        identity.MajorMinorRevision = '1.0'

        # 创建数据块 - 使用 ModbusSequentialDataBlock
        # 注意: 每个数据块需要指定起始地址和数据列表
        di_block = ModbusSequentialDataBlock(0, self.hr_data[:])
        co_block = ModbusSequentialDataBlock(0, self.co_data[:])
        hr_block = ModbusSequentialDataBlock(0, self.hr_data[:])
        ir_block = ModbusSequentialDataBlock(0, self.hr_data[:])

        # 创建从站上下文
        slave_context = ModbusSlaveContext(
            di=di_block,
            co=co_block,
            hr=hr_block,
            ir=ir_block
        )

        context = ModbusServerContext(slaves=slave_context, single=True)

        # 启动服务器
        StartTcpServer(
            context=context,
            identity=identity,
            address=("0.0.0.0", self.port)
        )

    def _update_loop(self):
        """数据更新循环"""
        while self.running:
            try:
                self.update_data()
                if int(time.time()) % 30 < 1:
                    self._print_current_data()
            except Exception as e:
                print(f"[Modbus Simulator] 更新数据错误: {e}")
            time.sleep(1)

    def _print_current_data(self):
        """打印当前数据"""
        data = self.get_current_data()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"\n[{now}] 📊 Modbus 设备数据:")
        print("-" * 70)

        env_data = ['temperature', 'humidity', 'pressure', 'co2', 'pm25', 'pm10', 'voc', 'noise', 'light']
        env_str = " | ".join(
            [f"{k}={data.get(k, 'N/A'):.1f}" for k in env_data if k in data and not isinstance(data.get(k), dict)])
        if env_str:
            print(f"  环境参数: {env_str}")

        elec_data = ['voltage', 'current', 'power']
        elec_str = " | ".join(
            [f"{k}={data.get(k, 'N/A'):.1f}" for k in elec_data if k in data and not isinstance(data.get(k), dict)])
        if elec_str:
            print(f"  电气参数: {elec_str}")

        status_data = ['battery', 'status', 'mode', 'fan_speed']
        status_str = " | ".join([
            f"{k}={data.get(k, {}).get('display', data.get(k, 'N/A'))}"
            if isinstance(data.get(k), dict) else f"{k}={data.get(k, 'N/A')}"
            for k in status_data if k in data
        ])
        if status_str:
            print(f"  状态参数: {status_str}")

        print("-" * 70)


def main():
    """主函数"""
    if not POMODBUS_AVAILABLE:
        print("[Modbus Simulator] ❌ pymodbus 未正确安装")
        print("[Modbus Simulator] 请运行: pip install pymodbus==2.5.3")
        sys.exit(1)

    simulator = ModbusSimulator(slave_id=1, port=5020)

    try:
        simulator.start()
    except KeyboardInterrupt:
        print("\n[Modbus Simulator] 用户中断")
    except Exception as e:
        print(f"[Modbus Simulator] 异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()