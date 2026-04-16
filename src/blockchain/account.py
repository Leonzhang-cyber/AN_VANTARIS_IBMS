# src/blockchain/account.py
from .client import BlockchainClient

class AccountManager:
    def __init__(self, client: BlockchainClient):
        self.client = client

    def list_accounts(self) -> list:
        return self.client.w3.eth.accounts

    def get_balance(self, address: str, unit: str = 'ether') -> float:
        wei = self.client.w3.eth.get_balance(address)
        return float(self.client.w3.from_wei(wei, unit))

    def create_account(self, password: str = "") -> str:
        return self.client.w3.geth.personal.new_account(password)

    def unlock_account(self, address: str, password: str = "", duration: int = 0) -> bool:
        return self.client.w3.geth.personal.unlock_account(address, password, duration)