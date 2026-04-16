# src/blockchain/transaction.py
from typing import Union, Dict, Any
from .client import BlockchainClient
from .config import DEFAULT_GAS_PRICE, DEFAULT_GAS_LIMIT

class TransactionManager:
    def __init__(self, client: BlockchainClient):
        self.client = client

    def send(self, from_addr: str, to_addr: str, value_ether: float = 0,
             data: Union[str, bytes] = "", wait: bool = True) -> Dict[str, Any]:
        if isinstance(data, str) and not data.startswith('0x'):
            data = '0x' + data.encode('utf-8').hex()

        tx = {
            'from': from_addr,
            'to': to_addr,
            'value': self.client.w3.to_wei(value_ether, 'ether'),
            'gas': DEFAULT_GAS_LIMIT,
            'gasPrice': DEFAULT_GAS_PRICE,
            'nonce': self.client.w3.eth.get_transaction_count(from_addr),
            'data': data,
            'chainId': self.client.chain_id
        }
        tx_hash = self.client.w3.eth.send_transaction(tx)
        result = {'tx_hash': tx_hash.hex()}
        if wait:
            receipt = self.client.w3.eth.wait_for_transaction_receipt(tx_hash)
            result['receipt'] = dict(receipt)
        return result

    def get_receipt(self, tx_hash: str) -> dict:
        return dict(self.client.w3.eth.get_transaction_receipt(tx_hash))