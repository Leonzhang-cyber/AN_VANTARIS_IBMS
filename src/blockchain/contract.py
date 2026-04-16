# src/blockchain/contract.py
"""
智能合约管理模块

提供智能合约的部署、调用（读/写）功能，封装了 Web3.py 合约交互的常用操作。

主要功能：
- 部署新合约到区块链
- 调用合约的只读函数（免费、即时返回）
- 调用合约的写函数（发送交易，修改链上状态）

使用前需准备好合约的 ABI 和字节码（可通过 solcx 编译 Solidity 源码获得）。
"""

from typing import List, Optional, Any, Dict

from .client import BlockchainClient
from .config import DEFAULT_GAS_PRICE


class ContractManager:
    """
    智能合约管理器

    依赖 BlockchainClient 提供的 Web3 连接实例，封装了合约部署和函数调用逻辑。
    """

    def __init__(self, client: BlockchainClient):
        """
        初始化合约管理器

        :param client: 已连接并配置好的 BlockchainClient 实例
        """
        self.client = client

    def deploy(
        self,
        from_addr: str,
        abi: List,
        bytecode: str,
        constructor_args: Optional[List] = None,
        gas: int = 3000000
    ) -> Dict:
        """
        部署一个新的智能合约到区块链上

        :param from_addr:       部署合约的账户地址（必须是已解锁的账户）
        :param abi:             合约的 ABI（Application Binary Interface）列表
        :param bytecode:        合约编译后的十六进制字节码（以 '0x' 开头）
        :param constructor_args: 合约构造函数的参数列表（按顺序），默认为 None 表示无参构造函数
        :param gas:             部署交易的最大 Gas 限额，默认 3,000,000（足够大多数合约）
        :return:                包含交易哈希和合约地址的字典
                                {'tx_hash': '0x...', 'contract_address': '0x...'}
        :rtype:                 Dict

        示例:
            >>> deploy_result = contract_manager.deploy(
            ...     from_addr='0x9AA128582b17C0c0143690F24012C8DBCf24767f',
            ...     abi=abi,
            ...     bytecode=bytecode,
            ...     constructor_args=[100]  # 假设构造函数接受一个 uint256 参数
            ... )
            >>> print(deploy_result['contract_address'])
            0x257fF6Ec9b026E50AA340FDe7A607bA0C665A49b
        """
        # 创建合约工厂对象
        contract = self.client.w3.eth.contract(abi=abi, bytecode=bytecode)

        # 获取构造函数（根据是否有参数决定调用方式）
        if constructor_args:
            constructor = contract.constructor(*constructor_args)
        else:
            constructor = contract.constructor()

        # 发送部署交易
        tx_hash = constructor.transact({
            'from': from_addr,
            'gas': gas,
            'gasPrice': DEFAULT_GAS_PRICE  # 从配置读取，当前为 0（私有链免费）
        })

        # 等待交易被打包确认，获取收据
        receipt = self.client.w3.eth.wait_for_transaction_receipt(tx_hash)

        return {
            'tx_hash': tx_hash.hex(),
            'contract_address': receipt['contractAddress']
        }

    def call(
        self,
        contract_addr: str,
        abi: List,
        func_name: str,
        args: Optional[List] = None,
        from_addr: Optional[str] = None,
        is_view: bool = False
    ) -> Any:
        """
        调用合约函数（自动区分只读函数和写函数）

        :param contract_addr: 已部署的合约地址（以 '0x' 开头）
        :param abi:           合约的 ABI 列表
        :param func_name:     要调用的函数名称
        :param args:          函数参数列表（按顺序），默认为 None 表示无参函数
        :param from_addr:     调用者的账户地址。
                              - 对于只读函数（is_view=True），可不传或传 None
                              - 对于写函数（is_view=False），必须提供已解锁的账户地址
        :param is_view:       是否为只读函数（view 或 pure）。
                              - True：使用 call() 方式调用，免费且不产生交易
                              - False：发送交易，消耗 Gas 并修改链上状态
        :return:              只读函数返回合约中定义的数据类型（如 int, str, bool 等）；
                              写函数返回包含交易哈希的字典 {'tx_hash': '0x...'}
        :rtype:               Any 或 Dict

        示例（只读）:
            >>> value = contract_manager.call(
            ...     contract_addr='0x257fF6Ec9b026E50AA340FDe7A607bA0C665A49b',
            ...     abi=abi,
            ...     func_name='get',
            ...     is_view=True
            ... )
            >>> print(value)
            42

        示例（写入）:
            >>> result = contract_manager.call(
            ...     contract_addr='0x257fF6Ec9b026E50AA340FDe7A607bA0C665A49b',
            ...     abi=abi,
            ...     func_name='set',
            ...     args=[42],
            ...     from_addr='0x9AA128582b17C0c0143690F24012C8DBCf24767f',
            ...     is_view=False
            ... )
            >>> print(result['tx_hash'])
            0x...
        """
        # 创建合约实例
        contract = self.client.w3.eth.contract(address=contract_addr, abi=abi)

        # 获取要调用的函数对象
        if args:
            func = getattr(contract.functions, func_name)(*args)
        else:
            func = getattr(contract.functions, func_name)()

        # 只读函数：直接调用 call()，返回结果
        if is_view:
            return func.call()

        # 写函数：构建交易并发送
        tx = func.build_transaction({
            'from': from_addr,
            'gas': 200000,                     # 写函数的默认 Gas 限额（可调）
            'gasPrice': DEFAULT_GAS_PRICE,      # 从配置读取，当前为 0
            'chainId': self.client.chain_id,    # 防止跨链重放
            'nonce': self.client.w3.eth.get_transaction_count(from_addr)
        })

        tx_hash = self.client.w3.eth.send_transaction(tx)
        # 注意：此处未等待交易收据，调用方可根据需要自行 wait_for_transaction_receipt
        return {'tx_hash': tx_hash.hex()}