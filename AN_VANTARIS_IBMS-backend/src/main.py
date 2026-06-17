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


def stop_all_mining(bc: Blockchain):
    """停止所有节点的挖矿"""
    try:
        node_urls = bc.client.node_urls if hasattr(bc.client, 'node_urls') else []
        from web3 import Web3

        for url in node_urls:
            try:
                w3 = Web3(Web3.HTTPProvider(url))
                if w3.is_connected():
                    result = w3.provider.make_request('miner_stop', [])
                    if result.get('result'):
                        print(f"  ✅ {url} 挖矿已停止")
                    else:
                        print(f"  ℹ️ {url} 挖矿本来就未运行")
                else:
                    print(f"  ⚠️ {url} 连接失败")
            except Exception as e:
                print(f"  ⚠️ {url} 停止挖矿异常: {e}")
    except Exception as e:
        print(f"⚠️ 停止挖矿失败: {e}")


def init_system_on_startup():
    bc = Blockchain()
    accounts = bc.account.list_accounts()
    if not accounts:
        raise RuntimeError("区块链账户不可用，请检查私有链状态")

    print("\n🔍 检查私有链挖矿状态...")
    mining_active = False

    try:
        for node_url in bc.client.node_urls:
            try:
                from web3 import Web3
                w3 = Web3(Web3.HTTPProvider(node_url))
                if w3.is_connected():
                    is_mining = w3.provider.make_request('eth_mining', [])
                    if is_mining.get('result'):
                        print(f"⚠️ {node_url} 正在挖矿")
                        mining_active = True
                    else:
                        print(f"ℹ️ {node_url} 挖矿已停止")
            except:
                pass

        if mining_active:
            print("\n🛑 停止所有节点挖矿...")
            stop_all_mining(bc)
            print("✅ 挖矿已停止，服务将以空闲模式启动\n")
        else:
            print("✅ 所有节点挖矿已停止，无需操作\n")

    except Exception as e:
        print(f"⚠️ 挖矿状态检查失败: {e}\n")

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
        # if result.get('is_new'):
        #     print(f"✅ 系统实体已创建: {result['did']}")
        if result.get('is_new'):
            print("✅✅✅ 系统根实体首次创建成功 ✅✅✅")
            print("=" * 60)
            print(f"📌 DID: {result['did']}")
            print(f"📌 实体名称: {result.get('name', 'System Root')}")
            print(f"📌 实体类型: {result.get('entity_type', 'system')}")
            print("-" * 60)
            configured = bool(result.get('private_key'))
            print(f"DID private key configured: {'yes' if configured else 'no'}")
            print("-" * 60)
            print("⚠️  警告：私钥已生成但未输出到日志。请通过安全渠道保存。")
            print("=" * 60)
        else:
            print(f"ℹ️ 系统实体已存在: {result['did']}")
    except Exception as e:
        print(f"❌ 系统初始化失败: {e}")


def init_iot_device_manager(app):
    try:
        device_manager = get_device_manager()
        device_manager.set_app(app)
        device_manager.start()
    except Exception as e:
        print(f"❌ IoT 设备管理器启动失败: {e}")


def _log_simulator_production_guard(app):
    """SECURITY-A8: testMQTT/simulators are not registered on the main Flask app."""
    env = app.config.get("IBMS_ENV", "development")
    is_prod = app.config.get("IS_PRODUCTION", False)
    is_smoke = app.config.get("IS_LOCAL_SMOKE", False)
    sim_on = app.config.get("SIMULATOR_ENABLED", False)
    testmqtt_on = app.config.get("TESTMQTT_ENABLED", False)
    print(f"[SECURITY-A8] IBMS_ENV={env}; production={is_prod}; local_smoke={is_smoke}")
    print("[SECURITY-A8] testMQTT/simulator routes are NOT registered on the main API blueprint.")
    if is_smoke:
        print("[local-smoke] Blockchain init and IoT DeviceManager start are disabled.")
    if is_prod:
        if sim_on or testmqtt_on:
            print("[SECURITY-A8] WARNING: simulator flags are ignored in production (forced off).")
        print("[SECURITY-A8] Production mode: standalone simulators and testMQTT scripts must remain disabled.")
    else:
        print(
            f"[SECURITY-A8] Non-production: IBMS_SIMULATOR_ENABLED={sim_on}, "
            f"IBMS_TESTMQTT_ENABLED={testmqtt_on} (explicit enable required for standalone scripts)."
        )


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)
    init_database(app)
    app.register_blueprint(api_bp)

    with app.app_context():
        _log_simulator_production_guard(app)
        if app.config.get("IS_LOCAL_SMOKE"):
            print("[local-smoke] Skipping blockchain/DID system initialization")
        else:
            init_system_on_startup()
        if app.config.get("IS_LOCAL_SMOKE"):
            print("[local-smoke] Skipping IoT DeviceManager start")
        else:
            init_iot_device_manager(app)
    return app


# ==========================================
# ✅ 关键修复：uWSGI 必须能找到这个变量
# ==========================================
app = create_app()
application = app

if __name__ == '__main__':
    bind_host = Config.BIND_HOST
    bind_port = Config.BIND_PORT
    print(f"[IBMS] Starting on {bind_host}:{bind_port} (IBMS_ENV={Config.IBMS_ENV})")
    application.run(debug=False, host=bind_host, port=bind_port)