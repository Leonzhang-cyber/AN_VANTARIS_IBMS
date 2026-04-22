# # deploy_anchor.py
# """
# 手动部署 IMBSAnchor 合约到私有链（使用 ContractManager）
# """
#
# import json
# from src.blockchain import Blockchain
#
# # 读取合约源码
# with open('src/blockchain/contracts/IMBSAnchor.sol', 'r', encoding='utf-8') as f:
#     source = f.read()
#
# # 编译合约
# from solcx import compile_source, install_solc, set_solc_version
# install_solc('0.8.19')
# set_solc_version('0.8.19')
# compiled = compile_source(source, output_values=['abi', 'bin'])
# _, interface = compiled.popitem()
# abi = interface['abi']
# bytecode = interface['bin']
#
# print("✅ 合约编译成功")
#
# # 连接私有链
# bc = Blockchain()
# accounts = bc.account.list_accounts()
# if len(accounts) < 2:
#     raise RuntimeError("请确保私有链节点至少有两个账户（其中一个有余额）")
# deployer = accounts[1]  # 使用第二个账户（有100 ETH）
#
# print(f"🔑 部署账户: {deployer}")
# print("🚀 正在部署合约（将自动通过调度器管理挖矿）...")
#
# # 直接调用 ContractManager.deploy，内部已集成挖矿调度器
# deploy_result = bc.contract.deploy(
#     from_addr=deployer,
#     abi=abi,
#     bytecode=bytecode,
#     gas=3000000
# )
# contract_addr = deploy_result['contract_address']
#
# print("\n" + "=" * 60)
# print(f"✅ 合约部署成功！")
# print(f"📜 合约地址: {contract_addr}")
# print("=" * 60)
# print("\n📋 请将以下内容复制到 src/blockchain/config.py 中：\n")
# print(f'ANCHOR_CONTRACT_ADDRESS = "{contract_addr}"')
# print("ANCHOR_CONTRACT_ABI = [")
# for item in abi:
#     print(f"    {json.dumps(item)},")
# print("]")


# deploy_anchor.py
"""
手动部署 IMBSAnchor 合约到私有链（使用 ContractManager）
"""

import json
from src.blockchain import Blockchain

# 读取合约源码
with open('../blockchain/contracts/IMBSAnchor.sol', 'r', encoding='utf-8') as f:
    source = f.read()

# 编译合约
from solcx import compile_source, install_solc, set_solc_version
install_solc('0.8.19')
set_solc_version('0.8.19')
compiled = compile_source(source, output_values=['abi', 'bin'])
_, interface = compiled.popitem()
abi = interface['abi']
bytecode = interface['bin']

print("✅ 合约编译成功")

# 连接私有链
bc = Blockchain()
accounts = bc.account.list_accounts()
if len(accounts) < 2:
    raise RuntimeError("请确保私有链节点至少有两个账户（其中一个有余额）")
deployer = accounts[1]  # 使用第二个账户（有100 ETH）

print(f"🔑 部署账户: {deployer}")
print("🚀 正在部署合约（将自动通过调度器管理挖矿）...")

# 直接调用 ContractManager.deploy，内部已集成挖矿调度器
deploy_result = bc.contract.deploy(
    from_addr=deployer,
    abi=abi,
    bytecode=bytecode,
    gas=3000000
)
contract_addr = deploy_result['contract_address']

print("\n" + "=" * 60)
print(f"✅ 合约部署成功！")
print(f"📜 合约地址: {contract_addr}")
print("=" * 60)

# 🆕 立即停止挖矿
print("\n🛑 停止挖矿...")
try:
    # 方法1：通过 mining_scheduler 停止
    if hasattr(bc, 'mining_scheduler') and bc.mining_scheduler:
        bc.mining_scheduler.stop_mining()
        print("✅ 挖矿已停止（通过调度器）")
    else:
        # 方法2：直接调用 RPC 停止
        for node_url in bc.client.node_urls:
            from web3 import Web3
            w3 = Web3(Web3.HTTPProvider(node_url))
            if w3.is_connected():
                w3.provider.make_request('miner_stop', [])
                print(f"  ✅ {node_url} 挖矿已停止")
except Exception as e:
    print(f"⚠️ 停止挖矿失败: {e}")

print("\n📋 请将以下内容复制到 src/blockchain/config.py 中：\n")
print(f'ANCHOR_CONTRACT_ADDRESS = "{contract_addr}"')
print("ANCHOR_CONTRACT_ABI = [")
for item in abi:
    print(f"    {json.dumps(item)},")
print("]")