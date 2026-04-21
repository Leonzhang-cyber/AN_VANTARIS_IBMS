# # src/common/utils/vp_util.py
# import json
# from cryptography.hazmat.primitives.asymmetric import ed25519
# from src.DID_Back.dao.did_dao import DIDDocumentDAO
#
#
# def verify_vp(vp: dict) -> tuple[bool, str, str]:
#     """
#     验证 Verifiable Presentation（简化版，适用于内部系统）
#     Returns: (is_valid: bool, holder_did: str, vc_id: str)
#     """
#     try:
#         # 1. 基本结构检查
#         if not isinstance(vp, dict):
#             return False, "", ""
#         if 'VerifiablePresentation' not in vp.get('type', []):
#             return False, "", ""
#
#         holder_did = vp.get('holder')
#         if not holder_did or not isinstance(holder_did, str):
#             return False, "", ""
#
#         vcs = vp.get('verifiableCredential', [])
#         if not vcs or not isinstance(vcs, list) or len(vcs) == 0:
#             return False, "", ""
#
#         # 只处理第一个 VC（你的系统一对一）
#         first_vc = vcs[0]
#         vc_id_uri = first_vc.get('id')
#         if not vc_id_uri or not vc_id_uri.startswith('urn:uuid:'):
#             return False, "", ""
#         vc_id = vc_id_uri.split(':')[-1]  # 提取 UUID
#
#         # 2. 获取公钥
#         doc = DIDDocumentDAO.find_by_did(holder_did)
#         if not doc:
#             return False, "", ""
#         public_key = ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(doc.public_key))
#
#         # 3. 构造待签消息（简化：移除 proof 后排序 JSON）
#         unsigned_vp = vp.copy()
#         unsigned_vp.pop('proof', None)
#         message = json.dumps(unsigned_vp, sort_keys=True, separators=(',', ':')).encode()
#
#         # 4. 验证签名
#         proof = vp.get('proof', {})
#         sig_hex = proof.get('signatureValue') or proof.get('signature')
#         if not sig_hex:
#             return False, "", ""
#
#         # 处理 hex 或 base64（这里假设是 hex）
#         if all(c in '0123456789abcdefABCDEF' for c in sig_hex):
#             sig_bytes = bytes.fromhex(sig_hex)
#         else:
#             # 如果是 base64，需解码（根据前端实现调整）
#             import base64
#             sig_bytes = base64.b64decode(sig_hex)
#
#         public_key.verify(sig_bytes, message)
#
#         return True, holder_did, vc_id
#
#     except Exception as e:
#         print(f"[VP Verify Error] {str(e)}")
#         return False, "", ""