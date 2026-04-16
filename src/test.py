from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

# ==================== 配置区域 ====================
# 三个节点的 RPC 地址
NODE_URLS = [
    "http://140.245.109.223:8545",  # node1
    "http://140.245.109.223:8546",  # node2
    "http://140.245.109.223:8547",  # node3
]
# =================================================

def check_node(node_url, node_name):
    """检查单个节点的状态并返回关键信息"""
    print(f"\n{'='*50}")
    print(f"🔍 正在检查 {node_name} ({node_url})")
    print('='*50)

    w3 = Web3(Web3.HTTPProvider(node_url))
    w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

    if not w3.is_connected():
        print(f"❌ {node_name} 无法连接！")
        return None

    print(f"✅ 连接成功")
    info = {
        'name': node_name,
        'chain_id': w3.eth.chain_id,
        'block_number': w3.eth.block_number,
        'accounts': w3.eth.accounts,
        'balances': {},
        'client_version': w3.client_version,
        'peer_count': None,
        'node_info': None,
    }

    # 查询账户余额
    for addr in info['accounts']:
        info['balances'][addr] = w3.from_wei(w3.eth.get_balance(addr), 'ether')

    # 尝试获取对等节点数
    try:
        info['peer_count'] = w3.net.peer_count
    except Exception:
        pass

    # 尝试获取节点详情
    try:
        info['node_info'] = w3.geth.admin.node_info()
    except Exception:
        pass

    return info


def main():
    results = []
    for idx, url in enumerate(NODE_URLS, start=1):
        info = check_node(url, f"node{idx}")
        if info:
            results.append(info)

    if not results:
        print("❌ 所有节点均无法连接，请检查网络或节点状态。")
        return

    # 汇总对比
    print("\n" + "="*60)
    print("📊 三节点状态汇总对比")
    print("="*60)

    # 链 ID 和区块高度一致性
    chain_ids = [r['chain_id'] for r in results]
    block_numbers = [r['block_number'] for r in results]

    print(f"🔗 链 ID 一致性: {chain_ids[0] if len(set(chain_ids)) == 1 else '❌ 不一致！'}")
    if len(set(block_numbers)) == 1:
        print(f"📦 区块高度一致: 均为 {block_numbers[0]}")
    else:
        print("⚠️ 区块高度不一致！如果相差唯一可能是访问时间差")
        for r in results:
            print(f"   {r['name']}: {r['block_number']}")

    # 对等节点数
    print("\n🌐 对等节点数:")
    for r in results:
        peer_str = r['peer_count'] if r['peer_count'] is not None else "N/A"
        print(f"   {r['name']}: {peer_str}")

    # 账户信息
    print("\n👛 各节点管理的账户:")
    for r in results:
        print(f"   {r['name']} ({len(r['accounts'])} 个账户):")
        for addr, bal in r['balances'].items():
            print(f"      {addr[:10]}...{addr[-8:]}: {bal} ETH")

    # 节点版本
    print("\n🖥️ 客户端版本:")
    for r in results:
        print(f"   {r['name']}: {r['client_version']}")

    # 如果有节点详情，显示 enode 前缀
    print("\n📡 节点 enode (前20字符):")
    for r in results:
        if r['node_info']:
            enode = r['node_info']['enode']
            print(f"   {r['name']}: {enode[:30]}...")
        else:
            print(f"   {r['name']}: 未启用 admin 模块")

    # 健康检查结论
    print("\n" + "="*60)
    if len(set(block_numbers)) == 1 and all(r['peer_count'] == 2 for r in results if r['peer_count'] is not None):
        print("✅ 集群状态健康：所有节点高度一致，对等节点数正常。")
    else:
        print("⚠️ 集群可能存在异常，请检查上述不一致项。")


if __name__ == "__main__":
    main()