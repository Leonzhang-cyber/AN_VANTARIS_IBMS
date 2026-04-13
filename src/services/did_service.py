# src/services/did_service.py
from typing import Optional, Tuple, List
import json
import secrets
from cryptography.hazmat.primitives.asymmetric import ed25519
from src.utils.jwt_util import create_jwt
from datetime import datetime, timedelta
from src.models.did_models import DIDDocument, VCCredential
from src.dao.did_dao import DIDDocumentDAO, VCCredentialDAO, EmployeeDAO
import uuid


class DIDService:
    # 挑战码缓存（类变量）
    _challenge_cache = {}

    # ---------- 辅助方法：挑战码管理 ----------
    @staticmethod
    def _clean_expired_challenges():
        """清理过期的挑战码"""
        now = datetime.utcnow()
        expired = [ch for ch, entry in DIDService._challenge_cache.items() if now > entry["expire_at"]]
        for ch in expired:
            DIDService._challenge_cache.pop(ch, None)

    @staticmethod
    def generate_challenge(did: str) -> str:
        """生成随机挑战码并缓存，有效期 5 分钟"""
        DIDService._clean_expired_challenges()
        challenge = secrets.token_hex(16)
        DIDService._challenge_cache[challenge] = {
            "did": did,
            "expire_at": datetime.utcnow() + timedelta(minutes=5)
        }
        return challenge

    @staticmethod
    def verify_challenge(did: str, challenge: str) -> bool:
        """验证挑战码，一次性使用"""
        entry = DIDService._challenge_cache.get(challenge)
        if not entry:
            return False
        if entry["did"] != did:
            return False
        if datetime.utcnow() > entry["expire_at"]:
            DIDService._challenge_cache.pop(challenge, None)
            return False
        # 验证通过，删除挑战码（防止重放）
        DIDService._challenge_cache.pop(challenge, None)
        return True

    # ---------- 根 DID 初始化 ----------
    @staticmethod
    def init_root_did() -> Tuple[str, str]:
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        public_key_hex = public_key.public_bytes_raw().hex()
        root_did = f"did:ibms:root:{uuid.uuid4()}"
        DIDDocumentDAO.create(did=root_did, did_type='root', public_key=public_key_hex,
                              issuer_did=None, extra_metadata=None)
        private_key_hex = private_key.private_bytes_raw().hex()
        return root_did, private_key_hex

    # ---------- 创建机构 ----------
    @staticmethod
    def create_organization(issuer_did: str, issuer_private_key_hex: str,
                            org_type: str, metadata: dict,
                            frontend_perms: List[str], api_perms: List[str],
                            valid_days: int = 365) -> dict:
        root_doc = DIDDocumentDAO.find_by_did(issuer_did)
        if not root_doc or root_doc.did_type != 'root':
            raise PermissionError("只有根DID可以创建机构")
        org_private_key = ed25519.Ed25519PrivateKey.generate()
        org_public_key = org_private_key.public_key()
        org_did = f"did:ibms:{org_type}:{uuid.uuid4()}"
        DIDDocumentDAO.create(did=org_did, did_type=org_type,
                              public_key=org_public_key.public_bytes_raw().hex(),
                              issuer_did=issuer_did, extra_metadata=metadata)
        vc_id = str(uuid.uuid4())
        valid_from = datetime.utcnow()
        valid_until = valid_from + timedelta(days=valid_days)
        vc_json = DIDService._build_vc(vc_id, issuer_did, org_did,
                                       frontend_perms, api_perms,
                                       valid_from, valid_until)
        root_private_key = ed25519.Ed25519PrivateKey.from_private_bytes(bytes.fromhex(issuer_private_key_hex))
        signature = root_private_key.sign(json.dumps(vc_json, sort_keys=True).encode())
        vc_json['proof'] = {'signature': signature.hex()}
        VCCredentialDAO.create(vc_id=vc_id, issuer_did=issuer_did, subject_did=org_did,
                               frontend_perms=frontend_perms, api_perms=api_perms,
                               valid_from=valid_from, valid_until=valid_until, vc_json=vc_json)
        return {
            'did': org_did,
            'private_key': org_private_key.private_bytes_raw().hex(),
            'vc_id': vc_id
        }

    # ---------- 创建员工 ----------
    @staticmethod
    def create_employee(issuer_did: str, issuer_private_key_hex: str,
                        employee_metadata: dict,
                        frontend_perms: List[str], api_perms: List[str],
                        valid_days: int = 180) -> dict:
        issuer_vc = VCCredentialDAO.find_valid_by_subject(issuer_did)
        if not issuer_vc:
            raise PermissionError("签发者没有有效的权限凭证")
        if not set(frontend_perms).issubset(set(issuer_vc.frontend_permissions)):
            raise PermissionError("请求的前端权限超出签发者权限范围")
        if not set(api_perms).issubset(set(issuer_vc.api_permissions)):
            raise PermissionError("请求的API权限超出签发者权限范围")
        emp_private_key = ed25519.Ed25519PrivateKey.generate()
        emp_public_key = emp_private_key.public_key()
        emp_did = f"did:ibms:employee:{uuid.uuid4()}"
        # 修正：直接传入 employee_metadata 字典
        DIDDocumentDAO.create(did=emp_did, did_type='employee',
                              public_key=emp_public_key.public_bytes_raw().hex(),
                              issuer_did=issuer_did, extra_metadata=employee_metadata)
        vc_id = str(uuid.uuid4())
        valid_from = datetime.utcnow()
        valid_until = valid_from + timedelta(days=valid_days)
        vc_json = DIDService._build_vc(vc_id, issuer_did, emp_did,
                                       frontend_perms, api_perms,
                                       valid_from, valid_until)
        issuer_private_key = ed25519.Ed25519PrivateKey.from_private_bytes(bytes.fromhex(issuer_private_key_hex))
        signature = issuer_private_key.sign(json.dumps(vc_json, sort_keys=True).encode())
        vc_json['proof'] = {'signature': signature.hex()}
        VCCredentialDAO.create(vc_id=vc_id, issuer_did=issuer_did, subject_did=emp_did,
                               frontend_perms=frontend_perms, api_perms=api_perms,
                               valid_from=valid_from, valid_until=valid_until, vc_json=vc_json)
        return {
            'did': emp_did,
            'private_key': emp_private_key.private_bytes_raw().hex(),
            'vc_id': vc_id
        }

    # ---------- 登录 ----------
    # ---------- 登录 ----------
    @staticmethod
    def login(login_data: dict) -> Optional[str]:
        """
        支持两种登录方式：
        1. 传统 Challenge 模式（兼容旧客户端）:
            {
                "did": "did:ibms:...",
                "challenge": "a1b2c3...",
                "signature": "hex_signature"
            }
        2. VP 模式（新标准）:
            {
                "presentation": { ... }  # VerifiablePresentation 对象
            }
        """
        from src.utils.vp_util import verify_vp  # 假设你已创建 vp_util.py

        holder_did = None
        vc = None

        # ========== 判断登录模式 ==========
        if 'presentation' in login_data:
            # --- 新：VP 模式 ---
            vp = login_data['presentation']
            is_valid, holder_did, vc_id = verify_vp(vp)
            if not is_valid:
                return None

            # 从数据库查找 VC（使用 vc_id）
            vc = VCCredentialDAO.find_by_id(vc_id)
            if not vc:
                return None
            if vc.subject_did != holder_did:
                return None
            if datetime.utcnow() > vc.valid_until:
                return None

        else:
            # --- 旧：Challenge 模式（完全保留原逻辑）---
            did = login_data.get('did')
            challenge = login_data.get('challenge')
            signature_hex = login_data.get('signature')

            if not did or not challenge or not signature_hex:
                return None

            # 1. 验证挑战码
            if not DIDService.verify_challenge(did, challenge):
                return None
            # 2. 验证签名
            doc = DIDDocumentDAO.find_by_did(did)
            if not doc:
                return None
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(doc.public_key))
            try:
                public_key.verify(bytes.fromhex(signature_hex), challenge.encode())
            except Exception:
                return None
            # 3. 获取有效 VC
            vc = VCCredentialDAO.find_valid_by_subject(did)
            if not vc:
                return None
            holder_did = did

        # ========== 通用：生成 JWT ==========
        payload = {
            'sub': holder_did,
            'frontend_perms': vc.frontend_permissions,
            'api_perms': vc.api_permissions,
            'exp': datetime.utcnow() + timedelta(hours=8)
        }
        jwt_token = create_jwt(payload)
        return jwt_token
    # @staticmethod
    # def login(did: str, signature_hex: str, challenge: str) -> Optional[str]:
    #     # 1. 验证挑战码
    #     if not DIDService.verify_challenge(did, challenge):
    #         return None
    #     # 2. 验证签名
    #     doc = DIDDocumentDAO.find_by_did(did)
    #     if not doc:
    #         return None
    #     public_key = ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(doc.public_key))
    #     try:
    #         public_key.verify(bytes.fromhex(signature_hex), challenge.encode())
    #     except:
    #         return None
    #     # 3. 获取有效 VC
    #     vc = VCCredentialDAO.find_valid_by_subject(did)
    #     if not vc:
    #         return None
    #     # 4. 生成 JWT
    #     payload = {
    #         'sub': did,
    #         'frontend_perms': vc.frontend_permissions,
    #         'api_perms': vc.api_permissions,
    #         'exp': datetime.utcnow() + timedelta(hours=8)
    #     }
    #     jwt_token = create_jwt(payload)
    #     return jwt_token

    # ---------- 撤销凭证 ----------
    @staticmethod
    def revoke_employee(issuer_did: str, issuer_private_key_hex: str, employee_did: str) -> bool:
        doc = DIDDocumentDAO.find_by_did(issuer_did)
        if not doc:
            return False
        emp_doc = DIDDocumentDAO.find_by_did(employee_did)
        if not emp_doc or emp_doc.issuer_did != issuer_did:
            return False
        updated = VCCredentialDAO.revoke_by_subject(employee_did, issuer_did)
        return updated > 0

    # ---------- VC 构建 ----------
    @staticmethod
    def _build_vc(vc_id, issuer, subject, frontend_perms, api_perms, valid_from, valid_until):
        return {
            '@context': ['https://www.w3.org/2018/credentials/v1'],
            'id': f'urn:uuid:{vc_id}',
            'type': ['VerifiableCredential', 'IBMSRoleCredential'],
            'issuer': issuer,
            'issuanceDate': valid_from.isoformat() + 'Z',
            'expirationDate': valid_until.isoformat() + 'Z',
            'credentialSubject': {
                'id': subject,
                'frontend_permissions': frontend_perms,
                'api_permissions': api_perms
            }
        }

    @staticmethod
    def update_employee(
            issuer_did, issuer_private_key, subject_did,
            metadata, frontend_perms, api_perms, valid_days
    ):
        print("进入到了update_employee的service方法里面了")

        # ====== 1. 权限校验（参考 create_employee）======
        issuer_vc = VCCredentialDAO.find_valid_by_subject(issuer_did)
        if not issuer_vc:
            raise PermissionError("签发者没有有效的权限凭证")
        if not set(frontend_perms).issubset(set(issuer_vc.frontend_permissions)):
            raise PermissionError("请求的前端权限超出签发者权限范围")
        if not set(api_perms).issubset(set(issuer_vc.api_permissions)):
            raise PermissionError("请求的API权限超出签发者权限范围")

        # ====== 2. 构建标准 VC（复用 _build_vc）======
        now = datetime.utcnow()
        new_vc_id = str(uuid.uuid4())  # 先生成 ID
        vc_data = DIDService._build_vc(
            vc_id=new_vc_id,
            issuer=issuer_did,
            subject=subject_did,
            frontend_perms=frontend_perms,
            api_perms=api_perms,
            valid_from=now,
            valid_until=now + timedelta(days=valid_days)
        )

        # ====== 3. 签名（对 vc_data 整体签名）======
        issuer_pk = ed25519.Ed25519PrivateKey.from_private_bytes(
            bytes.fromhex(issuer_private_key)
        )
        # 注意：签名的是 vc_data 的 JSON 字符串（和 create_employee 一致）
        message = json.dumps(vc_data, sort_keys=True, separators=(',', ':')).encode()
        signature = issuer_pk.sign(message)
        vc_data['proof'] = {'signature': signature.hex()}

        # ====== 4. 调用 DAO（传入标准 vc_data）======
        new_vc_id_full = EmployeeDAO.update_employee_credential(
            subject_did=subject_did,
            new_metadata=metadata,
            new_frontend_perms=frontend_perms,
            new_api_perms=api_perms,
            issuer_did=issuer_did,
            valid_days=valid_days,
            vc_json=vc_data  # ← 传入标准 W3C VC 对象
        )

        return new_vc_id_full