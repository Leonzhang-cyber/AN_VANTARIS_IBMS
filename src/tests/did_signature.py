#!/usr/bin/env python3
"""
使用真实数据生成签名
"""

from eth_account import Account
from eth_account.messages import encode_defunct

# ========== 你的真实数据 ==========
# system_did = "did:imbs:system:root:2f71181048b0"
#     system_did_secret = "0xa1eeD703B79f2548eaa1E591370d19c67E561D9e"
#     system_did_public_key = "0xa1eeD703B79f2548eaa1E591370d19c67E561D9e"
#     system_did_private_key = "792b838cc64813c4b40f4ecbde9cce1479930062e2726c8dec9e0fdc64821a10"
# DID = "did:imbs:system:root:property:1de5df17:dae89a357231"
# PRIVATE_KEY = "d6d29d9268fccb39d384ad8bb756a39d45aae11461f0d4cca3c14848ff20078c"
# CHALLENGE = "3e7eea9485da5ff5cc450e02d02760048aa869a47832dea14a9720623ce65f66"
DID = "did:imbs:system:root:2f71181048b0"
PRIVATE_KEY = "792b838cc64813c4b40f4ecbde9cce1479930062e2726c8dec9e0fdc64821a10"
CHALLENGE = "3e7eea9485da5ff5cc450e02d02760048aa869a47832dea14a9720623ce65f66"

# ========== 生成签名 ==========
print("\n" + "=" * 70)
print("签名生成")
print("=" * 70)

# 1. 格式化私钥（添加 0x 前缀）
if not PRIVATE_KEY.startswith('0x'):
    private_key = '0x' + PRIVATE_KEY
else:
    private_key = PRIVATE_KEY

print(f"DID:        {DID}")
print(f"私钥:       {private_key}")
print(f"挑战码:     {CHALLENGE}")

# 2. 创建钱包获取公钥地址
wallet = Account.from_key(private_key)
print(f"\n公钥地址:   {wallet.address}")

# 3. 签名
message = encode_defunct(text=CHALLENGE)
signed = Account.sign_message(message, private_key=private_key)
signature = '0x' + signed.signature.hex()

print(f"\n签名结果:")
print(f"signature = \"{signature}\"")
print(f"\n签名长度: {len(signature)} 字符")

# 4. 验证签名
print("\n" + "=" * 70)
print("签名验证")
print("=" * 70)

recovered = Account.recover_message(message, signature=signature)
print(f"恢复地址:   {recovered}")

if recovered.lower() == wallet.address.lower():
    print(f"\n✅ 签名验证通过！")
else:
    print(f"\n❌ 签名验证失败！")
    print(f"期望地址:   {wallet.address}")

# 5. 输出登录请求 JSON
print("\n" + "=" * 70)
print("登录请求 JSON")
print("=" * 70)

import json
login_data = {
    "did": DID,
    "challenge": CHALLENGE,
    "signature": signature
}
print(json.dumps(login_data, indent=2))

print("\n" + "=" * 70)
print("curl 命令")
print("=" * 70)
print(f'''curl -X POST "http://localhost:5000/api/did/login" \\
  -H "Content-Type: application/json" \\
  -d '{{"did": "{DID}", "challenge": "{CHALLENGE}", "signature": "{signature}"}}'
''')