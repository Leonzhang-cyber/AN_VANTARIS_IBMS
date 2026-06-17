# src/blockchain/account.py
"""
区块链账户管理模块

提供与 Geth 节点账户相关的操作，包括：
- 查询节点管理的所有账户
- 查询指定账户的 ETH 余额
- 创建新的以太坊账户
- 解锁账户（用于发送交易）

注意：
    - 创建和解锁账户需要 Geth 节点启用 personal API，并在启动参数中添加 --http.api personal
    - 出于安全考虑，生产环境应避免通过 HTTP 远程解锁账户，推荐使用节点启动时的自动解锁或 IPC 方式
"""

from .client import BlockchainClient


class AccountManager:
    """
    账户管理器

    封装了与以太坊账户相关的常见操作，依赖 BlockchainClient 提供的 Web3 连接实例。
    """

    def __init__(self, client: BlockchainClient):
        """
        初始化账户管理器

        :param client: 已连接并配置好的 BlockchainClient 实例
        """
        self.client = client

    def list_accounts(self) -> list:
        """
        获取当前节点管理的所有账户地址列表

        这些账户对应于节点 keystore 目录下的私钥文件。
        注意：账户必须被节点“识别”（即私钥存在于 keystore 中），但不一定已解锁。

        :return: 账户地址字符串列表，每个地址以 '0x' 开头
        :rtype: list[str]

        示例:
            >>> accounts = account_manager.list_accounts()
            >>> print(accounts)
            ['0x9AA128582b17C0c0143690F24012C8DBCf24767f', '0xc49eb8C061c89d5a7a1385b27c63eBd141b89123']
        """
        return self.client.w3.eth.accounts

    def get_balance(self, address: str, unit: str = 'ether') -> float:
        """
        查询指定账户的 ETH 余额

        :param address: 要查询的账户地址（支持 checksum 或普通格式）
        :param unit:    返回余额的单位，默认为 'ether'。
                         可选值：'wei', 'kwei', 'mwei', 'gwei', 'szabo', 'finney', 'ether'
        :return:        以指定单位表示的账户余额（浮点数）
        :rtype:         float

        示例:
            >>> balance = account_manager.get_balance('0x9AA128582b17C0c0143690F24012C8DBCf24767f')
            >>> print(f"余额: {balance} ETH")
            余额: 100.0 ETH
        """
        # 获取以 wei 为单位的余额（最小单位）
        wei = self.client.w3.eth.get_balance(address)
        # 使用 Web3 内置方法将 wei 转换为目标单位
        return float(self.client.w3.from_wei(wei, unit))

    def create_account(self, password: str = "") -> str:
        """
        在节点上创建一个新的以太坊账户

        新账户的私钥将被加密保存在节点的 keystore 目录中。
        注意：此方法依赖 personal API，需节点启用相应模块。

        :param password: 用于加密私钥的密码，默认为空字符串（测试环境常用）
        :return:         新创建的账户地址（字符串，以 '0x' 开头）
        :rtype:          str

        示例:
            >>> new_addr = account_manager.create_account("mypassword")
            >>> print(f"新账户地址: {new_addr}")
            新账户地址: 0x...
        """
        return self.client.w3.geth.personal.new_account(password)

    def unlock_account(self, address: str, password: str = "", duration: int = 0) -> bool:
        """
        解锁指定账户，使其可用于发送交易

        在 PoA 私有链中，若节点启动时未通过 --unlock 自动解锁，则需要调用此方法。
        出于安全考虑，通过 HTTP-RPC 调用此方法需要节点启动时添加 --allow-insecure-unlock 参数。

        :param address:  要解锁的账户地址
        :param password: 账户对应的密码（创建账户时设置的密码）
        :param duration: 解锁持续时间（秒）。0 表示永久解锁（直到节点重启），
                         其他正数表示在指定秒数后自动重新锁定。
        :return:         解锁是否成功（True/False）
        :rtype:          bool

        示例:
            >>> unlocked = account_manager.unlock_account('0x...', 'mypassword', 300)
            >>> print(f"解锁状态: {unlocked}")
            解锁状态: True
        """
        return self.client.w3.geth.personal.unlock_account(address, password, duration)