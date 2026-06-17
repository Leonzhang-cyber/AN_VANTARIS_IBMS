import json
import os

_PLACEHOLDER = "replace-with-test-did-private-key"
private_key = os.getenv("IBMS_TEST_DID_PRIVATE_KEY", _PLACEHOLDER).strip() or _PLACEHOLDER

vc_payload = {
    "private_key": private_key,
    "public_key": "0x3779698D179cfeC938b31CEbdc7ED515b6EEDa0D",
    "vc": {
        "@context": [
            "https://www.w3.org/2018/credentials/v1"
        ],
        "credentialSubject": {
            "active": True,
            "created_at": "2026-04-28T15:37:25",
            "entity_type": "property",
            "extra": {
                "address": "XX路1号",
                "contact": "123456789",
                "parent_did": "did:imbs:system:root:2f71181048b0",
            },
            "id": "did:imbs:system:root:property:f121f6d6:0818318eea03",
            "level": 1,
            "name": "测试物业",
            "permissions": [
                "device:read",
                "device:control",
                "employee:manage",
            ],
            "public_key": "0x3779698D179cfeC938b31CEbdc7ED515b6EEDa0D",
            "region": "全园区",
        },
        "expirationDate": "2027-04-28T07:36:58.672474Z",
        "id": "vc:imbs:e192361dee76",
        "issuanceDate": "2026-04-28T07:37:29.397325Z",
        "issuer": "did:imbs:system:root:2f71181048b0",
        "proof": {
            "created": "2026-04-28T07:37:29.405086Z",
            "proofPurpose": "assertionMethod",
            "signatureValue": "17b0fea6cd076a4b8f1666ccc29bb151ec9f671507432d150c56f46184232c4970e2fa657ff86cbcd39ebc51d6e0646d66e6f4ef4eefde95fef8213ed70d25b81c",
            "type": "EcdsaSecp256k1Signature2019",
            "verificationMethod": "did:imbs:system:root:2f71181048b0#keys-1",
        },
        "type": [
            "VerifiableCredential",
            "PropertyCredential",
        ],
    },
}

if private_key == _PLACEHOLDER:
    print("IBMS_TEST_DID_PRIVATE_KEY is not set; writing placeholder private_key to output file.")
    print("Export a test-only private key via environment variable for real signing tests.")

with open("vc_credential.json", "w", encoding="utf-8") as f:
    json.dump(vc_payload, f, indent=4, ensure_ascii=False)

print("✅ 文件已生成: vc_credential.json")
print("📄 文件包含 VC 凭证结构（private_key 来自环境变量或占位符）")
