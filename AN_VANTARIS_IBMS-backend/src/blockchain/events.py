# src/blockchain/events.py
"""
智能合约事件查询模块

提供链上事件日志的检索功能，用于追溯合约的历史操作记录。
事件是合约执行时主动发射的“信号”，存储在区块的日志中，查询效率高且不产生 Gas 费用。

典型用途：
- 监听合约状态变更（如 ValueChanged 事件）
- 获取特定条件的业务记录（如某用户的转账历史）
- 构建链下索引数据库
"""

from typing import List, Dict, Union

from .client import BlockchainClient


class EventManager:
    """
    事件管理器

    封装 Web3.py 的事件过滤与查询功能，提供简洁的事件检索接口。
    """

    def __init__(self, client: BlockchainClient):
        """
        初始化事件管理器

        :param client: 已连接并配置好的 BlockchainClient 实例
        """
        self.client = client

    def get_events(
        self,
        contract_addr: str,
        abi: List,
        event_name: str,
        from_block: int = 0,
        to_block: Union[int, str] = 'latest',
        argument_filters: Dict = None
    ) -> List[Dict]:
        """
        查询合约的指定事件日志

        :param contract_addr:    已部署的合约地址（以 '0x' 开头）
        :param abi:              合约的 ABI 列表（用于解析事件结构）
        :param event_name:       要查询的事件名称（必须与合约中定义的一致）
        :param from_block:       起始区块号，默认为 0（创世块）
        :param to_block:         结束区块号，默认为 'latest'（最新区块）。
                                 支持传入具体数字或 'latest', 'earliest', 'pending'。
        :param argument_filters: 事件参数过滤字典，用于筛选特定值的事件。
                                 例如：{'from': '0x...'} 只匹配 from 字段为该地址的事件。
        :return:                 事件列表，每个事件为字典格式，包含：
                                 - 'args': 事件参数（字典，键名为合约中定义的参数名）
                                 - 'event': 事件名称
                                 - 'logIndex': 日志在区块中的索引
                                 - 'transactionIndex': 交易在区块中的索引
                                 - 'transactionHash': 所属交易的哈希
                                 - 'address': 合约地址
                                 - 'blockHash': 所在区块哈希
                                 - 'blockNumber': 所在区块号
        :rtype:                  List[Dict]

        示例（查询所有 ValueChanged 事件）:
            >>> events = event_manager.get_events(
            ...     contract_addr='0x257fF6Ec9b026E50AA340FDe7A607bA0C665A49b',
            ...     abi=abi,
            ...     event_name='ValueChanged',
            ...     from_block=0
            ... )
            >>> for ev in events:
            ...     print(ev['blockNumber'], ev['args']['oldValue'], '->', ev['args']['newValue'])
            1615 0 -> 42
        """
        # 创建合约实例
        contract = self.client.w3.eth.contract(address=contract_addr, abi=abi)

        # 获取指定名称的事件对象
        event = getattr(contract.events, event_name)

        # 创建事件过滤器
        # 注意：使用蛇形命名参数 from_block / to_block 以兼容 web3.py v6+
        flt = event.create_filter(
            from_block=from_block,
            to_block=to_block,
            argument_filters=argument_filters
        )

        # 获取所有匹配的事件条目
        events = flt.get_all_entries()

        # 将每个事件对象转换为字典便于使用
        return [dict(e) for e in events]