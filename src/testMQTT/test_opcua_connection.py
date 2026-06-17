# src/testMQTT/test_opcua_connect.py
"""
OPC UA 连接测试脚本
测试能否连接到模拟器
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from asyncua import Client

    print("✅ asyncua 加载成功")
except ImportError:
    print("❌ asyncua 未安装，请运行: pip install asyncua")
    sys.exit(1)


async def test_connect(url: str, max_retries: int = 3):
    """测试 OPC UA 连接"""
    print("\n" + "=" * 60)
    print(f"🔗 测试连接: {url}")
    print("=" * 60)

    for attempt in range(max_retries):
        try:
            print(f"\n📡 尝试 {attempt + 1}/{max_retries}...")
            client = Client(url=url)

            # 设置超时
            client.timeout = 5

            await client.connect()
            print(f"✅ 连接成功!")

            # 尝试读取服务器信息
            try:
                server_node = client.get_node("ns=0;i=2253")  # ServerStatus
                status = await server_node.read_value()
                print(f"📊 服务器状态: {status}")
            except Exception as e:
                print(f"⚠️ 读取服务器状态失败: {e}")

            # 尝试读取一个测试节点
            try:
                test_node = client.get_node("ns=2;i=5")  # Temperature
                temp = await test_node.read_value()
                print(f"🌡️ 温度: {temp}℃")
            except Exception as e:
                print(f"⚠️ 读取温度失败: {e}")

            await client.disconnect()
            print("✅ 断开连接")
            return True

        except asyncio.TimeoutError:
            print(f"❌ 连接超时 (尝试 {attempt + 1})")
        except Exception as e:
            print(f"❌ 连接失败: {e}")

        if attempt < max_retries - 1:
            print(f"⏳ 等待 2 秒后重试...")
            await asyncio.sleep(2)

    return False


async def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("   🔍 OPC UA 连接测试")
    print("=" * 60)

    # 测试不同的 URL
    urls = [
        "opc.tcp://localhost:4840",
        "opc.tcp://127.0.0.1:4840",
        "opc.tcp://0.0.0.0:4840",
    ]

    success = False
    for url in urls:
        print("\n" + "-" * 60)
        result = await test_connect(url)
        if result:
            print(f"\n✅ 连接成功! URL: {url}")
            print("💡 请在数据库中使用此 URL")
            success = True
            break

    if not success:
        print("\n❌ 所有 URL 都连接失败!")
        print("\n请检查:")
        print("  1. 模拟器是否在运行: python src/testMQTT/opcua_simulator.py")
        print("  2. 端口是否被占用: netstat -an | findstr 4840")
        print("  3. 防火墙是否允许端口 4840")


if __name__ == "__main__":
    asyncio.run(main())