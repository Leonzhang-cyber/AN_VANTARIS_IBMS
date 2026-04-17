# src/main.py
from flask import Flask
from flask_cors import CORS

from src.DID import DIDService
from src.api import api_bp
from src.common.core.database import init_database, db
from src.common.config.default import Config
from src.blockchain import Blockchain
from src.blockchain.config import ANCHOR_CONTRACT_ADDRESS, ANCHOR_CONTRACT_ABI


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)
    init_database(app)
    app.register_blueprint(api_bp)

    with app.app_context():
        init_system_on_startup()

    return app


def init_system_on_startup():
    """应用启动时自动初始化系统实体（使用已部署的锚定合约）"""
    bc = Blockchain()
    accounts = bc.account.list_accounts()
    if not accounts:
        raise RuntimeError("区块链账户不可用，请检查私有链状态")

    if not ANCHOR_CONTRACT_ADDRESS or not ANCHOR_CONTRACT_ABI:
        print("❌ 锚定合约未配置，请在 src/blockchain/config.py 中设置 ANCHOR_CONTRACT_ADDRESS 和 ANCHOR_CONTRACT_ABI")
        return

    # 直接使用 Web3 创建合约实例
    try:
        contract = bc.client.w3.eth.contract(address=ANCHOR_CONTRACT_ADDRESS, abi=ANCHOR_CONTRACT_ABI)
        _ = contract.functions.getEntityHash("test").call()
        print(f"ℹ️ 锚定合约已连接: {ANCHOR_CONTRACT_ADDRESS}")
    except Exception as e:
        print(f"❌ 锚定合约连接失败: {e}")
        return

    # 使用带区块链客户端和合约的 DIDService
    service = DIDService(db.session, bc, contract)

    try:
        result = service.init_system_entity()
        if result.get('is_new'):
            print(f"✅ 系统实体已创建: {result['did']}")
            print(f"📋 系统公钥: {result['public_key']}")
            print(f"🔐 系统私钥: {result['private_key']}")
            print(f"🔗 上链交易哈希: {result['entity_info']['tx_hash']}")
        else:
            print(f"ℹ️ 系统实体已存在: {result['did']}")
    except Exception as e:
        print(f"❌ 系统初始化失败: {e}")


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)