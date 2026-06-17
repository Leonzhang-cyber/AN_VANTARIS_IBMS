# src/blockchain/transaction.py
"""
交易管理模块

提供交易构建、发送及收据查询功能，支持：
- 普通 ETH 转账
- 附带文本数据的存证交易（数据上链）
- 自动估算 Gas 限额（含 20% 缓冲）
- 可选的交易确认等待机制
- 通过全局挖矿调度器实现智能启停（首次请求启动，空闲10分钟自动停止）

费用说明：
    所有交易的 gasPrice 由 config.DEFAULT_GAS_PRICE 控制（当前为 0），
    因此在私有链中发送交易完全免费，不会消耗账户 ETH。
"""
import time
from typing import Union, Dict, Any, Optional

from .client import BlockchainClient
from .config import DEFAULT_GAS_PRICE, DEFAULT_GAS_LIMIT


class TransactionManager:
    """
    交易管理器

    封装了 Web3.py 的交易发送逻辑，简化了私有链中的数据上链操作。
    主要功能：
        - send(): 发送交易（转账或附带数据），通过调度器管理挖矿
        - get_receipt(): 查询已发送交易的状态和结果
    """

    def __init__(self, client: BlockchainClient):
        """
        初始化交易管理器

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
            # 降级：如果没有调度器，则不做任何操作（或者可以抛出警告）
            return

        def start_func():
            """调度器回调：实际启动挖矿"""
            from .config import NODE_URLS
            print("⛏️ [Transaction] 正在启动所有节点挖矿...")
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
            print(f"✅ [Transaction] 挖矿已就绪，当前高度: {self.client.w3.eth.block_number}")

        self.scheduler.start(start_func)

    def send(
            self,
            from_addr: str,
            to_addr: str,
            value_ether: float = 0,
            data: Union[str, bytes] = "",
            wait: bool = True,
            gas: Optional[int] = None,
            timeout: int = 30
    ) -> Dict[str, Any]:
        """
        发送一笔交易到私有链，自动通过调度器管理挖矿。

        该方法是数据上链的核心入口，适用于以下场景：
            - 向其他账户转账（设置 value_ether > 0）
            - 在链上永久存储一段文本（设置 data 参数）
            - 同时转账并存证（value_ether 和 data 均设置）

        :param from_addr:    发送方账户地址（必须是节点已解锁的账户）
        :param to_addr:      接收方账户地址（存证场景可设为发送方自己的地址）
        :param value_ether:  转账金额（单位：ETH），默认 0 表示不转账
        :param data:         附带数据，可以是普通字符串（自动转十六进制）或已编码的十六进制字符串。
        :param wait:         是否等待交易被打包确认。默认 True，返回结果中会包含交易收据。
        :param gas:          手动指定的 Gas 限额。若为 None（默认），则自动调用节点估算并上浮 20%。
        :param timeout:      等待交易确认的超时秒数，默认 30。
        :return:             包含 'tx_hash' 和（若 wait=True）'receipt' 的字典
        """
        # ====== 确保挖矿已启动（由调度器管理） ======
        self._ensure_mining()

        # ====== 构建并发送交易 ======
        # 1. 处理附带数据
        if isinstance(data, str) and not data.startswith('0x'):
            data = '0x' + data.encode('utf-8').hex()

        # 2. 构建交易字典
        tx = {
            'from': from_addr,
            'to': to_addr,
            'value': self.client.w3.to_wei(value_ether, 'ether'),
            'gasPrice': DEFAULT_GAS_PRICE,
            'nonce': self.client.w3.eth.get_transaction_count(from_addr, block_identifier='pending'),
            'data': data,
            'chainId': self.client.chain_id
        }

        # 3. 处理 Gas 限额
        if gas is None:
            try:
                estimated = self.client.w3.eth.estimate_gas(tx)
                gas = int(estimated * 1.2)
            except Exception:
                gas = 100000
        tx['gas'] = gas

        # 4. 发送交易
        tx_hash = self.client.w3.eth.send_transaction(tx)
        result = {'tx_hash': tx_hash.hex()}
        print(f"📤 交易已提交: {tx_hash.hex()}")

        # ====== 等待交易确认 ======
        if wait:
            try:
                receipt = self.client.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
                result['receipt'] = dict(receipt)
            except Exception as e:
                # 确认失败只记录，不停止挖矿（由调度器自行管理）
                raise Exception(f"交易确认失败: {e}")

        return result

    def get_receipt(self, tx_hash: str) -> dict:
        """
        根据交易哈希获取交易收据

        交易收据包含交易的最终执行结果，是验证链上操作是否成功的重要凭证。

        :param tx_hash: 交易哈希（由 send() 返回的十六进制字符串）
        :return:        收据字典，关键字段包括：
                            - 'status': 1 表示成功，0 表示失败（revert）
                            - 'blockNumber': 交易被打包的区块号
                            - 'gasUsed': 实际消耗的 Gas 数量
                            - 'logs': 合约事件日志列表
                            - 'transactionHash': 交易哈希
        :rtype:         dict
        """
        return dict(self.client.w3.eth.get_transaction_receipt(tx_hash))