# src/blockchain/config.py
"""
区块链模块全局配置文件

集中管理私有链的连接地址、链ID、Gas费用等核心参数。
修改本文件中的配置将影响整个 blockchain 模块的行为。
"""

from typing import List
import os


_DEV_NODE_URLS: List[str] = [
    "http://127.0.0.1:8545",
    "http://127.0.0.1:8546",
    "http://127.0.0.1:8547",
]
_DEV_CHAIN_ID = 9527  # local dev chain id when IBMS_BLOCKCHAIN_CHAIN_ID is unset
_DEV_ANCHOR_CONTRACT_ADDRESS = ""


def _load_node_urls() -> List[str]:
    rpc_env = os.getenv("IBMS_BLOCKCHAIN_RPC_URL")
    if rpc_env is not None and str(rpc_env).strip():
        urls = [u.strip() for u in str(rpc_env).split(",") if u.strip()]
        if urls:
            return urls
    return _DEV_NODE_URLS


def _env_chain_id() -> int:
    value = os.getenv("IBMS_BLOCKCHAIN_CHAIN_ID")
    if value is not None and str(value).strip():
        return int(str(value).strip())
    return _DEV_CHAIN_ID


def _env_contract_address() -> str:
    value = os.getenv("IBMS_BLOCKCHAIN_CONTRACT_ADDRESS")
    if value is not None and str(value).strip():
        return str(value).strip()
    return _DEV_ANCHOR_CONTRACT_ADDRESS


# ======================== 节点 RPC 地址列表 ========================
# 说明：
#   - 用于 BlockchainClient 按顺序尝试连接，第一个成功即使用
#   - 默认指向本地开发节点；生产环境必须通过 IBMS_BLOCKCHAIN_RPC_URL 配置
#   - 支持逗号分隔的多节点 URL
# ================================================================
NODE_URLS: List[str] = _load_node_urls()


# ======================== 链 ID ========================
# 说明：
#   - 用于交易的 chainId 字段，防止跨链重放攻击
#   - 必须与 genesis.json 中的 chainId 保持一致
# 注意：
#   - 若重建私有链并修改了创世文件中的 chainId，必须同步更新此处
# ======================================================
CHAIN_ID: int = _env_chain_id()


# ======================== 默认 Gas 价格 ========================
# 说明：
#   - 发送交易时使用的 gasPrice（单位：wei）
#   - 当前设为 0，表示私有链交易完全免费
# 注意：
#   - 生产环境若需模拟真实费用，可修改为任意正数（如 1000000000 即 1 Gwei）
#   - 即使 gasPrice=0，节点仍会正常打包交易（前提是未在节点启动参数中限制最低 gasPrice）
# ===========================================================
DEFAULT_GAS_PRICE: int = 0


# ======================== 默认 Gas 限额 ========================
# 说明：
#   - 用于简单转账交易的基础 gas 限额
#   - 实际发送交易时，TransactionManager 会根据交易数据自动估算并调整
# 注意：
#   - 若部署复杂合约或调用高消耗函数，建议在调用时手动指定更高的 gas 值
#   - 21000 是以太坊标准转账的最低 gas 消耗
# ============================================================
DEFAULT_GAS_LIMIT: int = 21000

"""
DID 模块专用配置
包含锚定智能合约的地址和 ABI
"""

# ======================== 锚定合约配置 ========================
# 说明：
#   - 合约部署后，将返回的地址填入此处
#   - ABI 可从 Remix 编译后的 JSON 中复制，或从 solc 编译输出获取
# 注意：
#   - 合约地址必须以 0x 开头，长度为 42 个字符
#   - ABI 是一个 JSON 数组，直接粘贴即可
# ============================================================
# ======================== 锚定合约配置 ========================
ANCHOR_CONTRACT_ADDRESS = _env_contract_address()
ANCHOR_CONTRACT_ABI = [
    {"anonymous": False, "inputs": [{"indexed": True, "internalType": "string", "name": "did", "type": "string"}, {"indexed": False, "internalType": "string", "name": "metadataHash", "type": "string"}, {"indexed": True, "internalType": "address", "name": "operator", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "timestamp", "type": "uint256"}], "name": "EntityAnchored", "type": "event"},
    {"anonymous": False, "inputs": [{"indexed": True, "internalType": "string", "name": "vcId", "type": "string"}, {"indexed": False, "internalType": "string", "name": "vcHash", "type": "string"}, {"indexed": True, "internalType": "string", "name": "issuerDid", "type": "string"}, {"indexed": True, "internalType": "string", "name": "subjectDid", "type": "string"}, {"indexed": False, "internalType": "uint256", "name": "timestamp", "type": "uint256"}], "name": "VCIssuedAnchored", "type": "event"},
    {"anonymous": False, "inputs": [{"indexed": True, "internalType": "string", "name": "vcId", "type": "string"}, {"indexed": True, "internalType": "address", "name": "operator", "type": "address"}, {"indexed": False, "internalType": "uint256", "name": "timestamp", "type": "uint256"}], "name": "VCRevoked", "type": "event"},
    {"inputs": [{"internalType": "string", "name": "did", "type": "string"}, {"internalType": "string", "name": "metadataHash", "type": "string"}], "name": "anchorEntity", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"internalType": "string", "name": "vcId", "type": "string"}, {"internalType": "string", "name": "_vcHash", "type": "string"}, {"internalType": "string", "name": "issuerDid", "type": "string"}, {"internalType": "string", "name": "subjectDid", "type": "string"}], "name": "anchorVC", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"internalType": "string", "name": "", "type": "string"}], "name": "entityMetadataHash", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "string", "name": "did", "type": "string"}], "name": "getEntityHash", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "string", "name": "vcId", "type": "string"}], "name": "getVCHash", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "string", "name": "vcId", "type": "string"}], "name": "isVCRevoked", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "string", "name": "vcId", "type": "string"}], "name": "revokeVC", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"internalType": "string", "name": "did", "type": "string"}, {"internalType": "string", "name": "newMetadataHash", "type": "string"}], "name": "updateEntity", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"internalType": "string", "name": "", "type": "string"}], "name": "vcHash", "outputs": [{"internalType": "string", "name": "", "type": "string"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"internalType": "string", "name": "", "type": "string"}], "name": "vcRevoked", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}], "stateMutability": "view", "type": "function"},
]