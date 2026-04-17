# src/blockchain/__init__.py
"""
IMBS 区块链模块 - Geth 私有链统一入口

本模块封装了与私有链交互的所有功能，提供以下核心管理器：

    - BlockchainClient : 节点连接与故障转移
    - AccountManager  : 账户管理（余额查询、创建账户、解锁）
    - TransactionManager : 交易发送（转账、数据上链）
    - ContractManager  : 智能合约部署与调用
    - EventManager     : 合约事件查询（历史追溯）

通过 Blockchain 统一入口类，您可以一站式完成所有链上操作。
"""

from .client import BlockchainClient
from .account import AccountManager
from .transaction import TransactionManager
from .contract import ContractManager
from .events import EventManager
from .mining_controller import MiningScheduler
from .config import NODE_URLS


class Blockchain:
    """
    私有链操作统一入口类

    初始化时会自动按配置文件中的节点列表尝试连接，连接成功后提供以下管理器：

    - client   : 底层 Web3 连接管理
    - account  : 账户相关操作
    - tx       : 交易发送与凭证查询
    - contract : 合约部署与函数调用
    - events   : 事件查询（历史数据溯源）

    使用示例:
        >>> bc = Blockchain()                     # 自动连接配置中的节点
        >>> accounts = bc.account.list_accounts() # 获取所有账户
        >>> bc.tx.send(from_addr, to_addr, 0.1)   # 转账 0.1 ETH
        >>> bc.contract.deploy(abi, bytecode)     # 部署合约
        >>> bc.events.get_events(...)             # 查询事件

    :param node_urls: 自定义节点 RPC 地址列表，若不提供则使用 config.NODE_URLS
    :type node_urls: list[str], optional
    """

    def __init__(self, node_urls=None):
        # 底层客户端（负责连接管理、Web3 实例提供）
        self.client = BlockchainClient(node_urls)

        # 账户管理器
        self.account = AccountManager(self.client)

        # 交易管理器
        self.tx = TransactionManager(self.client)

        # 合约管理器
        self.contract = ContractManager(self.client)

        # 事件管理器
        self.events = EventManager(self.client)

        # 全局挖矿调度器（单例，空闲10分钟自动停止）
        self.scheduler = MiningScheduler(NODE_URLS, idle_timeout=600)

        # 将调度器注入到需要按需挖矿的管理器中
        self.tx.set_scheduler(self.scheduler)
        self.contract.set_scheduler(self.scheduler)


# ================================================================================
# 各管理器常用方法速查
# ================================================================================
#
# 【1】client (BlockchainClient) —— 底层连接
#   - w3 : Web3 实例属性
#   - chain_id : 链 ID 属性
#   - _current_url : 当前连接的节点 URL
#
# 【2】account (AccountManager) —— 账户管理
#   - list_accounts() -> list[str]
#         获取节点管理的所有账户地址
#   - get_balance(address, unit='ether') -> float
#         查询指定账户的 ETH 余额
#   - create_account(password='') -> str
#         创建新账户，返回地址
#   - unlock_account(address, password='', duration=0) -> bool
#         解锁账户（测试环境节点通常已自动解锁，一般无需调用）
#
# 【3】tx (TransactionManager) —— 交易发送
#   - send(from_addr, to_addr, value_ether=0, data='', wait=True, gas=None) -> dict
#         发送交易，支持转账和附带文本数据。
#         返回 {'tx_hash': '0x...', 'receipt': {...}}（若 wait=True）
#   - get_receipt(tx_hash) -> dict
#         根据交易哈希获取收据（包含状态、Gas 消耗、事件日志）
#
# 【4】contract (ContractManager) —— 智能合约
#   - deploy(from_addr, abi, bytecode, constructor_args=None, gas=3000000) -> dict
#         部署新合约，返回 {'tx_hash': '0x...', 'contract_address': '0x...'}
#   - call(contract_addr, abi, func_name, args=None, from_addr=None, is_view=False) -> Any
#         调用合约函数：
#           - 若 is_view=True：只读调用，返回合约返回值
#           - 若 is_view=False：发送交易，返回 {'tx_hash': '0x...'}
#
# 【5】events (EventManager) —— 事件查询
#   - get_events(contract_addr, abi, event_name, from_block=0, to_block='latest', argument_filters=None) -> list[dict]
#         查询指定合约的历史事件，返回事件字典列表（按区块顺序）。
#         每个事件包含 'args', 'blockNumber', 'transactionHash' 等字段。
#
# ================================================================================
# 快速上手示例
# ================================================================================
#
# from blockchain import Blockchain
#
# # 1. 初始化
# bc = Blockchain()
#
# # 2. 查看账户
# accounts = bc.account.list_accounts()
# balance = bc.account.get_balance(accounts[0])
# print(f"主账户 {accounts[0]} 余额: {balance} ETH")
#
# # 3. 数据上链
# result = bc.tx.send(accounts[0], accounts[0], data="IMBS存证数据")
# print(f"交易哈希: {result['tx_hash']}")
#
# # 4. 部署合约（需要先编译得到 ABI 和 bytecode）
# deploy_res = bc.contract.deploy(accounts[0], abi, bytecode)
# contract_addr = deploy_res['contract_address']
#
# # 5. 调用合约
# bc.contract.call(contract_addr, abi, 'set', args=[42], from_addr=accounts[0])
# value = bc.contract.call(contract_addr, abi, 'get', is_view=True)
# print(f"合约返回值: {value}")
#
# # 6. 查询历史事件
# events = bc.events.get_events(contract_addr, abi, 'ValueChanged', from_block=0)
# for ev in events:
#     print(f"区块 {ev['blockNumber']}: {ev['args']}")
#