#!/usr/bin/env python3
"""
使用环境变量中的测试私钥生成签名（本地手动运行）。
设置 IBMS_TEST_DID_PRIVATE_KEY 后再执行；不会在输出中打印私钥值。
"""

import json
import os
import sys

from eth_account import Account
from eth_account.messages import encode_defunct

DID = "did:imbs:system:root:2f71181048b0"
CHALLENGE = "3e7eea9485da5ff5cc450e02d02760048aa869a47832dea14a9720623ce65f66"

PRIVATE_KEY = os.getenv("IBMS_TEST_DID_PRIVATE_KEY", "").strip()
_PLACEHOLDER = "replace-with-test-did-private-key"

if not PRIVATE_KEY or PRIVATE_KEY == _PLACEHOLDER:
    print("IBMS_TEST_DID_PRIVATE_KEY is not set or is still the placeholder.")
    print("Export a test-only private key via environment variable before running this script.")
    sys.exit(0)

# ========== 生成签名 ==========
print("\n" + "=" * 70)
print("签名生成")
print("=" * 70)

if not PRIVATE_KEY.startswith("0x"):
    private_key = "0x" + PRIVATE_KEY
else:
    private_key = PRIVATE_KEY

print(f"DID:        {DID}")
print("私钥:       [configured — value not printed]")
print(f"挑战码:     {CHALLENGE}")

wallet = Account.from_key(private_key)
print(f"\n公钥地址:   {wallet.address}")

message = encode_defunct(text=CHALLENGE)
signed = Account.sign_message(message, private_key=private_key)
signature = "0x" + signed.signature.hex()

print("\n签名结果:")
print(f'signature = "{signature}"')
print(f"\n签名长度: {len(signature)} 字符")

print("\n" + "=" * 70)
print("签名验证")
print("=" * 70)

recovered = Account.recover_message(message, signature=signature)
print(f"恢复地址:   {recovered}")

if recovered.lower() == wallet.address.lower():
    print("\n✅ 签名验证通过！")
else:
    print("\n❌ 签名验证失败！")
    print(f"期望地址:   {wallet.address}")

print("\n" + "=" * 70)
print("登录请求 JSON")
print("=" * 70)

login_data = {
    "did": DID,
    "challenge": CHALLENGE,
    "signature": signature,
}
print(json.dumps(login_data, indent=2))

print("\n" + "=" * 70)
print("curl 命令")
print("=" * 70)
print(
    f'''curl -X POST "http://localhost:5000/api/did/login" \\
  -H "Content-Type: application/json" \\
  -d '{{"did": "{DID}", "challenge": "{CHALLENGE}", "signature": "{signature}"}}'
'''
)
