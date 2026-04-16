# src/blockchain/transaction.py
"""
交易管理模块

提供交易构建、发送及收据查询功能，支持：
- 普通 ETH 转账
- 附带文本数据的存证交易（数据上链）
- 自动估算 Gas 限额（含 20% 缓冲）
- 可选的交易确认等待机制

费用说明：
    所有交易的 gasPrice 由 config.DEFAULT_GAS_PRICE 控制（当前为 0），
    因此在私有链中发送交易完全免费，不会消耗账户 ETH。
"""

from typing import Union, Dict, Any, Optional

from .client import BlockchainClient
from .config import DEFAULT_GAS_PRICE, DEFAULT_GAS_LIMIT  # 从配置读取 Gas 价格和限额


class TransactionManager:
    """
    交易管理器

    封装了 Web3.py 的交易发送逻辑，简化了私有链中的数据上链操作。
    主要功能：
        - send(): 发送交易（转账或附带数据）
        - get_receipt(): 查询已发送交易的状态和结果
    """

    def __init__(self, client: BlockchainClient):
        """
        初始化交易管理器

        :param client: 已连接并配置好的 BlockchainClient 实例
        """
        self.client = client

    def send(
            self,
            from_addr: str,
            to_addr: str,
            value_ether: float = 0,
            data: Union[str, bytes] = "",
            wait: bool = True,
            gas: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        发送一笔交易到私有链

        该方法是数据上链的核心入口，适用于以下场景：
            - 向其他账户转账（设置 value_ether > 0）
            - 在链上永久存储一段文本（设置 data 参数）
            - 同时转账并存证（value_ether 和 data 均设置）

        :param from_addr:    发送方账户地址（必须是节点已解锁的账户）
        :param to_addr:      接收方账户地址（存证场景可设为发送方自己的地址）
        :param value_ether:  转账金额（单位：ETH），默认 0 表示不转账
        :param data:         附带数据，可以是普通字符串（自动转十六进制）或已编码的十六进制字符串。
                             最大长度受区块 Gas 限制，建议不超过 100KB。
        :param wait:         是否等待交易被打包确认。默认 True，返回结果中会包含交易收据。
        :param gas:          手动指定的 Gas 限额。若为 None（默认），则自动调用节点估算并上浮 20%。
        :return:             包含以下字段的字典：
                                 - 'tx_hash': 交易哈希（链上数据的唯一凭证，务必保存）
                                 - 'receipt': 交易收据（仅当 wait=True 时存在），包含状态、区块号、Gas 消耗等
        :rtype:              Dict[str, Any]

        使用示例：
            >>> result = tx_manager.send(
            ...     from_addr='0x9AA128582b17C0c0143690F24012C8DBCf24767f',
            ...     to_addr='0x9AA128582b17C0c0143690F24012C8DBCf24767f',
            ...     data='IMBS合同存证：合同号CT001'
            ... )
            >>> print(result['tx_hash'])
            0x7f2302cc4167d2b9e8650afb57a024926cf751affee54845bacde250fe2fbcd2
            >>> print(result['receipt']['blockNumber'])
            1655
        """
        # 1. 处理附带数据：将普通字符串转换为十六进制格式
        if isinstance(data, str) and not data.startswith('0x'):
            data = '0x' + data.encode('utf-8').hex()

        # 2. 构建交易字典
        tx = {
            'from': from_addr,
            'to': to_addr,
            'value': self.client.w3.to_wei(value_ether, 'ether'),  # ETH 转 wei（1e18 倍）
            'gasPrice': DEFAULT_GAS_PRICE,  # 费用单价（当前为 0，交易免费）
            'nonce': self.client.w3.eth.get_transaction_count(from_addr),  # 发送方已发交易计数
            'data': data,                  # 附带数据（空则为 '0x'）
            'chainId': self.client.chain_id  # 链 ID，防止跨链重放
        }

        # 3. 处理 Gas 限额
        #    Gas 限额是计算资源上限，不是费用！
        #    真实费用 = gasPrice × 实际消耗的 gas（其中 gasPrice = 0）
        if gas is None:
            try:
                # 调用节点 RPC 估算该交易所需 Gas
                estimated = self.client.w3.eth.estimate_gas(tx)
                # 增加 20% 缓冲，防止因链上状态变化导致 Gas 不足而交易失败
                gas = int(estimated * 1.2)
            except Exception:
                # 估算失败（如合约 revert），使用一个较大的安全值
                # 在私有链中即使设高也不产生费用，但过高可能浪费区块容量
                gas = 100000
        tx['gas'] = gas

        # 4. 发送交易（此时交易进入节点的 txpool，等待出块节点打包）
        tx_hash = self.client.w3.eth.send_transaction(tx)
        result = {'tx_hash': tx_hash.hex()}

        # 5. 等待交易确认（可选）
        if wait:
            # 阻塞直到交易被打包进区块（默认超时 120 秒）
            receipt = self.client.w3.eth.wait_for_transaction_receipt(tx_hash)
            result['receipt'] = dict(receipt)

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

        使用示例：
            >>> receipt = tx_manager.get_receipt('0x7f2302cc...')
            >>> if receipt['status'] == 1:
            ...     print(f"交易成功，区块号 {receipt['blockNumber']}")
        """
        return dict(self.client.w3.eth.get_transaction_receipt(tx_hash))