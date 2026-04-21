# src/main.py
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

from flask import Flask
from flask_cors import CORS

from src.DID import DIDService
from src.api import api_bp
from src.common.core.database import init_database, db
from src.common.config.default import Config
from src.blockchain import Blockchain
from src.blockchain.config import ANCHOR_CONTRACT_ADDRESS, ANCHOR_CONTRACT_ABI
from src.Iot.device_manager import get_device_manager


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)
    init_database(app)
    app.register_blueprint(api_bp)

    with app.app_context():
        init_system_on_startup()
        init_iot_device_manager(app)
    return app


def init_system_on_startup():
    bc = Blockchain()
    accounts = bc.account.list_accounts()
    if not accounts:
        raise RuntimeError("区块链账户不可用，请检查私有链状态")

    if not ANCHOR_CONTRACT_ADDRESS or not ANCHOR_CONTRACT_ABI:
        print("❌ 锚定合约未配置")
        return

    try:
        contract = bc.client.w3.eth.contract(address=ANCHOR_CONTRACT_ADDRESS, abi=ANCHOR_CONTRACT_ABI)
        _ = contract.functions.getEntityHash("test").call()
        print(f"ℹ️ 锚定合约已连接: {ANCHOR_CONTRACT_ADDRESS}")
    except Exception as e:
        print(f"❌ 锚定合约连接失败: {e}")
        return

    service = DIDService(db.session, bc, contract)

    try:
        result = service.init_system_entity()
        if result.get('is_new'):
            print(f"✅ 系统实体已创建: {result['did']}")
        else:
            print(f"ℹ️ 系统实体已存在: {result['did']}")
    except Exception as e:
        print(f"❌ 系统初始化失败: {e}")


def init_iot_device_manager(app):
    try:
        device_manager = get_device_manager()
        device_manager.set_app(app)
        # 不再需要 set_socketio
        device_manager.start()
    except Exception as e:
        print(f"❌ IoT 设备管理器启动失败: {e}")


if __name__ == '__main__':
    app = create_app()
    # 使用普通 Flask 运行，不再需要 socketio
    app.run(debug=False, host='0.0.0.0', port=5000)