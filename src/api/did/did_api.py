# src/api/did/did_api.py
from flask import request
from src.api import api_bp
from src.services.did.did_service import DIDService
from src.models.response import Result
from src.utils.jwt_util import jwt_required, get_current_did  # 待实现
from src.dao.did_dao import VCCredentialDAO, DIDDocumentDAO   # 添加 DIDDocumentDAO

"""
    初始化根DID
    ---
    功能描述:
        生成根DID和对应的私钥，并存入数据库。根DID是系统信任锚点，用于签发机构DID。
    请求方法: POST
    请求体: 无
    返回示例:
        {
            "code": 200,
            "message": "success",
            "data": {
                "did": "did:ibms:root:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
                "private_key": "hex_encoded_private_key"
            }
        }
    """
@api_bp.route('/did/init', methods=['POST'])
def init_root():
    did, private_key = DIDService.init_root_did()
    return Result.success(data={'did': did, 'private_key': private_key})

"""
    创建机构DID及对应的可验证凭证(VC)
    ---
    功能描述:
        由根DID签发一个新的机构DID，生成机构公私钥对，并签发包含权限的VC。
    请求方法: POST
    请求体 JSON:
        {
            "issuer_did": "根DID",
            "issuer_private_key": "根DID私钥(十六进制)",
            "org_type": "机构类型(如: company, school, government)",
            "metadata": { ... },                 // 可选，机构元数据
            "frontend_perms": ["perm1", "perm2"], // 前端权限列表
            "api_perms": ["api:read", "api:write"], // API权限列表
            "valid_days": 365                     // 可选，VC有效天数，默认365
        }
    返回示例:
        {
            "code": 200,
            "message": "success",
            "data": {
                "did": "did:ibms:company:xxxx",
                "private_key": "hex_encoded_org_private_key",
                "vc_id": "urn:uuid:xxxx"
            }
        }
    """
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

"""
    创建员工DID及对应的可验证凭证(VC)
    ---
    功能描述:
        由机构DID签发员工DID，生成员工公私钥对，并签发包含权限的VC。
        签发者必须持有有效的VC，且请求的权限不能超出签发者自身权限范围。
    请求方法: POST
    请求体 JSON:
        {
            "issuer_did": "机构DID",
            "issuer_private_key": "机构私钥(十六进制)",
            "metadata": {                         // 员工个人信息，如 name, phone, position
                "name": "张三",
                "phone": "13800138000",
                "position": "工程师"
            },
            "frontend_perms": ["dashboard:view"],
            "api_perms": ["employee:read"],
            "valid_days": 180                     // 可选，默认180天
        }
    返回示例:
        {
            "code": 200,
            "message": "success",
            "data": {
                "did": "did:ibms:employee:xxxx",
                "private_key": "hex_encoded_emp_private_key",
                "vc_id": "urn:uuid:xxxx"
            }
        }
    """
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

"""
    用户登录
    ---
    功能描述:
        支持两种登录验证方式：
        1. Challenge-Response 模式（传统）：
            - 客户端先调用 /did/challenge?did=xxx 获取挑战码
            - 使用DID私钥对挑战码签名，提交 did, challenge, signature
        2. Verifiable Presentation (VP) 模式（推荐）：
            - 客户端构造 VP 对象直接提交 presentation 字段

        验证通过后返回 JWT Token，后续请求需在 Header 中携带 Authorization: Bearer <token>。
    请求方法: POST
    请求体 JSON (两种格式):
        # 格式一: Challenge 模式
        {
            "did": "did:ibms:employee:xxxx",
            "challenge": "a1b2c3...",
            "signature": "hex_signature_of_challenge"
        }
        # 格式二: VP 模式
        {
            "presentation": { ... }   // VerifiablePresentation 对象
        }
    返回:
        成功: {"token": "jwt_token_string"}
        失败: {"error": "Login failed"}, 401
    """

@api_bp.route('/did/login', methods=['POST'])
def login_route():
    data = request.get_json()
    token = DIDService.login(data)  # 传整个 JSON body
    if token:
        return {"token": token}
    else:
        return {"error": "Login failed"}, 401


"""
    撤销员工DID的有效凭证
    ---
    功能描述:
        由签发机构撤销指定员工的VC，使其凭证失效。
    请求方法: POST
    请求体 JSON:
        {
            "issuer_did": "签发机构DID",
            "issuer_private_key": "签发机构私钥(十六进制)",
            "employee_did": "待撤销的员工DID"
        }
    返回示例:
        {
            "code": 200,
            "message": "success",
            "data": {
                "success": true
            }
        }
    """
@api_bp.route('/did/revoke', methods=['POST'])
def revoke():
    data = request.json
    success = DIDService.revoke_employee(data['issuer_did'], data['issuer_private_key'], data['employee_did'])
    return Result.success(data={'success': success})
"""
    获取当前登录用户的信息
    ---
    功能描述:
        通过 JWT 解析当前用户 DID，返回其 DID、权限列表及个人信息。
    请求头:
        Authorization: Bearer <jwt_token>
    返回示例:
        {
            "code": 200,
            "message": "success",
            "data": {
                "did": "did:ibms:employee:xxxx",
                "frontend_perms": ["dashboard:view"],
                "api_perms": ["employee:read"],
                "name": "张三",
                "phone": "13800138000",
                "position": "工程师"
            }
        }
    """

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
    extra_metadata = doc.extra_metadata if doc else {}

    return Result.success(data={
        'did': did,
        'frontend_perms': vc.frontend_permissions or [],
        'api_perms': vc.api_permissions or [],
        'metadata': extra_metadata  # 完整元数据
    })

"""
    获取登录挑战码 (Challenge)
    ---
    功能描述:
        为指定 DID 生成一次性随机挑战码，有效期5分钟，用于后续的 Challenge-Response 登录。
    请求参数:
        did (query string): 用户 DID
    返回示例:
        {
            "code": 200,
            "message": "success",
            "data": {
                "challenge": "a1b2c3d4e5f6..."
            }
        }
    错误:
        若 DID 不存在或参数缺失返回错误信息。
    """
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


"""
    更新员工凭证及个人信息
    ---
    功能描述:
        由签发机构更新指定员工的权限和元数据，生成新的 VC（旧 VC 被撤销）。
    请求方法: POST
    请求体 JSON:
        {
            "issuer_did": "签发机构DID",
            "issuer_private_key": "签发机构私钥(十六进制)",
            "subject_did": "员工DID",
            "metadata": { ... },                 // 更新的元数据
            "frontend_perms": ["new_perm"],
            "api_perms": ["new_api:read"],
            "valid_days": 180                    // 可选，新VC有效天数
        }
    返回示例:
        {
            "code": 200,
            "message": "success",
            "data": {
                "new_vc_id": "urn:uuid:xxxx"
            }
        }
    """
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

"""
    获取指定DID签发的所有可验证凭证(VC)
    ---
    功能描述:
        查询某个 DID（通常为机构或根）作为签发者时签发过的所有 VC 记录。
        权限控制：当前登录用户 DID 必须与查询的 DID 相同，或者是根 DID。
    请求方法: GET
    请求路径参数:
        did (string): 目标 DID
    请求头:
        Authorization: Bearer <jwt_token>
    返回示例:
        {
            "code": 200,
            "message": "success",
            "data": {
                "issuer_did": "did:ibms:company:xxxx",
                "total": 5,
                "vcs": [
                    {
                        "vc_id": "urn:uuid:xxxx",
                        "subject_did": "did:ibms:employee:yyyy",
                        "issuance_date": "2025-01-01T00:00:00Z",
                        "expiration_date": "2025-12-31T23:59:59Z",
                        "frontend_perms": ["dashboard:view"],
                        "api_perms": ["employee:read"],
                        "is_revoked": false,
                        "vc_json": { ... }
                    },
                    ...
                ]
            }
        }
    错误:
        401: 未授权或无权访问
        404: DID 不存在
    """
@api_bp.route('/did/<string:did>/issued-vcs', methods=['GET'])
@jwt_required
def list_issued_vcs(did):

    current_did = get_current_did()

    # 检查目标 DID 是否存在
    target_doc = DIDDocumentDAO.find_by_did(did)
    if not target_doc:
        return Result.error(message="DID not found", status_code=404)

    # 获取当前用户 DID 类型，用于权限判断
    current_doc = DIDDocumentDAO.find_by_did(current_did)
    if current_doc.did_type != 'root' and current_did != did:
        return Result.error(message="Permission denied: you can only view your own issued VCs", status_code=401)

    # 获取该 DID 作为签发者的所有 VC（包括已撤销）
    vc_list = VCCredentialDAO.find_by_issuer(did)

    # 格式化输出
    vcs_data = []
    for vc in vc_list:
        # 查询被签发者的 DIDDocument，获取 extra_metadata
        subject_doc = DIDDocumentDAO.find_by_did(vc.subject_did)
        subject_metadata = subject_doc.extra_metadata if subject_doc else {}

        vcs_data.append({
            'vc_id': vc.vc_id,
            'subject_did': vc.subject_did,
            'subject_info': subject_metadata,  # 直接放入完整 extra_metadata
            'issuance_date': vc.valid_from.isoformat() + 'Z' if vc.valid_from else None,
            'expiration_date': vc.valid_until.isoformat() + 'Z' if vc.valid_until else None,
            'frontend_perms': vc.frontend_permissions,
            'api_perms': vc.api_permissions,
            'is_revoked': vc.revoked,
            'vc_json': vc.vc_json
        })

    return Result.success(data={
        'issuer_did': did,
        'total': len(vcs_data),
        'vcs': vcs_data
    })



# src/api/did/did_api.py
"""
    使用 DID 和私钥签名查询下属列表（无需 JWT Token）
    ---
    功能描述:
        通过 DID 和对应私钥的签名验证身份，返回该 DID 签发的所有下属 DID 列表。
        调用前建议先获取挑战码，再用私钥签名。
    请求方法: POST
    请求体 JSON:
        {
            "did": "did:ibms:root:xxxx",
            "signature": "hex_signature_of_challenge",
            "challenge": "optional_challenge_string"   // 可选，若不提供则使用服务端生成的临时挑战
        }
    返回示例:
        {
            "code": 200,
            "data": {
                "issuer_did": "did:ibms:root:xxxx",
                "total": 2,
                "subordinates": [
                    {
                        "did": "did:ibms:property:yyy",
                        "did_type": "property",
                        "metadata": { ... },
                        "created_at": "2026-04-13T07:39:10Z"
                    },
                    ...
                ]
            }
        }
    """
@api_bp.route('/did/subordinates', methods=['POST'])
def get_subordinates():

    data = request.get_json()
    did = data.get('did')
    signature = data.get('signature')
    challenge = data.get('challenge')

    if not did or not signature:
        return Result.error("Missing did or signature")

    try:
        result = DIDService.get_subordinates(did, signature, challenge)
        return Result.success(data=result)
    except ValueError as e:
        return Result.error(str(e), status_code=404)
    except PermissionError as e:
        return Result.error(str(e), status_code=401)

"""
    统一创建实体 DID 及 VC（支持所有类型）
    ---
    请求体 JSON:
        {
            "issuer_did": "签发者DID",
            "issuer_private_key": "签发者私钥(hex)",
            "did_type": "property | employee | device | area | client | temporary",
            "metadata": { ... },
            "frontend_perms": [...],
            "api_perms": [...],
            "valid_days": 365
        }
    返回:
        { "code":200, "data":{ "did":"...", "private_key":"...", "vc_id":"..." } }
    """
@api_bp.route('/did/entity', methods=['POST'])
def create_entity():
    data = request.json
    required_fields = ['issuer_did', 'issuer_private_key', 'did_type']
    if not all(k in data for k in required_fields):
        return Result.error(code=400, message="缺少必要参数")

    did_type = data['did_type']
    allowed_types = ['property', 'employee', 'device', 'area', 'client', 'temporary']
    if did_type not in allowed_types:
        return Result.error(code=400, message=f"did_type 必须为 {allowed_types} 之一")

    try:
        result = DIDService.create_entity(
            issuer_did=data['issuer_did'],
            issuer_private_key_hex=data['issuer_private_key'],
            did_type=did_type,
            metadata=data.get('metadata', {}),
            frontend_perms=data.get('frontend_perms', []),
            api_perms=data.get('api_perms', []),
            valid_days=data.get('valid_days', 365)
        )
        return Result.success(data=result)
    except PermissionError as e:
        return Result.error(code=403, message=str(e))
    except Exception as e:
        return Result.error(code=500, message=str(e))