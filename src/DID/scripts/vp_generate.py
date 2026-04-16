import json
from datetime import datetime, timezone
from cryptography.hazmat.primitives.asymmetric import ed25519

# ==============================
# 🔑 请在这里填写你的参数
# ==============================
DID = "did:ibms:area:0bdf6af2-0ba2-4c85-b3c6-63f02f3dc31e"
VC_ID = "0b29870f-702b-49b3-abbd-c2e77e262788"
PRIVATE_KEY_HEX = "e05d6fa2c4dbfde2b2efe0bf71bca8cf7f264878ec29b2286003f8c7c243cc52"
CHALLENGE = "9b44f3410ffaaea8a2c59eb9b0c2c5be"

# ==============================
# 🧮 自动生成 VP
# ==============================

# 1. 构造 unsigned VP（不含 proof）
unsigned_vp = {
    "@context": ["https://www.w3.org/2018/credentials/v1"],
    "type": ["VerifiablePresentation"],
    "holder": DID,
    "verifiableCredential": [
        {"id": f"urn:uuid:{VC_ID}"}
    ]
}

# 2. Canonicalize：按 key 排序 + 紧凑 JSON（无空格）
canonical_json = json.dumps(unsigned_vp, sort_keys=True, separators=(',', ':'))
message_bytes = canonical_json.encode('utf-8')

# 3. 用私钥签名（Ed25519）
private_key = ed25519.Ed25519PrivateKey.from_private_bytes(bytes.fromhex(PRIVATE_KEY_HEX))
signature = private_key.sign(message_bytes)
signature_value = signature.hex()

# 4. 构造完整 VP
vp = {
    "presentation": {
        **unsigned_vp,
        "proof": {
            "type": "Ed25519Signature2020",
            "created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "verificationMethod": f"{DID}#key-1",
            "proofPurpose": "authentication",
            "challenge": CHALLENGE,
            "signatureValue": signature_value
        }
    }
}

# 5. 输出结果
print("✅ 你的 VP 登录参数如下：\n")
print(json.dumps(vp, indent=2))