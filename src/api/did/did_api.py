# src/api/did/did_api.py
from flask import request, jsonify
from src.api import api_bp
from src.services.did_service import DIDService
from src.models.response import Result
from src.utils.jwt_util import jwt_required, get_current_did  # 待实现
from src.dao.did_dao import VCCredentialDAO, DIDDocumentDAO   # 添加 DIDDocumentDAO

@api_bp.route('/did/init', methods=['POST'])
def init_root():
    did, private_key = DIDService.init_root_did()
    return Result.success(data={'did': did, 'private_key': private_key})

@api_bp.route('/did/organization', methods=['POST'])
def create_organization():
    data = request.json
    result = DIDService.create_organization(
        issuer_did=data['issuer_did'],
        issuer_private_key_hex=data['issuer_private_key'],
        org_type=data['org_type'],
        metadata=data.get('metadata', {}),
        frontend_perms=data.get('frontend_perms', []),
        api_perms=data.get('api_perms', []),
        valid_days=data.get('valid_days', 365)
    )
    return Result.success(data=result)

@api_bp.route('/did/employee', methods=['POST'])
def create_employee():
    data = request.json
    result = DIDService.create_employee(
        issuer_did=data['issuer_did'],
        issuer_private_key_hex=data['issuer_private_key'],
        employee_metadata=data.get('metadata', {}),
        # employee_name=data['employee_name'],
        frontend_perms=data.get('frontend_perms', []),
        api_perms=data.get('api_perms', []),
        valid_days=data.get('valid_days', 180)
    )
    return Result.success(data=result)

# @api_bp.route('/did/login', methods=['POST'])
# def login():
#     data = request.json
#     token = DIDService.login(data['did'], data['signature'], data['challenge'])
#     if token:
#         return Result.success(data={'access_token': token})
#     else:
#         return Result.error(message="Invalid credentials")

@api_bp.route('/did/login', methods=['POST'])
def login_route():
    data = request.get_json()
    token = DIDService.login(data)  # 传整个 JSON body
    if token:
        return {"token": token}
    else:
        return {"error": "Login failed"}, 401



@api_bp.route('/did/revoke', methods=['POST'])
def revoke():
    data = request.json
    success = DIDService.revoke_employee(data['issuer_did'], data['issuer_private_key'], data['employee_did'])
    return Result.success(data={'success': success})

@api_bp.route('/did/me', methods=['GET'])
@jwt_required
def get_me():
    did = get_current_did()

    # 1. 获取权限（从 VC）
    vc = VCCredentialDAO.find_valid_by_subject(did)
    if not vc:
        return Result.error(message="No valid credential")

    # 2. 获取个人信息（从 DIDDocument.extra_metadata）
    doc = DIDDocumentDAO.find_by_did(did)
    metadata = {}
    if doc and doc.extra_metadata:
        # extra_metadata 是 db.JSON，直接是 dict，无需 json.loads
        metadata = {
            'name': doc.extra_metadata.get('name'),
            'phone': doc.extra_metadata.get('phone'),
            'position': doc.extra_metadata.get('position')
        }

    return Result.success(data={
        'did': did,
        'frontend_perms': vc.frontend_permissions or [],
        'api_perms': vc.api_permissions or [],
        **metadata  # 合并到顶层
    })


@api_bp.route('/did/challenge', methods=['GET'])
def get_challenge():
    did = request.args.get('did')
    if not did:
        return Result.error(message="Missing did parameter")
    # 可选：验证 did 是否存在（查数据库）
    doc = DIDDocumentDAO.find_by_did(did)
    if not doc:
        return Result.error(message="DID not found")
    challenge = DIDService.generate_challenge(did)  # 调用 service 方法
    return Result.success(data={"challenge": challenge})


@api_bp.route('/did/employee/update', methods=['POST'])
def update_employee():
    print(">>> 收到更新员工请求")  # ←←← 加这一行
    data = request.get_json()
    print(f">>> [DEBUG] 解析数据: {data}")
    required_fields = ['issuer_did', 'issuer_private_key', 'subject_did', 'metadata']
    if not all(k in data for k in required_fields):
        print("缺少必要参数")
        return Result.error("缺少必要参数")

    try:
        new_vc_id = DIDService.update_employee(
            issuer_did=data['issuer_did'],
            issuer_private_key=data['issuer_private_key'],
            subject_did=data['subject_did'],
            metadata=data['metadata'],
            frontend_perms=data.get('frontend_perms', []),
            api_perms=data.get('api_perms', []),
            valid_days=data.get('valid_days', 180)
        )
        print(f">>> [DEBUG] 成功生成新 VC ID: {new_vc_id}")
        return Result.success({"new_vc_id": new_vc_id})
    except Exception as e:
        print(e)
        return Result.error(str(e))