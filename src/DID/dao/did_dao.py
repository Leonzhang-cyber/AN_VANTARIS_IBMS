# src/dao/did_dao.py
from typing import Optional, List
from datetime import datetime  # 添加导入
from src.DID.models.did_models import DIDDocument, VCCredential, PermissionDefinition
from src.common.core.database import db


class DIDDocumentDAO:
    @staticmethod
    def create(did: str, did_type: str, public_key: str, issuer_did: Optional[str],
               extra_metadata: dict = None) -> DIDDocument:  # metadata -> extra_metadata
        doc = DIDDocument(did=did, did_type=did_type, public_key=public_key,
                          issuer_did=issuer_did, extra_metadata=extra_metadata)  # 字段名改为 extra_metadata
        db.session.add(doc)
        db.session.commit()
        return doc

    @staticmethod
    def find_by_did(did: str) -> Optional[DIDDocument]:
        return DIDDocument.query.filter_by(did=did).first()

    @staticmethod
    def find_by_issuer(issuer_did: str) -> List[DIDDocument]:
        return DIDDocument.query.filter_by(issuer_did=issuer_did).all()

    @staticmethod
    def find_active_by_subject(subject_did):
        return VCCredential.query.filter_by(
            subject_did=subject_did,
            revoked=False
        ).first()

    @staticmethod
    def update_extra_metadata(did: str, new_metadata: dict) -> Optional[DIDDocument]:
        doc = DIDDocument.query.filter_by(did=did).first()
        if doc:
            doc.extra_metadata = new_metadata
            db.session.commit()
        return doc


class VCCredentialDAO:

    @staticmethod
    def find_by_id(vc_id: str) -> Optional[VCCredential]:
        return VCCredential.query.filter_by(vc_id=vc_id).first()

    @staticmethod
    def find_by_issuer(issuer_did: str) -> List[VCCredential]:
        """
        查询某个 issuer DID 签发的所有 VC（包括有效和已撤销的）
        :param issuer_did: 签发者 DID
        :return: VCCredential 对象列表
        """
        return VCCredential.query.filter_by(issuer_did=issuer_did).all()

    @staticmethod
    def create(vc_id: str, issuer_did: str, subject_did: str,
               frontend_perms: list, api_perms: list,
               valid_from: datetime, valid_until: datetime,
               vc_json: dict) -> VCCredential:
        cred = VCCredential(vc_id=vc_id, issuer_did=issuer_did, subject_did=subject_did,
                            frontend_permissions=frontend_perms, api_permissions=api_perms,
                            valid_from=valid_from, valid_until=valid_until, vc_json=vc_json)
        db.session.add(cred)
        db.session.commit()
        return cred

    @staticmethod
    def find_valid_by_subject(subject_did: str) -> Optional[VCCredential]:
        now = datetime.utcnow()
        return VCCredential.query.filter(
            VCCredential.subject_did == subject_did,
            VCCredential.revoked == False,
            VCCredential.valid_from <= now,
            VCCredential.valid_until > now
        ).order_by(VCCredential.valid_until.desc()).first()

    @staticmethod
    def revoke_by_subject(subject_did: str, issuer_did: str) -> int:
        updated = VCCredential.query.filter(
            VCCredential.subject_did == subject_did,
            VCCredential.revoked == False,
            VCCredential.issuer_did == issuer_did
        ).update({'revoked': True, 'revoked_at': datetime.utcnow()})
        db.session.commit()
        return updated

    @staticmethod
    def revoke_vc(vc_id: str):
        vc = VCCredential.query.filter_by(vc_id=vc_id).first()
        if vc and not vc.revoked:
            vc.revoked = True
            vc.revoked_at = datetime.utcnow()
            db.session.commit()
        return vc

    @staticmethod
    def save(cred: VCCredential) -> VCCredential:
        """通用保存方法（用于创建或更新）"""
        db.session.add(cred)
        db.session.commit()
        return cred


class PermissionDefinitionDAO:
    @staticmethod
    def get_all_frontend_codes() -> List[str]:
        perms = PermissionDefinition.query.filter_by(perm_type='frontend').all()
        return [p.code for p in perms]

    @staticmethod
    def get_all_api_patterns() -> List[dict]:
        perms = PermissionDefinition.query.filter_by(perm_type='api').all()
        return [{'code': p.code, 'method': p.method} for p in perms]


# src/dao/did_dao.py （或新建 EmployeeDAO）

# src/dao/did_dao.py （追加到文件末尾）

class EmployeeDAO:
    @staticmethod
    def update_employee_credential(
        subject_did: str,
        new_metadata: dict,
        new_frontend_perms: list,
        new_api_perms: list,
        issuer_did: str,
        valid_days: int,
        vc_json: dict  # ←←← 由 Service 层传入已签名的完整 VC JSON
    ) -> str:

        print(">>> EmployeeDAO.update_employee_credential 被调用")

        from src.DID.models.did_models import DIDDocument, VCCredential
        from datetime import datetime, timedelta
        import uuid

        # 1. 更新员工元数据
        doc = DIDDocument.query.filter_by(did=subject_did).first()
        if not doc:
            raise ValueError("员工 DID 不存在")
        doc.extra_metadata = new_metadata

        # 2. 撤销当前活跃的 VC
        current_vc = VCCredential.query.filter_by(
            subject_did=subject_did, revoked=False
        ).first()
        if current_vc:
            current_vc.revoked = True
            current_vc.revoked_at = datetime.utcnow()

        # 3. 创建新 VC（使用 Service 提供的完整 vc_json）
        now = datetime.utcnow()
        new_vc_id = f"urn:uuid:{uuid.uuid4()}"
        new_vc = VCCredential(
            vc_id=new_vc_id,
            issuer_did=issuer_did,
            subject_did=subject_did,
            frontend_permissions=new_frontend_perms,
            api_permissions=new_api_perms,
            valid_from=now,
            valid_until=now + timedelta(days=valid_days),
            revoked=False,
            vc_json=vc_json  # ✅ 使用传入的完整 VC
        )
        db.session.add(new_vc)
        db.session.commit()
        return new_vc_id