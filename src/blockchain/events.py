# src/blockchain/events.py
from typing import List, Dict, Union
from .client import BlockchainClient

class EventManager:
    def __init__(self, client: BlockchainClient):
        self.client = client

    def get_events(self, contract_addr: str, abi: List, event_name: str,
                   from_block: int = 0, to_block: Union[int, str] = 'latest',
                   argument_filters: Dict = None) -> List[Dict]:
        contract = self.client.w3.eth.contract(address=contract_addr, abi=abi)
        event = getattr(contract.events, event_name)
        flt = event.create_filter(fromBlock=from_block, toBlock=to_block, argument_filters=argument_filters)
        return [dict(e) for e in flt.get_all_entries()]