# src/blockchain/contract.py
"""
智能合约管理模块

提供智能合约的部署、调用（读/写）功能，封装了 Web3.py 合约交互的常用操作。

主要功能：
- 部署新合约到区块链
- 调用合约的只读函数（免费、即时返回）
- 调用合约的写函数（发送交易，修改链上状态）

使用前需准备好合约的 ABI 和字节码（可通过 solcx 编译 Solidity 源码获得）。
"""

import time
from typing import List, Optional, Any, Dict

from .client import BlockchainClient
from .config import DEFAULT_GAS_PRICE, NODE_URLS


class ContractManager:
    """
    智能合约管理器

    依赖 BlockchainClient 提供的 Web3 连接实例，封装了合约部署和函数调用逻辑。
    写操作通过全局挖矿调度器管理挖矿启停。
    """

    def __init__(self, client: BlockchainClient):
        """
        初始化合约管理器

        :param client: 已连接并配置好的 BlockchainClient 实例
        """
        self.client = client
        self.scheduler = None  # 由 Blockchain 注入

    def set_scheduler(self, scheduler):
        """注入全局挖矿调度器"""
        self.scheduler = scheduler

    def _ensure_mining(self):
        """确保挖矿已启动（委托给调度器）"""
        if self.scheduler is None:
            # 降级：如果没有调度器，则不做任何操作（或可记录警告）
            return

        def start_func():
            """调度器回调：实际启动挖矿"""
            print("⛏️ [Contract] 正在启动所有节点挖矿...")
            for url in NODE_URLS:
                try:
                    w3_temp = self.client.w3.__class__(self.client.w3.provider.__class__(url))
                    w3_temp.provider.make_request('miner_start', [])
                except Exception as e:
                    print(f"⚠️ 节点 {url} 启动失败: {e}")

            # 等待出块就绪
            start_block = self.client.w3.eth.block_number
            waited = 0
            while self.client.w3.eth.block_number == start_block and waited < 15:
                time.sleep(1)
                waited += 1
            if self.client.w3.eth.block_number == start_block:
                raise Exception("挖矿启动超时，未能在15秒内产生新区块")
            print(f"✅ [Contract] 挖矿已就绪，当前高度: {self.client.w3.eth.block_number}")

        self.scheduler.start(start_func)

    def deploy(
            self,
            from_addr: str,
            abi: List,
            bytecode: str,
            constructor_args: Optional[List] = None,
            gas: int = 3000000,
            timeout: int = 60
    ) -> Dict:
        """
        部署一个新的智能合约到区块链上（通过调度器自动管理挖矿）
        """
        # --- 确保挖矿已启动 ---
        self._ensure_mining()

        # --- 执行部署 ---
        contract = self.client.w3.eth.contract(abi=abi, bytecode=bytecode)

        if constructor_args:
            constructor = contract.constructor(*constructor_args)
        else:
            constructor = contract.constructor()

        tx_hash = constructor.transact({
            'from': from_addr,
            'gas': gas,
            'gasPrice': DEFAULT_GAS_PRICE
        })

        # 等待交易被打包
        receipt = self.client.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)

        return {
            'tx_hash': tx_hash.hex(),
            'contract_address': receipt['contractAddress']
        }

    def call(
            self,
            contract_addr: str,
            abi: List,
            func_name: str,
            args: Optional[List] = None,
            from_addr: Optional[str] = None,
            is_view: bool = False,
            gas: int = 200000,
            timeout: int = 60
    ) -> Any:
        """
        调用合约函数（写操作通过调度器自动管理挖矿）
        """
        contract = self.client.w3.eth.contract(address=contract_addr, abi=abi)

        if args:
            func = getattr(contract.functions, func_name)(*args)
        else:
            func = getattr(contract.functions, func_name)()

        # 只读函数：直接调用，不需要挖矿
        if is_view:
            return func.call()

        # --- 写函数：确保挖矿已启动 ---
        self._ensure_mining()

        # 构建并发送交易
        tx = func.build_transaction({
            'from': from_addr,
            'gas': gas,
            'gasPrice': DEFAULT_GAS_PRICE,
            'chainId': self.client.chain_id,
            'nonce': self.client.w3.eth.get_transaction_count(from_addr, block_identifier='pending')
        })

        tx_hash = self.client.w3.eth.send_transaction(tx)

        # 等待收据，确保交易被确认
        receipt = self.client.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)

        return {'tx_hash': tx_hash.hex(), 'receipt': dict(receipt)}