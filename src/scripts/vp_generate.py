import json
from datetime import datetime, timezone
from cryptography.hazmat.primitives.asymmetric import ed25519

# ==============================
# 🔑 请在这里填写你的参数
# ==============================
DID = "did:ibms:employee:3c00dfe4-1090-4e9f-8e59-99c16d50776b"
VC_ID = "43ce8396-9621-4a68-836e-ddb6c0bd3bb3"
PRIVATE_KEY_HEX = "632783d7d79047a2304bc117c447e836f6f468bfaa9cb9d1b0a5d0c991cb2980"
CHALLENGE = "221d539732a6f30718d5411c4cfba093"

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