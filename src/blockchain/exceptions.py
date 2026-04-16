# src/blockchain/exceptions.py
"""
区块链模块自定义异常

定义了模块内部可能抛出的各类异常，便于上层调用者精确捕获和处理错误。
所有异常均继承自 BlockchainError 基类，可统一捕获处理。
"""


class BlockchainError(Exception):
    """
    区块链模块基础异常

    所有自定义异常的父类，可用于统一捕获模块内抛出的所有错误。

    示例:
        try:
            bc = Blockchain()
        except BlockchainError as e:
            print(f"区块链模块错误: {e}")
    """
    pass


class ConnectionError(BlockchainError):
    """
    连接节点失败异常

    当 BlockchainClient 尝试连接所有配置的 RPC 节点均失败时抛出。
    常见原因：
        - 服务器防火墙未开放对应端口
        - Geth 容器未正常运行
        - 网络不可达

    处理建议：
        - 检查 config.NODE_URLS 配置是否正确
        - 在服务器上执行 `docker ps` 确认节点容器状态
        - 执行 `telnet <IP> <端口>` 测试网络连通性
    """
    pass


class TransactionError(BlockchainError):
    """
    交易相关错误异常

    在发送交易、估算 Gas、等待交易收据等环节失败时抛出。
    常见原因：
        - 账户余额不足
        - Gas 估算失败（合约调用参数错误或 revert）
        - 交易 nonce 冲突
        - 发送方账户未解锁

    处理建议：
        - 检查发送方账户余额是否足够
        - 检查合约调用参数是否符合预期
        - 确认节点已通过 --unlock 自动解锁账户
    """
    pass


class ContractError(BlockchainError):
    """
    智能合约相关错误异常

    在合约编译、部署、调用过程中失败时抛出。
    常见原因：
        - 合约源码语法错误或版本不兼容
        - 部署时 Gas 不足
        - 调用不存在的函数名
        - ABI 与合约地址不匹配

    处理建议：
        - 使用 solcx 编译时确认 Solidity 版本正确
        - 部署时适当提高 gas 限额
        - 检查函数名拼写和参数列表是否与 ABI 一致
    """
    pass