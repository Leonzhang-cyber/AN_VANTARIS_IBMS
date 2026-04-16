# src/blockchain/contract.py
from typing import List, Optional, Any, Dict
from .client import BlockchainClient
from .config import DEFAULT_GAS_PRICE

class ContractManager:
    def __init__(self, client: BlockchainClient):
        self.client = client

    def deploy(self, from_addr: str, abi: List, bytecode: str,
               constructor_args: List = None, gas: int = 3000000) -> Dict:
        contract = self.client.w3.eth.contract(abi=abi, bytecode=bytecode)
        constructor = contract.constructor(*constructor_args) if constructor_args else contract.constructor()
        tx_hash = constructor.transact({'from': from_addr, 'gas': gas, 'gasPrice': DEFAULT_GAS_PRICE})
        receipt = self.client.w3.eth.wait_for_transaction_receipt(tx_hash)
        return {'tx_hash': tx_hash.hex(), 'contract_address': receipt['contractAddress']}

    def call(self, contract_addr: str, abi: List, func_name: str,
             args: List = None, from_addr: str = None, is_view: bool = False) -> Any:
        contract = self.client.w3.eth.contract(address=contract_addr, abi=abi)
        func = getattr(contract.functions, func_name)(*args) if args else getattr(contract.functions, func_name)()
        if is_view:
            return func.call()
        tx = func.build_transaction({
            'from': from_addr,
            'gas': 200000,
            'gasPrice': DEFAULT_GAS_PRICE,
            'chainId': self.client.chain_id,
            'nonce': self.client.w3.eth.get_transaction_count(from_addr)
        })
        tx_hash = self.client.w3.eth.send_transaction(tx)
        return {'tx_hash': tx_hash.hex()}