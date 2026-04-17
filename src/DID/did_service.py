# src/DID/did_service.py
"""
DID 核心服务模块
提供实体注册、VC签发与验证、VP生成与验证、权限管理、层级查询等功能
所有密码学操作均为真实 ECDSA 签名与验证
集成区块链锚定（实体元数据哈希、VC哈希上链）
"""

import json
import hashlib
import secrets
import time
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple

from sqlalchemy.orm import Session
from eth_account import Account
from eth_account.messages import encode_defunct
from web3.auto import w3

from src.blockchain import Blockchain

from .dao import UserDAO, EntityTypeDAO, PermissionDAO, RelationshipDAO, VCRevocationDAO, VCAnchorDAO
from .models import User
from .did_utils import (
    generate_did,
    generate_child_did,
    generate_unique_suffix,
    validate_did,
    get_parent_did
)
from .exceptions import (
    DIDAlreadyExistsError,
    PermissionDeniedError,
    VCInvalidError
)


class DIDService:
    """DID 核心服务类"""

    def __init__(self, session: Session, bc: Optional[Blockchain] = None, contract=None):
        self.session = session
        self.bc = bc
        self.contract = contract
        self.user_dao = UserDAO(session)
        self.type_dao = EntityTypeDAO(session)
        self.perm_dao = PermissionDAO(session)
        self.rel_dao = RelationshipDAO(session)
        self.vc_revocation_dao = VCRevocationDAO(session)
        self.vc_anchor_dao = VCAnchorDAO(session)

    # ==================== 区块链交互封装 ====================
    def _call_contract(self, func_name: str, args: List) -> str:
        """
        调用合约写函数，返回交易哈希。
        若未配置区块链客户端或合约，则返回空字符串。
        """
        if not self.bc or not self.contract:
            return ""
        accounts = self.bc.account.list_accounts()
        if not accounts:
            raise ValueError("无可用区块链账户")
        # 使用第一个有余额的账户（通常为系统账户）作为发送方
        sender = accounts[1] if len(accounts) > 1 else accounts[0]
        result = self.bc.contract.call(
            contract_addr=self.contract.address,
            abi=self.contract.abi,
            func_name=func_name,
            args=args,
            from_addr=sender,
            is_view=False
        )
        return result['tx_hash']

    def revoke_vc(self, vc_id: str, revoked_by_did: str) -> bool:
        """将指定VC ID标记为撤销（同时上链）"""
        tx_hash = self._call_contract('revokeVC', [vc_id])
        if tx_hash:
            self.vc_revocation_dao.revoke(vc_id, revoked_by_did, tx_hash)
            return True
        # 即使链上调用失败，也记录本地撤销（可根据需要调整）
        self.vc_revocation_dao.revoke(vc_id, revoked_by_did, "")
        return True

    def is_vc_revoked(self, vc_id: str) -> bool:
        """检查VC ID是否已被撤销"""
        return self.vc_revocation_dao.is_revoked(vc_id)

    # ==================== 密码学工具 ====================
    def _sign_message(self, private_key: str, message: str) -> str:
        """
        使用私钥对消息进行签名
        :param private_key: 十六进制私钥字符串
        :param message: 待签名的消息字符串
        :return: 签名的十六进制字符串
        """
        msg = encode_defunct(text=message)
        signed = w3.eth.account.sign_message(msg, private_key=private_key)
        return signed.signature.hex()

    def _validate_private_key(self, did: str, private_key: str) -> bool:
        """验证私钥是否与 DID 对应的公钥匹配"""
        user = self.user_dao.get_by_did(did)
        if not user:
            raise ValueError(f"DID {did} 不存在")
        # 通过签名一个随机消息来验证
        test_msg = "key_validation"
        signature = self._sign_message(private_key, test_msg)
        return self._verify_signature(test_msg, signature, user.public_key)

    def _verify_signature(self, message: str, signature: str, expected_address: str) -> bool:
        """
        验证签名是否由指定地址的私钥签署
        :param message: 原始消息字符串
        :param signature: 签名字符串
        :param expected_address: 期望的以太坊地址
        :return: 验证是否通过
        """
        try:
            msg = encode_defunct(text=message)
            recovered = w3.eth.account.recover_message(msg, signature=signature)
            return recovered.lower() == expected_address.lower()
        except Exception:
            return False

    # ==================== 内部辅助方法 ====================
    def _resolve_permission_codes(self, permissions: List[str]) -> List[str]:
        """
        将权限输入统一转换为权限编码列表
        支持传入权限ID（32位十六进制）或权限编码（如 device:read）
        """
        codes = []
        for perm in permissions:
            if len(perm) == 32 and all(c in '0123456789abcdef' for c in perm):
                perm_obj = self.perm_dao.get_by_id(perm)
                if not perm_obj:
                    raise ValueError(f"权限ID {perm} 不存在")
                codes.append(perm_obj.perm_code)
            else:
                codes.append(perm)
        return codes

    def _build_full_entity_info(self, user: User) -> Dict[str, Any]:
        """构建完整的实体信息字典"""
        return {
            "did": user.did,
            "username": user.username,
            "name": user.name,
            "entity_type": user.entity_type.type_code,
            "public_key": user.public_key,
            "permission_codes": user.permission_codes,
            "extra": user.extra,
            "active": user.active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "tx_hash": user.tx_hash,
            "metadata_hash": user.metadata_hash,
        }

    def _create_entity_internal(
        self,
        entity_type_code: str,
        name: str,
        public_key: str,
        permissions: List[str],
        parent_did: Optional[str] = None,
        extra: Optional[Dict] = None
    ) -> User:
        """
        内部创建实体，返回 User 对象，不签发 VC
        """
        entity_type = self.type_dao.get_by_code(entity_type_code)
        if not entity_type:
            raise ValueError(f"实体类型 {entity_type_code} 不存在")

        perm_codes = self._resolve_permission_codes(permissions)

        if parent_did:
            parent = self.user_dao.get_by_did(parent_did)
            if not parent:
                raise ValueError(f"父实体 {parent_did} 不存在")
            parent_perms = set(parent.permission_codes or [])
            if not set(perm_codes).issubset(parent_perms):
                raise PermissionDeniedError("子实体权限不能超出父实体权限范围")

        if parent_did:
            did = generate_child_did(parent_did, entity_type_code, name)
        else:
            did = generate_did(entity_type_code, name)

        if self.user_dao.exists_did(did):
            raise DIDAlreadyExistsError(f"DID {did} 已存在")

        base_username = name
        username = base_username
        counter = 1
        while self.user_dao.exists_username(username):
            username = f"{base_username}_{counter}"
            counter += 1
            if len(username) > 64:
                username = username[:64]

        final_extra = extra.copy() if extra else {}
        if parent_did:
            final_extra['parent_did'] = parent_did

        # ===== 生成元数据哈希并上链 =====
        metadata = {
            "did": did,
            "type": entity_type_code,
            "name": name,
            "public_key": public_key,
            "permissions": perm_codes,
            "parent_did": parent_did,
            "extra": extra or {}
        }
        metadata_json = json.dumps(metadata, sort_keys=True, ensure_ascii=False)
        metadata_hash = "0x" + hashlib.sha256(metadata_json.encode('utf-8')).hexdigest()

        tx_hash = self._call_contract('anchorEntity', [did, metadata_hash])

        user = self.user_dao.create(
            username=username,
            password_hash="",
            did=did,
            entity_type_id=entity_type.id,
            name=name,
            public_key=public_key,
            permission_codes=perm_codes,
            extra=final_extra,
            tx_hash=tx_hash,
            metadata_hash=metadata_hash
        )

        if parent_did:
            self.rel_dao.add_relation(parent_did, did)
        return user

    # ==================== 1. 系统初始化 ====================
    def init_system_entity(self) -> Dict[str, Any]:
        """
        初始化系统实体（最高权限根实体）
        若已存在则返回现有信息，否则创建新的系统实体，并上链锚定。
        """
        system_type = self.type_dao.get_by_code("system")
        if not system_type:
            raise RuntimeError("系统类型 'system' 未在 imbs_entity_type 表中初始化，请执行初始化 SQL。")

        existing_system_users = self.user_dao.get_by_type("system")
        if existing_system_users:
            sys_user = existing_system_users[0]
            return {
                "did": sys_user.did,
                "public_key": sys_user.public_key,
                "private_key": None,
                "entity_info": self._build_full_entity_info(sys_user),
                "is_new": False
            }

        # 创建新的系统实体
        account = Account.create()
        public_key = account.address
        private_key = account.key.hex()

        all_perms = self.perm_dao.get_all()
        all_perm_codes = [p.perm_code for p in all_perms]

        system_did = generate_did("system", "root")

        # ===== 生成元数据哈希并上链（系统实体也上链） =====
        metadata = {
            "did": system_did,
            "type": "system",
            "name": "IMBS系统本体",
            "public_key": public_key,
            "permissions": all_perm_codes,
            "parent_did": None,
            "extra": {"description": "系统最高权限根实体"}
        }
        metadata_json = json.dumps(metadata, sort_keys=True, ensure_ascii=False)
        metadata_hash = "0x" + hashlib.sha256(metadata_json.encode('utf-8')).hexdigest()

        tx_hash = self._call_contract('anchorEntity', [system_did, metadata_hash])

        user = self.user_dao.create(
            username="system",
            password_hash="",
            did=system_did,
            entity_type_id=system_type.id,
            name="IMBS系统本体",
            public_key=public_key,
            permission_codes=all_perm_codes,
            extra={"description": "系统最高权限根实体", "parent_did": None},
            tx_hash=tx_hash,
            metadata_hash=metadata_hash
        )

        return {
            "did": user.did,
            "public_key": public_key,
            "private_key": private_key,
            "entity_info": self._build_full_entity_info(user),
            "is_new": True
        }

    # ==================== 2. 上级创建下级并签发 VC ====================
    def create_sub_entity_with_vc(
        self,
        parent_did: str,
        parent_private_key: str,
        entity_type_code: str,
        name: str,
        permissions: List[str],
        extra: Optional[Dict] = None,
        credential_type: str = "EntityCredential",
        custom_claims: Optional[Dict] = None,
        expires_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        上级创建下级实体，自动生成密钥对，签发 VC，返回完整信息
        """
        if not self._validate_private_key(parent_did, parent_private_key):
            raise ValueError("上级私钥与 DID 不匹配")

        # 1. 生成新实体的密钥对
        account = Account.create()
        public_key = account.address
        private_key = account.key.hex()

        # 2. 创建实体
        user = self._create_entity_internal(
            entity_type_code=entity_type_code,
            name=name,
            public_key=public_key,
            permissions=permissions,
            parent_did=parent_did,
            extra=extra
        )

        # 3. 签发 VC
        vc_result = self.issue_vc(
            issuer_did=parent_did,
            subject_did=user.did,
            credential_type=credential_type,
            issuer_private_key=parent_private_key,
            custom_claims=custom_claims,
            expires_at=expires_at
        )
        vc = vc_result["vc"]

        return {
            "did": user.did,
            "private_key": private_key,
            "public_key": public_key,
            "vc": vc,
            "entity_info": self._build_full_entity_info(user)
        }

    # ==================== VC 签发 ====================
    def issue_vc(
        self,
        issuer_did: str,
        subject_did: str,
        credential_type: str,
        issuer_private_key: str,
        custom_claims: Optional[Dict] = None,
        expires_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        签发可验证凭证 (VC)
        :return: {"vc": dict, "vc_hash": str}
        """
        issuer = self.user_dao.get_by_did(issuer_did)
        if not issuer or issuer.active == 0:
            raise ValueError("签发者无效或已被禁用")
        subject = self.user_dao.get_by_did(subject_did)
        if not subject:
            raise ValueError("持有者不存在")

        auto_claims = {
            "id": subject.did,
            "name": subject.name,
            "entity_type": subject.entity_type.type_code,
            "public_key": subject.public_key,
            "permissions": subject.permission_codes,
            "active": bool(subject.active),
            "created_at": subject.created_at.isoformat() if subject.created_at else None,
        }
        if subject.extra:
            auto_claims["extra"] = subject.extra

        claims = auto_claims.copy()
        if custom_claims:
            claims.update(custom_claims)

        vc_id = f"vc:imbs:{generate_unique_suffix()}"
        vc = {
            "@context": ["https://www.w3.org/2018/credentials/v1"],
            "id": vc_id,
            "type": ["VerifiableCredential", credential_type],
            "issuer": issuer_did,
            "issuanceDate": datetime.utcnow().isoformat() + "Z",
            "credentialSubject": claims
        }
        if expires_at:
            vc["expirationDate"] = expires_at.isoformat() + "Z"

        vc_json = json.dumps(vc, sort_keys=True, ensure_ascii=False)
        vc_hash = "0x" + hashlib.sha256(vc_json.encode('utf-8')).hexdigest()
        signature = self._sign_message(issuer_private_key, vc_hash)

        vc["proof"] = {
            "type": "EcdsaSecp256k1Signature2019",
            "created": datetime.utcnow().isoformat() + "Z",
            "proofPurpose": "assertionMethod",
            "verificationMethod": f"{issuer_did}#keys-1",
            "signatureValue": signature
        }

        # ===== 链上锚定 VC =====
        tx_hash = self._call_contract('anchorVC', [vc_id, vc_hash, issuer_did, subject_did])
        # 存入本地数据库
        self.vc_anchor_dao.create(vc_id, vc_hash, issuer_did, subject_did, tx_hash)

        return {"vc": vc, "vc_hash": vc_hash}

    # ==================== VC 验证 ====================
    def verify_vc(self, vc: Dict) -> bool:
        """验证 VC 的签名与完整性"""
        try:
            vc_copy = {k: v for k, v in vc.items() if k != "proof"}
            vc_json = json.dumps(vc_copy, sort_keys=True, ensure_ascii=False)
            vc_hash = "0x" + hashlib.sha256(vc_json.encode('utf-8')).hexdigest()

            proof = vc.get("proof", {})
            signature = proof.get("signatureValue")
            if not signature:
                return False

            issuer_did = vc.get("issuer")
            issuer = self.user_dao.get_by_did(issuer_did)
            if not issuer or issuer.active == 0:
                return False

            return self._verify_signature(vc_hash, signature, issuer.public_key)
        except Exception:
            return False

    # ==================== VP 生成 ====================
    def create_vp(
        self,
        holder_did: str,
        vcs: List[Dict],
        challenge: str,
        holder_private_key: str,
        domain: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建可验证表达 (VP)
        :return: VP 字典
        """
        holder = self.user_dao.get_by_did(holder_did)
        if not holder or holder.active == 0:
            raise ValueError("持有者无效或已被禁用")

        vp = {
            "@context": ["https://www.w3.org/2018/credentials/v1"],
            "type": "VerifiablePresentation",
            "verifiableCredential": vcs
        }

        vc_hashes = []
        for vc in vcs:
            vc_copy = {k: v for k, v in vc.items() if k != "proof"}
            vc_hashes.append(hashlib.sha256(json.dumps(vc_copy, sort_keys=True).encode()).hexdigest())

        signing_input = {
            "vc_hashes": vc_hashes,
            "challenge": challenge,
            "timestamp": int(time.time())
        }
        if domain:
            signing_input["domain"] = domain

        message = json.dumps(signing_input, sort_keys=True)
        signature = self._sign_message(holder_private_key, message)

        vp["proof"] = {
            "type": "EcdsaSecp256k1Signature2019",
            "created": datetime.utcnow().isoformat() + "Z",
            "proofPurpose": "authentication",
            "verificationMethod": f"{holder_did}#keys-1",
            "challenge": challenge,
            "domain": domain,
            "signatureValue": signature,
            "signingInput": signing_input
        }
        return vp

    def create_vp_for_holder(
        self,
        holder_did: str,
        holder_private_key: str,
        vcs: List[Dict],
        challenge: str,
        domain: Optional[str] = None
    ) -> Dict[str, Any]:
        """用户申请 VP 的便捷方法"""
        return self.create_vp(holder_did, vcs, challenge, holder_private_key, domain)

    # ==================== VP 验证与信息提取 ====================
    def verify_vp(self, vp: Dict, challenge: str) -> bool:
        """验证 VP 的签名与完整性"""
        try:
            vcs = vp.get("verifiableCredential", [])
            for vc in vcs:
                if not self.verify_vc(vc):
                    return False

            proof = vp.get("proof", {})
            if proof.get("challenge") != challenge:
                return False

            signing_input = proof.get("signingInput")
            if not signing_input:
                return False

            message = json.dumps(signing_input, sort_keys=True)
            holder_did = proof["verificationMethod"].split("#")[0]
            holder = self.user_dao.get_by_did(holder_did)
            if not holder or holder.active == 0:
                return False

            return self._verify_signature(message, proof["signatureValue"], holder.public_key)
        except Exception:
            return False

    def verify_and_extract_vp(self, vp: Dict, challenge: str) -> Tuple[bool, Optional[Dict]]:
        """
        验证 VP 并提取其中包含的用户信息
        :return: (验证是否成功, 提取的用户信息字典)
        """
        if not self.verify_vp(vp, challenge):
            return False, None

        vcs = vp.get("verifiableCredential", [])
        if not vcs:
            return False, None

        # 提取第一个 VC 的主体信息
        subject_info = vcs[0].get("credentialSubject", {})
        return True, subject_info

    # ==================== VC 状态检查 ====================
    def check_vc_status(self, vc: Dict) -> Dict[str, Any]:
        """
        检查 VC 是否有效
        :return: {"valid": bool, "reason": str, "subject_info": dict | None}
        """
        if not self.verify_vc(vc):
            return {"valid": False, "reason": "签名验证失败", "subject_info": None}

        # 检查撤销状态
        vc_id = vc.get("id")
        if vc_id and self.is_vc_revoked(vc_id):
            return {"valid": False, "reason": "VC已被撤销", "subject_info": None}

        exp_str = vc.get("expirationDate")
        if exp_str:
            from datetime import timezone
            exp = datetime.fromisoformat(exp_str.replace("Z", "+00:00"))
            now_aware = datetime.now(timezone.utc)
            if now_aware > exp:
                return {"valid": False, "reason": "VC 已过期", "subject_info": None}

        issuer_did = vc.get("issuer")
        subject_did = vc.get("credentialSubject", {}).get("id")
        issuer = self.user_dao.get_by_did(issuer_did)
        subject = self.user_dao.get_by_did(subject_did)

        if not issuer or issuer.active == 0:
            return {"valid": False, "reason": "签发者无效或已被禁用", "subject_info": None}
        if not subject or subject.active == 0:
            return {"valid": False, "reason": "持有者无效或已被禁用", "subject_info": None}

        return {"valid": True, "reason": "有效", "subject_info": vc.get("credentialSubject")}

    # ==================== 吊销并重新签发 VC ====================
    def revoke_and_reissue_vc(
        self,
        issuer_did: str,
        issuer_private_key: str,
        subject_did: str,
        new_permissions: Optional[List[str]] = None,
        new_extra: Optional[Dict] = None,
        new_public_key: Optional[str] = None,
        credential_type: str = "EntityCredential",
        custom_claims: Optional[Dict] = None,
        old_vc_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        吊销原 VC 并重新签发新的 VC（保留 DID）
        """
        user = self.user_dao.get_by_did(subject_did)
        if not user:
            raise ValueError("实体不存在")

        private_key = None
        if new_public_key is None:
            account = Account.create()
            new_public_key = account.address
            private_key = account.key.hex()

        update_data = {"public_key": new_public_key}
        if new_permissions is not None:
            update_data["permission_codes"] = self._resolve_permission_codes(new_permissions)
        if new_extra is not None:
            current_extra = user.extra or {}
            current_extra.update(new_extra)
            update_data["extra"] = current_extra

        self.user_dao.update(subject_did, **update_data)
        user = self.user_dao.get_by_did(subject_did)

        vc_result = self.issue_vc(
            issuer_did=issuer_did,
            subject_did=subject_did,
            credential_type=credential_type,
            issuer_private_key=issuer_private_key,
            custom_claims=custom_claims
        )
        new_vc = vc_result["vc"]

        # 自动吊销旧 VC（如果提供了 old_vc_id）
        if old_vc_id:
            self.revoke_vc(old_vc_id, issuer_did)

        return {
            "did": user.did,
            "private_key": private_key,
            "public_key": user.public_key,
            "vc": new_vc,
            "entity_info": self._build_full_entity_info(user)
        }

    # ==================== 挑战生成 ====================
    def generate_challenge(self, length: int = 32) -> str:
        """生成随机挑战码"""
        return secrets.token_hex(length)

    # ==================== 查询下级 ====================
    def get_direct_subordinates(self, parent_did: str) -> List[Dict]:
        """查询直接下级列表"""
        children_dids = self.rel_dao.get_children(parent_did)
        result = []
        for did in children_dids:
            user = self.user_dao.get_by_did(did)
            if user:
                result.append(self._build_full_entity_info(user))
        return result

    def get_all_subordinates_tree(self, parent_did: str) -> Dict[str, Any]:
        """查询所有下级及下级的下级，返回树形结构"""
        def build_tree(did):
            user = self.user_dao.get_by_did(did)
            if not user:
                return None
            node = self._build_full_entity_info(user)
            children_dids = self.rel_dao.get_children(did)
            node["children"] = []
            for child_did in children_dids:
                child_node = build_tree(child_did)
                if child_node:
                    node["children"].append(child_node)
            return node

        root = build_tree(parent_did)
        return root if root else {}

    def get_all_descendants_flat(self, parent_did: str) -> List[Dict]:
        """查询所有后代（平铺列表）"""
        descendants = self.rel_dao.get_all_descendants(parent_did)
        result = []
        for did in descendants:
            user = self.user_dao.get_by_did(did)
            if user:
                result.append(self._build_full_entity_info(user))
        return result

    # ==================== 权限检查 ====================
    def check_permission(self, did: str, perm_code: str) -> bool:
        """递归检查实体是否拥有指定权限"""
        entity = self.user_dao.get_by_did(did)
        if not entity or entity.active == 0:
            return False
        if entity.permission_codes and perm_code in entity.permission_codes:
            return True
        parent_did = (entity.extra or {}).get('parent_did')
        if parent_did:
            return self.check_permission(parent_did, perm_code)
        return False

    def get_entity(self, did: str) -> Optional[User]:
        return self.user_dao.get_by_did(did)