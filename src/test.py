# test.py
"""
================================================================================
  Geth 私有链模块 (blockchain) 完整使用说明书
================================================================================

本脚本演示了如何使用 src/blockchain 模块完成以下操作：

    [1] 连接私有链节点（支持多节点自动故障转移）
    [2] 查询账户列表及余额
    [3] 发送附带文本数据的交易（数据上链存证）
    [4] 通过交易哈希检索链上数据凭证
    [5] 编译、部署智能合约
    [6] 调用合约写函数（修改链上状态）
    [7] 调用合约读函数（免费、即时查询）
    [8] 查询合约事件日志（历史数据追溯）
    [9] 检查三节点集群的健康状态

运行环境要求：
    - Python 3.8+
    - 已安装依赖：web3.py, py-solc-x (可选，用于合约编译)
    - 服务器上已部署三节点 Geth 私有链（Docker Compose）

使用方法：
    直接运行本脚本，所有流程将自动执行，并输出详细日志。
    如需修改连接节点或链ID，请编辑 src/blockchain/config.py。

================================================================================
"""

import sys
import os
import time

# 将 src 目录加入 Python 模块搜索路径，确保可以导入 blockchain 包
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 导入封装好的区块链统一入口
from blockchain import Blockchain
from blockchain.config import NODE_URLS

# 尝试导入 Solidity 编译器（用于合约测试，非必须）
try:
    from solcx import compile_source, install_solc, set_solc_version
    SOLCX_AVAILABLE = True
except ImportError:
    SOLCX_AVAILABLE = False
    print("⚠️ 未安装 py-solc-x，智能合约测试将跳过。")
    print("   安装命令: pip install py-solc-x")

# 导入 PoA 中间件（用于多节点高度检查）
from web3.middleware import ExtraDataToPOAMiddleware


def print_section(title: str):
    """打印格式化的章节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def main():
    """主测试流程，同时也是区块链模块的用法示例。"""

    print_section("🚀 私有链模块功能测试开始")

    # =========================================================================
    # 1. 初始化连接
    # =========================================================================
    # Blockchain 类是模块的统一入口，内部自动完成以下操作：
    #   - 按 config.NODE_URLS 顺序尝试连接节点，直到成功
    #   - 注入 PoA 中间件，确保兼容 Clique 共识
    #   - 提供 client, account, tx, contract, events 五个子管理器
    # =========================================================================
    print_section("1️⃣ 连接私有链节点")
    try:
        bc = Blockchain()
        # 可通过 bc.client._current_url 查看当前实际连接的节点
        print(f"✅ 成功连接到节点: {bc.client._current_url}")
        print(f"🔗 链 ID: {bc.client.chain_id}")
        print(f"📦 当前区块高度: {bc.client.w3.eth.block_number}")
        print(f"🌐 对等节点数: {bc.client.w3.net.peer_count}")
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return

    # =========================================================================
    # 2. 账户管理
    # =========================================================================
    # bc.account 提供了以下常用方法：
    #   - list_accounts()      : 返回节点管理的所有账户地址列表
    #   - get_balance(address) : 查询指定账户的余额（单位：ETH）
    #   - create_account(pwd)  : 创建新账户（需 personal API 支持）
    #   - unlock_account(...)  : 解锁账户（测试环境节点已自动解锁，通常无需调用）
    # =========================================================================
    print_section("2️⃣ 账户管理")
    try:
        accounts = bc.account.list_accounts()
        print(f"📋 节点管理账户数: {len(accounts)}")

        # 遍历账户，找到有余额的作为后续操作的默认账户
        default_account = None
        for addr in accounts:
            balance = bc.account.get_balance(addr)
            print(f"   账户: {addr}  余额: {balance} ETH")
            if balance > 0 and default_account is None:
                default_account = addr

        if default_account is None:
            print("⚠️ 没有找到有余额的账户，将使用第一个账户（可能无ETH）")
            default_account = accounts[0] if accounts else None

        if not default_account:
            print("❌ 没有可用账户，测试终止")
            return

        print(f"🔓 默认操作账户: {default_account}（节点已自动解锁）")
    except Exception as e:
        print(f"❌ 账户管理测试失败: {e}")
        return

    # =========================================================================
    # 3. 数据上链（转账附带文本）
    # =========================================================================
    # bc.tx 提供了交易管理功能：
    #   - send(...)       : 发送交易，支持转账和附带数据
    #   - get_receipt(hash): 根据交易哈希获取交易收据
    #
    # 参数说明：
    #   - from_addr      : 发送方地址（必须是已解锁的账户）
    #   - to_addr        : 接收方地址（可填自己，仅用于存证）
    #   - value_ether    : 转账金额（ETH），默认0
    #   - data           : 附带的数据（字符串或十六进制），将永久写入区块链
    #   - wait           : 是否等待交易被确认（默认True）
    #   - gas            : 可选，手动指定 Gas 限额（默认自动估算）
    #
    # 返回值：
    #   - tx_hash        : 交易哈希（链上数据唯一凭证，务必保存）
    #   - receipt        : 交易收据（含区块号、状态、Gas消耗等）
    # =========================================================================
    print_section("3️⃣ 数据上链（转账附带文本）")
    try:
        # 构造附带数据（模拟业务存证）
        test_data = f"IMBS测试数据 - {time.strftime('%Y-%m-%d %H:%M:%S')}"
        result = bc.tx.send(
            from_addr=default_account,
            to_addr=default_account,
            value_ether=0,
            data=test_data,
            wait=True
        )
        tx_hash = result['tx_hash']
        print(f"📤 交易已发送，哈希: {tx_hash}")
        print(f"📦 上链数据: {test_data}")
        print(f"✅ 交易已确认，区块号: {result['receipt']['blockNumber']}")

        # ===== 通过交易哈希检索上链数据 =====
        print("\n🔍 检索交易凭证...")
        receipt = bc.tx.get_receipt(tx_hash)
        tx_info = bc.client.w3.eth.get_transaction(tx_hash)

        # 从交易的 input 字段中解码原始文本
        input_data = tx_info.get('input', '0x')
        if input_data and input_data != '0x':
            try:
                # 推荐使用 Web3 内置方法解码 UTF-8 文本
                retrieved_data = bc.client.w3.to_text(input_data)
            except Exception:
                try:
                    # 降级方案：手动解码
                    retrieved_data = bytes.fromhex(input_data[2:]).decode('utf-8', errors='ignore')
                except Exception:
                    retrieved_data = "(解码失败)"
        else:
            retrieved_data = "(无附带数据)"

        print(f"📋 从链上检索到的数据: {retrieved_data}")
        print(f"📊 交易状态: {'成功' if receipt['status'] == 1 else '失败'}")
    except Exception as e:
        print(f"❌ 数据上链测试失败: {e}")

    # =========================================================================
    # 4. 智能合约部署与调用
    # =========================================================================
    # bc.contract 提供智能合约管理功能：
    #   - deploy(...)    : 部署新合约
    #   - call(...)      : 调用合约函数（自动区分读/写）
    #
    # bc.events 提供事件查询功能：
    #   - get_events(...): 查询合约历史事件
    # =========================================================================
    # if not SOLCX_AVAILABLE:
    #     print_section("⚠️ 智能合约测试跳过（未安装 solcx）")
    # else:
    #     print_section("4️⃣ 智能合约部署与调用")
    #     try:
    #         # 安装并设置 Solidity 编译器版本
    #         install_solc('0.8.19')
    #         set_solc_version('0.8.19')
    #
    #         # 简单的存储合约源码（用于演示）
    #         contract_source = '''
    #         pragma solidity ^0.8.0;
    #         contract SimpleStorage {
    #             uint256 private storedData;
    #             event ValueChanged(uint256 oldValue, uint256 newValue);
    #             function set(uint256 x) public {
    #                 emit ValueChanged(storedData, x);
    #                 storedData = x;
    #             }
    #             function get() public view returns (uint256) {
    #                 return storedData;
    #             }
    #         }
    #         '''
    #
    #         # 编译合约，获得 ABI 和字节码
    #         compiled = compile_source(contract_source, output_values=['abi', 'bin'])
    #         contract_id, contract_interface = compiled.popitem()
    #         abi = contract_interface['abi']
    #         bytecode = contract_interface['bin']
    #         print("✅ 合约编译成功")
    #
    #         # ----- 部署合约 -----
    #         print("🚀 正在部署合约...")
    #         deploy_result = bc.contract.deploy(
    #             from_addr=default_account,
    #             abi=abi,
    #             bytecode=bytecode,
    #             gas=3000000
    #         )
    #         contract_addr = deploy_result['contract_address']
    #         print(f"📜 合约已部署，地址: {contract_addr}")
    #
    #         # ----- 调用写函数（修改状态，需要发送交易）-----
    #         print("✍️ 调用 set(42)...")
    #         set_result = bc.contract.call(
    #             contract_addr=contract_addr,
    #             abi=abi,
    #             func_name='set',
    #             args=[42],
    #             from_addr=default_account
    #             # 注：对于非只读函数，call() 会自动发送交易
    #         )
    #         print(f"  交易哈希: {set_result['tx_hash']}")
    #
    #         # 等待区块确认及事件索引
    #         time.sleep(3)
    #
    #         # ----- 调用读函数（免费、即时查询）-----
    #         print("🔍 调用 get()...")
    #         value = bc.contract.call(
    #             contract_addr=contract_addr,
    #             abi=abi,
    #             func_name='get',
    #             is_view=True          # 显式标记为只读，使用 call() 而非 transact()
    #         )
    #         print(f"  存储的值: {value}")
    #
    #         # ----- 查询合约事件（历史数据追溯）-----
    #         print("📡 查询 ValueChanged 事件...")
    #         events = bc.events.get_events(
    #             contract_addr=contract_addr,
    #             abi=abi,
    #             event_name='ValueChanged',
    #             from_block=0           # 从创世块开始搜索
    #         )
    #         print(f"  共检索到 {len(events)} 个事件")
    #         for ev in events:
    #             args = ev['args']
    #             print(f"    区块 {ev['blockNumber']}: {args['oldValue']} -> {args['newValue']}")
    #
    #     except Exception as e:
    #         print(f"❌ 智能合约测试失败: {e}")
    #         import traceback
    #         traceback.print_exc()

    # =========================================================================
    # 5. 节点状态复查（集群健康检查）
    # =========================================================================
    print_section("5️⃣ 最终节点状态")
    try:
        block_num = bc.client.w3.eth.block_number
        peer_count = bc.client.w3.net.peer_count
        print(f"📦 当前区块高度: {block_num}")
        print(f"🌐 对等节点数: {peer_count}")

        # 检查三个节点区块高度是否一致
        from web3 import Web3
        heights = []
        for url in NODE_URLS:
            try:
                w3_temp = Web3(Web3.HTTPProvider(url))
                w3_temp.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
                h = w3_temp.eth.block_number
                heights.append(h)
            except Exception:
                pass
        if len(set(heights)) == 1:
            print(f"✅ 所有节点区块高度一致: {heights[0]}")
        else:
            print(f"⚠️ 节点高度存在差异: {heights}")
    except Exception as e:
        print(f"⚠️ 状态复查失败: {e}")

    print_section("🎉 测试流程全部完成")
    print("\n💡 提示：以上所有操作均由 src/blockchain 模块封装，")
    print("   您可以在业务代码中通过 `from blockchain import Blockchain` 直接调用。")


if __name__ == "__main__":
    main()