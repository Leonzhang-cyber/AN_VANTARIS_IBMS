# src/blockchain/client.py
from typing import List, Optional

from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from .config import NODE_URLS, CHAIN_ID
from .exceptions import ConnectionError

class BlockchainClient:
    def __init__(self, node_urls: Optional[List[str]] = None):
        self.node_urls = node_urls or NODE_URLS
        self._w3: Optional[Web3] = None
        self._current_url: Optional[str] = None
        self._connect()

    def _connect(self):
        for url in self.node_urls:
            w3 = Web3(Web3.HTTPProvider(url))
            w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
            if w3.is_connected():
                self._w3 = w3
                self._current_url = url
                return
        raise ConnectionError("所有节点不可用")

    @property
    def w3(self) -> Web3:
        if not self._w3.is_connected():
            self._connect()
        return self._w3

    @property
    def chain_id(self) -> int:
        return CHAIN_ID