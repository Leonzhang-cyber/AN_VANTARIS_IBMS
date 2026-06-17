# src/DID/__init__.py
from .did_service import DIDService
from .did_utils import generate_did, validate_did
from .exceptions import DIDAlreadyExistsError, PermissionDeniedError
from .models import EntityType, Permission, User, VCRevocation

__all__ = [
    "DIDService",
    "generate_did",
    "validate_did",
    "DIDAlreadyExistsError",
    "PermissionDeniedError",
    "EntityType",
    "Permission",
    "User",
    "VCRevocation"
]




# src/DID/
# ├── __init__.py
# ├── models.py
# ├── dao.py
# ├── did_utils.py
# ├── did_service.py
# ├── exceptions.py



# ============================================================================
# DID 模块使用说明
# ============================================================================
# """
# DID 模块 - 去中心化身份管理
# ================================
#
# 基于 W3C DID Core 规范实现，提供完整的去中心化身份管理能力。
#
# 一、核心功能
# -----------
# 1. 实体管理：系统初始化、实体注册、层级关系管理
# 2. 可验证凭证(VC)：签发、验证、撤销、重新签发
# 3. 可验证表达(VP)：生成、验证、信息提取
# 4. 权限管理：基于实体层级的权限继承
# 5. 区块链锚定：实体元数据、VC哈希上链存证
#
# 二、模块结构
# -----------
# - models.py      : 6张数据库表模型
# - dao.py         : 数据访问层
# - did_utils.py   : DID生成与校验工具
# - did_service.py : 核心业务服务类
# - exceptions.py  : 自定义异常
#
# 三、数据库表说明
# ---------------
# | 表名                    | 说明                              |
# |------------------------|-----------------------------------|
# | imbs_entity_type       | 实体类型字典                       |
# | imbs_permission        | 权限定义表                         |
# | imbs_relationship      | 实体层级关系表                     |
# | imbs_users             | 统一用户/实体表（存储DID、公钥等） |
# | imbs_vc_anchor         | VC链上锚定记录表                   |
# | imbs_vc_revocation     | VC撤销记录表                       |
#
# 四、实体类型层级
# ---------------
# | 层级 | 类型              | 说明           |
# |------|------------------|----------------|
# | 0    | system           | 系统根实体     |
# | 1    | property/client  | 物业公司/客户  |
# | 2    | bim_region/person| BIM区域/人员   |
# | 3    | device           | 设备           |
#
# 五、快速开始示例
# ---------------
# ```python
# from src.DID import DIDService
# from src.blockchain import Blockchain
# from src.blockchain.config import ANCHOR_CONTRACT_ADDRESS, ANCHOR_CONTRACT_ABI
# from src.common.core.database import db
#
# # 1. 初始化服务
# bc = Blockchain()
# contract = bc.client.w3.eth.contract(
#     address=ANCHOR_CONTRACT_ADDRESS,
#     abi=ANCHOR_CONTRACT_ABI
# )
# did_service = DIDService(db.session, bc, contract)
#
# # 2. 系统初始化（幂等，仅首次执行会生成密钥对）
# result = did_service.init_system_entity()
# system_did = result["did"]
# system_private_key = result["private_key"]  # 请妥善保管
#
# # 3. 创建下级实体
# entity_result = did_service.create_sub_entity_with_vc(
#     parent_did=system_did,
#     parent_private_key=system_private_key,
#     entity_type_code="property",
#     name="中海物业",
#     permissions=["device:read", "device:control"],
#     credential_type="PropertyCredential"
# )
# property_did = entity_result["did"]
# property_private_key = entity_result["private_key"]
# property_vc = entity_result["vc"]
#
# # 4. 实体登录（VP方式）
# challenge = did_service.generate_challenge()
# vp = did_service.create_vp_for_holder(
#     holder_did=property_did,
#     holder_private_key=property_private_key,
#     vcs=[property_vc],
#     challenge=challenge
# )
# # 验证VP
# valid, subject_info = did_service.verify_and_extract_vp(vp, challenge)
#
# # 5. 查询下级实体
# subordinates = did_service.get_direct_subordinates(system_did)
#
# # 6. 检查权限
# has_permission = did_service.check_permission(property_did, "device:control")
#
# # 7. 撤销VC
# did_service.revoke_vc(vc_id=property_vc["id"], revoked_by_did=system_did)
#
# # 8. 重新签发VC（密钥轮换）
# new_result = did_service.revoke_and_reissue_vc(
#     issuer_did=system_did,
#     issuer_private_key=system_private_key,
#     subject_did=property_did,
#     new_permissions=["device:read"],
#     new_public_key=None
# )
#
# 六、API接口列表
#
# 所有API通过 /api/did 前缀访问：
#
# 接口	方法	说明	是否需要JWT
# /system/init	POST	系统初始化（幂等）	否
# /entity	POST	创建下级实体并签发VC	是
# /vp/generate	POST	生成VP	是
# /vp/verify	POST	验证VP并提取信息	否
# /vc/reissue	POST	吊销并重新签发VC	是
# /vc/revoke	POST	撤销VC	是
# /vc/status	POST	VC状态检查	否
# /challenge	GET	获取挑战码	否
# /subordinates/direct	GET	查询直接下级	否
# /subordinates/tree	GET	查询下级树	否
# /subordinates/flat	GET	查询后代平铺列表	否
# /entity/<did>	GET	查询实体信息	否
# /login	POST	登录（Challenge/VP）	否
# /me	GET	获取当前用户信息	是
# /chain/entity-hash/<did>	GET	查询链上实体哈希	否
# /chain/vc-hash/<vc_id>	GET	查询链上VC哈希	否
# /chain/events	GET	获取合约事件	否
# /verify/entity/<did>	GET	核对实体信息与链上哈希	否
# 七、核心方法说明
#
# 方法	说明	返回值
# init_system_entity()	初始化系统根实体（幂等）	dict
# create_sub_entity_with_vc(...)	创建下级实体并签发VC	dict
# issue_vc(...)	签发VC（自动上链锚定）	dict
# verify_vc(vc)	验证VC签名与完整性	bool
# create_vp_for_holder(...)	生成可验证表达VP	dict
# verify_and_extract_vp(vp, challenge)	验证VP并提取用户信息	tuple
# revoke_vc(vc_id, revoked_by_did)	撤销VC（上链）	bool
# revoke_and_reissue_vc(...)	吊销旧VC并签发新VC	dict
# check_vc_status(vc)	检查VC有效性	dict
# generate_challenge(length)	生成随机挑战码	str
# get_entity(did)	获取实体完整信息	User
# get_direct_subordinates(parent_did)	查询直接下级	list
# get_all_subordinates_tree(parent_did)	查询下级树	dict
# get_all_descendants_flat(parent_did)	查询所有后代（平铺）	list
# check_permission(did, perm_code)	递归权限检查	bool
# 八、权限继承规则
#
# 子实体自动继承父实体的所有权限
#
# 创建子实体时，传入的权限不能超出父实体权限范围
#
# 权限检查会递归向上查询，直到找到权限或到达根节点
#
# 系统根实体拥有所有权限（permission_codes = ["*"] 或全部权限编码）
#
# 九、区块链集成说明
#
# 实体注册时自动锚定元数据哈希到合约（调用 anchorEntity）
#
# VC签发时自动锚定VC哈希到合约（调用 anchorVC）
#
# VC撤销时调用合约记录撤销（调用 revokeVC）
#
# 可通过合约查询验证数据完整性（getEntityHash / getVCHash）
#
# 区块链未配置时，锚定操作会跳过（不影响基本功能）
#
# 所有写操作自动触发 MiningScheduler 按需挖矿
# """