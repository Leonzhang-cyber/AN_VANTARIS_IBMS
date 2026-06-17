# src/api/did/did_api.py
"""
DID 模块 API 接口
基于 DIDService，完全适配 imbs_entity_type, imbs_permission, imbs_relationship, imbs_users 等表
数据库会话通过 Flask-SQLAlchemy 的 db.session 获取
JWT 鉴权适配 src/utils/jwt_util.py
集成区块链锚定查询与事件检索
"""

from flask import request
from datetime import datetime, timedelta
import json
import hashlib

from web3.datastructures import AttributeDict

from src.api import api_bp
from src.DID import DIDService
from src.common.models.response import Result
from src.common.utils.jwt_util import jwt_required, get_current_did, create_jwt
from src.common.utils.permission_util import require_permission, require_any_permission
from src.common.core.database import db
from src.blockchain import Blockchain
from src.blockchain.config import ANCHOR_CONTRACT_ADDRESS, ANCHOR_CONTRACT_ABI
from hexbytes import HexBytes


def get_did_service() -> DIDService:
    """获取 DIDService 实例，注入数据库会话、区块链客户端和锚定合约"""
    bc = Blockchain()
    contract = bc.client.w3.eth.contract(address=ANCHOR_CONTRACT_ADDRESS, abi=ANCHOR_CONTRACT_ABI)
    return DIDService(db.session, bc, contract)

def _convert_hexbytes(obj):
    """递归将 HexBytes 和 AttributeDict 转换为可 JSON 序列化的类型"""
    if isinstance(obj, HexBytes):
        return obj.hex()
    elif isinstance(obj, AttributeDict):
        # 将 AttributeDict 转换为普通 dict
        return {k: _convert_hexbytes(v) for k, v in dict(obj).items()}
    elif isinstance(obj, dict):
        return {k: _convert_hexbytes(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_hexbytes(i) for i in obj]
    else:
        return obj


# ==================== 1. 系统初始化 ====================
@api_bp.route('/did/system/init', methods=['POST'])
@jwt_required
@require_any_permission(['system:admin', 'did:manage'])
def init_system():
    """
    初始化系统实体（最高权限根实体），幂等操作
    ---
    请求体: 无
    返回:
        {
            "code": 200,
            "data": {
                "did": "did:imbs:system:root:xxxx",
                "public_key": "0x...",
                "private_key": "0x...",   // 仅新建时返回
                "entity_info": {...},
                "is_new": true
            }
        }
    """
    service = get_did_service()
    result = service.init_system_entity()
    return Result.success(data=result)


# ==================== 2. 创建下级实体并签发 VC ====================
@api_bp.route('/did/entity', methods=['POST'])
@jwt_required
@require_permission('did:manage')
def create_entity():
    """
    上级创建下级实体，自动生成密钥对，并签发 VC
    ---
    请求体 JSON:
        {
            "parent_did": "did:imbs:system:root:xxxx",
            "parent_private_key": "0x...",
            "entity_type_code": "property",
            "name": "中海物业",
            "permissions": ["device:read", "device:control"],
            "extra": { "contact": "12345" },
            "credential_type": "PropertyCredential",
            "custom_claims": { "region": "A区" },
            "valid_days": 365
        }
    返回:
        {
            "code": 200,
            "data": {
                "did": "did:imbs:system:root:property:zhonghai:abc123",
                "private_key": "0x...",
                "public_key": "0x...",
                "vc": { ... },
                "entity_info": { ... }
            }
        }
    """
    data = request.get_json()
    required = ['parent_did', 'parent_private_key', 'entity_type_code', 'name', 'permissions']
    if not all(k in data for k in required):
        return Result.error(message="缺少必要参数", code=400)

    expires_at = None
    if 'valid_days' in data:
        expires_at = datetime.utcnow() + timedelta(days=data['valid_days'])

    service = get_did_service()
    try:
        result = service.create_sub_entity_with_vc(
            parent_did=data['parent_did'],
            parent_private_key=data['parent_private_key'],
            entity_type_code=data['entity_type_code'],
            name=data['name'],
            permissions=data['permissions'],
            extra=data.get('extra'),
            credential_type=data.get('credential_type', 'EntityCredential'),
            custom_claims=data.get('custom_claims'),
            expires_at=expires_at
        )
        return Result.success(data=result)
    except Exception as e:
        return Result.error(message=str(e), code=400)


# ==================== 3. 用户生成 VP ====================
@api_bp.route('/did/vp/generate', methods=['POST'])
@jwt_required
@require_permission('did:issue')
def generate_vp():
    """
    用户（持有者）生成可验证表达 VP
    ---
    请求体 JSON:
        {
            "holder_did": "did:imbs:property:zhonghai:abc123",
            "holder_private_key": "0x...",
            "vcs": [ {...}, {...} ],
            "challenge": "nonce_12345",
            "domain": "imbs.example.com"
        }
    返回:
        {
            "code": 200,
            "data": { ... }                        // 完整 VP JSON
        }
    """
    data = request.get_json()
    required = ['holder_did', 'holder_private_key', 'vcs', 'challenge']
    if not all(k in data for k in required):
        return Result.error(message="缺少必要参数", code=400)

    service = get_did_service()
    try:
        vp = service.create_vp_for_holder(
            holder_did=data['holder_did'],
            holder_private_key=data['holder_private_key'],
            vcs=data['vcs'],
            challenge=data['challenge'],
            domain=data.get('domain')
        )
        return Result.success(data=vp)
    except Exception as e:
        return Result.error(message=str(e), code=400)


# ==================== 4. 验证 VP 并提取信息 ====================
@api_bp.route('/did/vp/verify', methods=['POST'])
def verify_vp():
    """
    验证 VP，若通过则返回 VP 中包含的用户信息
    ---
    请求体 JSON:
        {
            "vp": { ... },
            "challenge": "nonce_12345"
        }
    返回:
        {
            "code": 200,
            "data": {
                "valid": true,
                "subject_info": { ... }
            }
        }
    """
    data = request.get_json()
    if 'vp' not in data or 'challenge' not in data:
        return Result.error(message="缺少 vp 或 challenge", code=400)

    service = get_did_service()
    valid, subject_info = service.verify_and_extract_vp(data['vp'], data['challenge'])
    return Result.success(data={'valid': valid, 'subject_info': subject_info})


# ==================== 5. 吊销并重新签发 VC ====================
@api_bp.route('/did/vc/reissue', methods=['POST'])
@jwt_required
@require_permission('did:issue')
def revoke_and_reissue():
    """
    吊销原 VC 并重新签发新 VC（保留 DID）
    ---
    请求体 JSON:
        {
            "issuer_did": "did:imbs:system:root:xxxx",
            "issuer_private_key": "0x...",
            "subject_did": "did:imbs:property:zhonghai:abc123",
            "new_permissions": ["device:read"],
            "new_extra": { "contact": "new" },
            "new_public_key": "0x...",
            "credential_type": "PropertyCredential",
            "custom_claims": {...},
            "old_vc_id": "vc:imbs:xxxx"
        }
    返回:
        {
            "code": 200,
            "data": {
                "did": "...",
                "private_key": "...",
                "public_key": "...",
                "vc": {...},
                "entity_info": {...}
            }
        }
    """
    data = request.get_json()
    required = ['issuer_did', 'issuer_private_key', 'subject_did']
    if not all(k in data for k in required):
        return Result.error(message="缺少必要参数", code=400)

    service = get_did_service()
    try:
        result = service.revoke_and_reissue_vc(
            issuer_did=data['issuer_did'],
            issuer_private_key=data['issuer_private_key'],
            subject_did=data['subject_did'],
            new_permissions=data.get('new_permissions'),
            new_extra=data.get('new_extra'),
            new_public_key=data.get('new_public_key'),
            credential_type=data.get('credential_type', 'EntityCredential'),
            custom_claims=data.get('custom_claims'),
            old_vc_id=data.get('old_vc_id')
        )
        return Result.success(data=result)
    except Exception as e:
        return Result.error(message=str(e), code=400)


# ==================== 6. VC 状态检查与撤销 ====================
@api_bp.route('/did/vc/revoke', methods=['POST'])
@jwt_required
@require_permission('did:revoke')
def revoke_vc():
    """撤销指定的VC（需要提供撤销者 DID）"""
    data = request.get_json()
    vc_id = data.get('vc_id')
    revoked_by_did = data.get('revoked_by_did')
    if not vc_id or not revoked_by_did:
        return Result.error(message="缺少 vc_id 或 revoked_by_did", code=400)

    service = get_did_service()
    success = service.revoke_vc(vc_id, revoked_by_did)
    if success:
        return Result.success(message="VC撤销成功")
    else:
        return Result.error(message="VC撤销失败", code=500)


@api_bp.route('/did/vc/status', methods=['POST'])
def check_vc_status():
    """
    检查 VC 是否有效（签名、过期、撤销、签发者/持有者状态）
    ---
    请求体 JSON:
        {
            "vc": { ... }
        }
    返回:
        {
            "code": 200,
            "data": {
                "valid": true,
                "reason": "有效",
                "subject_info": {...}
            }
        }
    """
    data = request.get_json()
    if 'vc' not in data:
        return Result.error(message="缺少 vc", code=400)

    service = get_did_service()
    status = service.check_vc_status(data['vc'])
    return Result.success(data=status)


# ==================== 7. 挑战码生成 ====================
@api_bp.route('/did/challenge', methods=['GET'])
def generate_challenge():
    """
    生成随机挑战码（用于 VP 防重放或 Challenge-Response 登录）
    ---
    请求参数: length (可选，默认32)
    返回:
        {
            "code": 200,
            "data": {
                "challenge": "a1b2c3..."
            }
        }
    """
    length = request.args.get('length', 32, type=int)
    service = get_did_service()
    challenge = service.generate_challenge(length)
    return Result.success(data={'challenge': challenge})


# ==================== 8. 查询直接下级 ====================
@api_bp.route('/did/subordinates/direct', methods=['GET'])
def get_direct_subordinates():
    """
    查询直接下级列表
    ---
    请求参数: parent_did (query string)
    返回:
        {
            "code": 200,
            "data": [
                { "did": "...", "name": "...", ... },
                ...
            ]
        }
    """
    parent_did = request.args.get('parent_did')
    if not parent_did:
        return Result.error(message="缺少 parent_did", code=400)

    service = get_did_service()
    subs = service.get_direct_subordinates(parent_did)
    return Result.success(data=subs)


# ==================== 9. 查询所有下级树 ====================
@api_bp.route('/did/subordinates/tree', methods=['GET'])
def get_subordinates_tree():
    """
    查询所有下级及下级的下级，返回树形结构
    ---
    请求参数: parent_did (query string)
    返回:
        {
            "code": 200,
            "data": {
                "did": "...",
                "name": "...",
                "children": [ ... ]
            }
        }
    """
    parent_did = request.args.get('parent_did')
    if not parent_did:
        return Result.error(message="缺少 parent_did", code=400)

    service = get_did_service()
    tree = service.get_all_subordinates_tree(parent_did)
    return Result.success(data=tree)


# ==================== 10. 查询所有后代平铺列表 ====================
@api_bp.route('/did/subordinates/flat', methods=['GET'])
def get_subordinates_flat():
    """
    查询所有后代实体（平铺列表）
    ---
    请求参数: parent_did (query string)
    返回:
        {
            "code": 200,
            "data": [
                { "did": "...", "name": "...", ... },
                ...
            ]
        }
    """
    parent_did = request.args.get('parent_did')
    if not parent_did:
        return Result.error(message="缺少 parent_did", code=400)

    service = get_did_service()
    descendants = service.get_all_descendants_flat(parent_did)
    return Result.success(data=descendants)


# ==================== 11. 查询实体信息 ====================
@api_bp.route('/did/entity/<string:did>', methods=['GET'])
def get_entity_info(did):
    """
    根据 DID 查询实体完整信息（含链上锚定哈希和交易哈希）
    ---
    返回:
        {
            "code": 200,
            "data": {
                "did": "...",
                "name": "...",
                "entity_type": "...",
                "public_key": "...",
                "permission_codes": [...],
                "extra": {...},
                "active": 1,
                "created_at": "...",
                "tx_hash": "...",
                "metadata_hash": "..."
            }
        }
    """
    service = get_did_service()
    user = service.get_entity(did)
    if not user:
        return Result.error(message="实体不存在", code=404)
    return Result.success(data=service._build_full_entity_info(user))


# ==================== 12. 登录 ====================
@api_bp.route('/did/login', methods=['POST'])
def login():
    data = request.get_json()
    service = get_did_service()

    # VP 模式
    if 'vp' in data:
        valid, subject_info = service.verify_and_extract_vp(data['vp'], data.get('challenge', ''))
        print("vp valid最后:", valid)
        if valid:
            did = subject_info.get('id')
            user = service.get_entity(did)
            perms = user.permission_codes if user else []
            token = create_jwt({"sub": did, "perms": perms})
            return Result.success(data={'token': token})
        else:
            return Result.error(message="VP 验证失败", code=401)

    # Challenge 模式
    if 'did' in data and 'challenge' in data and 'signature' in data:
        did = data['did']
        user = service.get_entity(did)
        if not user:
            return Result.error(message="DID 不存在", code=404)
        if service._verify_signature(data['challenge'], data['signature'], user.public_key):
            perms = user.permission_codes if user else []
            token = create_jwt({"sub": did, "perms": perms})
            return Result.success(data={'token': token})
        else:
            return Result.error(message="签名验证失败", code=401)

    return Result.error(message="无效的登录请求", code=400)


# ==================== 13. 当前用户信息 ====================
@api_bp.route('/did/me', methods=['GET'])
@jwt_required
def get_current_user_info():
    """
    获取当前登录用户的 DID 信息（需携带 JWT Token）
    """
    current_did = get_current_did()
    service = get_did_service()
    user = service.get_entity(current_did)
    if not user:
        return Result.error(message="用户不存在", code=404)
    return Result.success(data=service._build_full_entity_info(user))


# ==================== 14. 查询链上锚定哈希 ====================
@api_bp.route('/did/chain/entity-hash/<string:did>', methods=['GET'])
def get_entity_chain_hash(did):
    """
    根据 DID 查询链上存储的实体元数据哈希（从合约只读函数获取）
    ---
    返回:
        {
            "code": 200,
            "data": {
                "did": "...",
                "metadata_hash": "0x..."
            }
        }
    """
    service = get_did_service()
    if not service.contract:
        return Result.error(message="区块链合约未配置", code=503)

    try:
        metadata_hash = service.contract.functions.getEntityHash(did).call()
        return Result.success(data={"did": did, "metadata_hash": metadata_hash})
    except Exception as e:
        return Result.error(message=f"查询失败: {str(e)}", code=500)


@api_bp.route('/did/chain/vc-hash/<string:vc_id>', methods=['GET'])
def get_vc_chain_hash(vc_id):
    """
    根据 VC ID 查询链上存储的 VC 哈希（从合约只读函数获取）
    ---
    返回:
        {
            "code": 200,
            "data": {
                "vc_id": "...",
                "vc_hash": "0x..."
            }
        }
    """
    service = get_did_service()
    if not service.contract:
        return Result.error(message="区块链合约未配置", code=503)

    try:
        vc_hash = service.contract.functions.getVCHash(vc_id).call()
        return Result.success(data={"vc_id": vc_id, "vc_hash": vc_hash})
    except Exception as e:
        return Result.error(message=f"查询失败: {str(e)}", code=500)


# ==================== 15. 获取合约事件记录 ====================
def _make_json_serializable(obj):
    """
    递归将任何对象转换为可 JSON 序列化的类型。
    处理 HexBytes, AttributeDict, bytes, int, dict, list 等。
    """
    from hexbytes import HexBytes
    from web3.datastructures import AttributeDict

    if isinstance(obj, HexBytes):
        return obj.hex()
    elif isinstance(obj, bytes):
        return obj.hex()
    elif isinstance(obj, AttributeDict):
        return {k: _make_json_serializable(v) for k, v in dict(obj).items()}
    elif isinstance(obj, dict):
        return {k: _make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_make_json_serializable(i) for i in obj]
    elif isinstance(obj, int):
        return obj
    elif hasattr(obj, 'hex'):  # 例如 HexBytes 的备选
        return obj.hex()
    else:
        # 尝试直接返回，若不可序列化则转为字符串
        try:
            import json
            json.dumps(obj)
            return obj
        except (TypeError, ValueError):
            return str(obj)


@api_bp.route('/did/chain/events', methods=['GET'])
def get_contract_events():
    """
    获取锚定合约的历史事件记录（支持按事件名称过滤）
    """
    service = get_did_service()
    if not service.bc or not service.contract:
        return Result.error(message="区块链服务未配置", code=503)

    event_name = request.args.get('event_name')
    from_block = request.args.get('from_block', 0, type=int)

    try:
        if event_name:
            raw_events = service.bc.events.get_events(
                contract_addr=service.contract.address,
                abi=service.contract.abi,
                event_name=event_name,
                from_block=from_block
            )
            # 将每个事件对象转为普通字典，再序列化
            events = _make_json_serializable([dict(e) for e in raw_events])
            return Result.success(data={"events": events})
        else:
            known_events = ['EntityAnchored', 'VCIssuedAnchored', 'VCRevoked']
            all_events = []
            for ev_name in known_events:
                try:
                    ev_list = service.bc.events.get_events(
                        contract_addr=service.contract.address,
                        abi=service.contract.abi,
                        event_name=ev_name,
                        from_block=from_block
                    )
                    all_events.extend([dict(e) for e in ev_list])
                except Exception:
                    pass

            # 按区块号和日志索引排序
            all_events.sort(key=lambda e: (e.get('blockNumber', 0), e.get('logIndex', 0)))
            events = _make_json_serializable(all_events)
            return Result.success(data={"events": events})

    except Exception as e:
        return Result.error(message=f"查询事件失败: {str(e)}", code=500)



# ==================== 16. 核对实体信息与链上哈希 ====================
# ==================== 16. 核对实体信息与链上哈希 ====================
@api_bp.route('/did/verify/entity/<string:did>', methods=['GET'])
def verify_entity_integrity(did):
    """
    核对实体信息是否与链上锚定哈希一致。
    从数据库提取实体元数据，重新计算 SHA256，与链上哈希比对。
    """
    service = get_did_service()
    user = service.get_entity(did)
    if not user:
        return Result.error(message="实体不存在", code=404)

    # ✅ 构建与注册时完全一致的元数据 JSON
    # 注意：必须与 DIDService._create_entity_internal 中的 metadata 结构严格一致
    extra_without_parent = (user.extra or {}).copy()
    parent_did = extra_without_parent.pop('parent_did', None)  # 提取出 parent_did，并从 extra 中移除

    metadata = {
        "did": user.did,
        "type": user.entity_type.type_code,
        "name": user.name,
        "public_key": user.public_key,
        "permissions": user.permission_codes,      # 注意字段名为 permissions，而非 permission_codes
        "parent_did": parent_did,                  # 使用从 extra 中提取的 parent_did
        "extra": extra_without_parent              # extra 中不再包含 parent_did
    }

    metadata_json = json.dumps(metadata, sort_keys=True, ensure_ascii=False)
    local_hash = "0x" + hashlib.sha256(metadata_json.encode('utf-8')).hexdigest()

    # 从链上获取锚定哈希
    if not service.contract:
        return Result.error(message="区块链合约未配置", code=503)

    try:
        chain_hash = service.contract.functions.getEntityHash(did).call()
    except Exception as e:
        return Result.error(message=f"查询链上哈希失败: {str(e)}", code=500)

    verified = (local_hash.lower() == chain_hash.lower())

    return Result.success(data={
        "did": did,
        "verified": verified,
        "local_hash": local_hash,
        "chain_hash": chain_hash
    })