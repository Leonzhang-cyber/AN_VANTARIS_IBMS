# src/blockchain/client.py
"""
区块链客户端连接模块

负责管理与 Geth 私有链节点的连接，提供：
- 多节点自动故障转移（按配置顺序尝试连接）
- PoA 共识中间件注入
- Web3 实例的统一获取入口

使用方式：
    >>> client = BlockchainClient()
    >>> w3 = client.w3
    >>> print(client.chain_id)
"""

from typing import List, Optional

from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

from .config import NODE_URLS, CHAIN_ID
from .exceptions import ConnectionError


class BlockchainClient:
    """
    区块链客户端

    封装 Web3.py 连接逻辑，支持：
    - 从配置文件中读取多个 RPC 节点地址
    - 按顺序尝试连接，使用第一个可用的节点
    - 自动注入 PoA 中间件以兼容 Clique 共识
    - 提供 Web3 实例和链 ID 的只读属性
    """

    def __init__(self, node_urls: Optional[List[str]] = None):
        """
        初始化区块链客户端

        :param node_urls: 自定义的节点 RPC 地址列表。
                          若未提供，则使用 config.NODE_URLS 中的默认配置。
        :type node_urls: list[str], optional
        """
        # 使用传入的节点列表，若为空则回退到配置文件中的默认值
        self.node_urls = node_urls or NODE_URLS

        # Web3 实例和当前连接的节点 URL（初始为 None）
        self._w3: Optional[Web3] = None
        self._current_url: Optional[str] = None

        # 初始化时立即建立连接
        self._connect()

    def _connect(self) -> None:
        """
        私有方法：建立与节点的连接

        按 self.node_urls 的顺序遍历每个 RPC 地址，尝试创建 Web3 实例并注入 PoA 中间件。
        一旦连接成功，将 Web3 实例保存到 self._w3，记录当前 URL，并立即返回。
        若所有节点均无法连接，则抛出 ConnectionError 异常。

        :raises ConnectionError: 当所有节点都不可用时抛出
        """
        for url in self.node_urls:
            # 创建 HTTPProvider 连接的 Web3 实例
            w3 = Web3(Web3.HTTPProvider(url))

            # 注入 PoA 中间件，确保能正确处理 Clique 共识的 extraData 字段
            w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

            # 测试连接是否成功
            if w3.is_connected():
                self._w3 = w3
                self._current_url = url
                return  # 连接成功，退出循环

        # 所有节点均不可用，抛出异常
        raise ConnectionError("所有节点不可用")

    @property
    def w3(self) -> Web3:
        """
        获取当前可用的 Web3 实例

        每次访问此属性时，会先检查现有连接是否仍然有效。
        若连接已断开，则自动尝试重新连接（故障自愈）。

        :return: Web3 实例
        :rtype: Web3
        """
        if not self._w3.is_connected():
            self._connect()
        return self._w3

    @property
    def chain_id(self) -> int:
        """
        获取当前私有链的链 ID

        该值从配置文件 config.CHAIN_ID 中读取，用于构造交易时防止跨链重放攻击。

        :return: 链 ID
        :rtype: int
        """
        return CHAIN_ID