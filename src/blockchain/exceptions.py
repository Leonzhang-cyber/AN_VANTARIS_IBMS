# src/blockchain/exceptions.py
"""区块链模块自定义异常"""

class BlockchainError(Exception):
    """区块链模块基础异常"""
    pass

class ConnectionError(BlockchainError):
    """连接节点失败"""
    pass

class TransactionError(BlockchainError):
    """交易相关错误"""
    pass

class ContractError(BlockchainError):
    """智能合约相关错误"""
    pass