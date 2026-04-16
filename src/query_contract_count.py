# query_contract_count_fast.py
"""
快速查询账户部署的合约数量（并发批量版）
"""

import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from blockchain import Blockchain
from web3 import Web3


def fetch_block_transactions(w3: Web3, block_num: int) -> List[dict]:
    """获取单个区块的所有交易（只返回必要字段）"""
    try:
        block = w3.eth.get_block(block_num, full_transactions=True)
        return [
            {'from': tx['from'], 'to': tx.to, 'hash': tx.hash.hex()}
            for tx in block.transactions
        ]
    except Exception:
        return []


def get_contract_deploy_count_fast(
    bc: Blockchain,
    account_address: str,
    from_block: int = 0,
    to_block: Optional[int] = None,
    max_workers: int = 10
) -> int:
    """
    并发扫描统计合约部署数量

    :param bc: Blockchain 实例
    :param account_address: 目标账户地址
    :param from_block: 起始区块
    :param to_block: 结束区块
    :param max_workers: 并发线程数（建议 5~20，视服务器性能而定）
    :return: 合约部署数量
    """
    w3 = bc.client.w3
    account_address = w3.to_checksum_address(account_address)

    if to_block is None:
        to_block = w3.eth.block_number

    print(f"📊 扫描范围：区块 {from_block} 至 {to_block}（共 {to_block - from_block + 1} 个区块）")
    print(f"🔍 目标账户：{account_address}")
    print(f"⚡ 并发线程数：{max_workers}\n")

    block_numbers = list(range(from_block, to_block + 1))
    deploy_count = 0
    processed = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_block = {
            executor.submit(fetch_block_transactions, w3, bn): bn
            for bn in block_numbers
        }

        for future in as_completed(future_to_block):
            block_num = future_to_block[future]
            try:
                txs = future.result()
                for tx in txs:
                    if tx['to'] is None or tx['to'] == "0x0000000000000000000000000000000000000000":
                        if tx['from'] == account_address:
                            deploy_count += 1
                            print(f"   ✅ 发现合约部署：区块 {block_num}，交易 {tx['hash']}")
            except Exception as e:
                print(f"   ⚠️ 区块 {block_num} 获取失败: {e}")

            processed += 1
            if processed % 500 == 0:
                print(f"   进度：{processed}/{len(block_numbers)} 区块已处理")

    return deploy_count


def main():
    print("=" * 60)
    print("  智能合约部署数量查询工具（并发加速版）")
    print("=" * 60)

    try:
        bc = Blockchain()
        print(f"✅ 已连接节点：{bc.client._current_url}")
    except Exception as e:
        print(f"❌ 连接失败：{e}")
        return

    target_address = "0x9AA128582b17C0c0143690F24012C8DBCf24767f"
    print(f"\n🎯 查询账户：{target_address}")

    import time
    start = time.time()
    count = get_contract_deploy_count_fast(
        bc=bc,
        account_address=target_address,
        max_workers=15  # 可根据服务器性能调整
    )
    elapsed = time.time() - start

    print("\n" + "=" * 60)
    print(f"📋 结果：账户 {target_address} 共部署了 {count} 个智能合约")
    print(f"⏱️ 耗时：{elapsed:.2f} 秒")
    print("=" * 60)


if __name__ == "__main__":
    main()