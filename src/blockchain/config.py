# src/blockchain/config.py
from typing import List

NODE_URLS: List[str] = [
    "http://140.245.109.223:8545",
    "http://140.245.109.223:8546",
    "http://140.245.109.223:8547",
]
CHAIN_ID: int = 9527
DEFAULT_GAS_PRICE: int = 0
DEFAULT_GAS_LIMIT: int = 21000