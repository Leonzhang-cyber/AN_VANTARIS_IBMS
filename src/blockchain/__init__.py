# src/blockchain/__init__.py
from .client import BlockchainClient
from .account import AccountManager
from .transaction import TransactionManager
from .contract import ContractManager
from .events import EventManager

class Blockchain:
    def __init__(self, node_urls=None):
        self.client = BlockchainClient(node_urls)
        self.account = AccountManager(self.client)
        self.tx = TransactionManager(self.client)
        self.contract = ContractManager(self.client)
        self.events = EventManager(self.client)